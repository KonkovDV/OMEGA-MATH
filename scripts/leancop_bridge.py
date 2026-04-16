#!/usr/bin/env python3
"""LeanCopilot ExternalGenerator bridge for OMEGA.

This server exposes a minimal HTTP API compatible with LeanCopilot's
ExternalGenerator contract (`external_model_api.yaml`) and forwards generation
requests to an OpenAI-compatible endpoint (vLLM, Ollama, LM Studio, etc.).

Usage:
  python scripts/leancop_bridge.py --model goedel-prover-v2-32b --base-url http://localhost:8000/v1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 23337
DEFAULT_BASE_URL = os.environ.get("OMEGA_LEANCOP_BASE_URL", "http://localhost:8000/v1")
DEFAULT_MODEL = os.environ.get("OMEGA_LEANCOP_MODEL", "goedel-prover-v2-32b")
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 256
DEFAULT_CANDIDATES = 5
DEFAULT_TIMEOUT_SECONDS = 60


@dataclass
class BridgeConfig:
    host: str
    port: int
    base_url: str
    model: str
    api_key_env: str
    temperature: float
    max_tokens: int
    candidates: int
    timeout_seconds: int


def build_generation_messages(goal_state: str, target_prefix: str, candidates: int) -> list[dict[str, str]]:
    """Build model messages for tactic generation from a Lean goal state."""
    prefix_note = (
        f"Target prefix constraint: {target_prefix}\nOnly return tactics starting with this prefix."
        if target_prefix
        else "No prefix constraint."
    )
    return [
        {
            "role": "system",
            "content": (
                "You are a Lean 4 tactic generator. Return concise tactic lines only. "
                "Do not include explanations, markdown, or prose."
            ),
        },
        {
            "role": "user",
            "content": (
                "Generate candidate Lean 4 tactics for this goal state.\n"
                f"{prefix_note}\n"
                f"Candidate count target: {candidates}\n"
                "Goal state:\n"
                f"{goal_state}"
            ),
        },
    ]


def request_openai_chat(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout_seconds: int,
    api_key: str,
) -> str:
    """Send one OpenAI-compatible chat completion request and return text output."""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Bridge upstream HTTP {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Bridge upstream network error: {exc.reason}") from exc

    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("Bridge upstream response missing choices")
    first = choices[0]
    message = first.get("message", {}) if isinstance(first, dict) else {}
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str):
        raise RuntimeError("Bridge upstream response missing text content")
    return content


def normalize_tactic_candidates(raw_text: str, *, max_candidates: int, target_prefix: str = "") -> list[str]:
    """Normalize raw model output into unique Lean tactic candidates."""
    candidates: list[str] = []
    seen: set[str] = set()
    for line in raw_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.startswith("```"):
            continue
        cleaned = re.sub(r"^[-*]\s+", "", cleaned)
        cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned)
        cleaned = cleaned.strip("` ")
        if not cleaned:
            continue
        if target_prefix and not cleaned.startswith(target_prefix):
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        candidates.append(cleaned)
        if len(candidates) >= max_candidates:
            break

    if not candidates and target_prefix:
        return [target_prefix]
    if not candidates:
        return ["exact?"]
    return candidates


def generate_tactics(goal_state: str, target_prefix: str, config: BridgeConfig) -> list[dict[str, Any]]:
    """Generate scored tactic candidates for LeanCopilot ExternalGenerator."""
    api_key = os.environ.get(config.api_key_env, "")
    if not api_key and "localhost" not in config.base_url and "127.0.0.1" not in config.base_url:
        raise RuntimeError(
            f"Environment variable {config.api_key_env} is required for non-local base URL {config.base_url}"
        )

    messages = build_generation_messages(goal_state, target_prefix, config.candidates)
    raw = request_openai_chat(
        base_url=config.base_url,
        model=config.model,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        timeout_seconds=config.timeout_seconds,
        api_key=api_key or "local",
    )

    tactics = normalize_tactic_candidates(raw, max_candidates=config.candidates, target_prefix=target_prefix)
    if len(tactics) == 1:
        return [{"output": tactics[0], "score": 1.0}]

    step = 1.0 / max(1, len(tactics) - 1)
    return [{"output": tactic, "score": round(1.0 - (idx * step), 4)} for idx, tactic in enumerate(tactics)]


class BridgeHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_cls: type[BaseHTTPRequestHandler], config: BridgeConfig):
        super().__init__(server_address, handler_cls)
        self.config = config


class BridgeRequestHandler(BaseHTTPRequestHandler):
    server: BridgeHTTPServer

    def _write_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._write_json(200, {"ok": True, "model": self.server.config.model})
            return
        self._write_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/generate":
            self._write_json(404, {"ok": False, "error": "not found"})
            return

        length_header = self.headers.get("Content-Length")
        if not length_header or not length_header.isdigit():
            self._write_json(400, {"ok": False, "error": "Content-Length is required"})
            return

        raw = self.rfile.read(int(length_header))
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._write_json(400, {"ok": False, "error": "invalid JSON"})
            return

        goal_state = str(payload.get("input", "")).strip()
        target_prefix = str(payload.get("prefix", "")).strip()
        if not goal_state:
            self._write_json(400, {"ok": False, "error": "field 'input' is required"})
            return

        try:
            outputs = generate_tactics(goal_state, target_prefix, self.server.config)
        except Exception as exc:  # pragma: no cover - runtime guard
            self._write_json(502, {"ok": False, "error": str(exc)})
            return

        self._write_json(200, {"outputs": outputs})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Keep bridge quiet by default.
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OMEGA LeanCopilot ExternalGenerator bridge")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--candidates", type=int, default=DEFAULT_CANDIDATES)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = BridgeConfig(
        host=args.host,
        port=args.port,
        base_url=args.base_url,
        model=args.model,
        api_key_env=args.api_key_env,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        candidates=args.candidates,
        timeout_seconds=args.timeout,
    )

    server = BridgeHTTPServer((config.host, config.port), BridgeRequestHandler, config)
    print(
        f"OMEGA LeanCop bridge listening on http://{config.host}:{config.port} "
        f"-> {config.base_url.rstrip('/')}/chat/completions ({config.model})"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
