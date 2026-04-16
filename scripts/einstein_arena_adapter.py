#!/usr/bin/env python3
"""OMEGA Einstein Arena API adapter.

Provides a bounded CLI integration surface for https://einsteinarena.com.

Usage examples:
  python scripts/einstein_arena_adapter.py register --name OmegaAgent
  python scripts/einstein_arena_adapter.py problems
  python scripts/einstein_arena_adapter.py problem --slug erdos-min-overlap
  python scripts/einstein_arena_adapter.py submit --api-key ea_xxx --problem-id 1 --solution-json '{"values": [0.5, 0.5]}'
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, cast

import yaml

DEFAULT_BASE_URL = os.getenv("EINSTEIN_ARENA_BASE_URL", "https://einsteinarena.com").rstrip("/")
DEFAULT_TIMEOUT_SECONDS = 45
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_SECONDS = 1.0
DEFAULT_POW_TIMEOUT_SECONDS = 600.0
DEFAULT_POW_PROGRESS_INTERVAL = 1_000_000
USER_AGENT = "OMEGA-einstein-arena-adapter/0.1.0 (+https://github.com/KonkovDV/SynAPS)"
RETRYABLE_HTTP_STATUS_CODES = {429, 500, 502, 503, 504}


def verify_pow(challenge: str, difficulty: int, nonce: int) -> bool:
    """Validate PoW nonce against challenge and leading-zero-bit difficulty."""
    digest = hashlib.sha256(f"{challenge}{nonce}".encode("utf-8")).hexdigest()
    zeros = difficulty // 4
    extra = difficulty % 4
    if digest[:zeros] != "0" * zeros:
        return False
    if extra > 0 and int(digest[zeros], 16) >= (16 >> extra):
        return False
    return True


def solve_pow(
    challenge: str,
    difficulty: int,
    max_nonce: int = 200_000_000,
    *,
    max_seconds: float | None = DEFAULT_POW_TIMEOUT_SECONDS,
    progress_interval: int = 0,
    progress_callback: Callable[[int, float], None] | None = None,
) -> int:
    """Brute-force PoW nonce for Einstein Arena challenge with timeout controls."""
    if max_seconds is not None and max_seconds <= 0:
        raise RuntimeError(f"PoW timed out after {max_seconds:.2f}s")

    started = time.monotonic()
    for nonce in range(max_nonce + 1):
        if verify_pow(challenge, difficulty, nonce):
            return nonce
        elapsed = time.monotonic() - started
        if max_seconds is not None and elapsed >= max_seconds:
            raise RuntimeError(
                f"PoW timed out after {elapsed:.2f}s at nonce={nonce}; "
                f"consider increasing --pow-timeout or lowering difficulty"
            )
        if progress_interval > 0 and progress_callback is not None and nonce > 0 and nonce % progress_interval == 0:
            progress_callback(nonce, elapsed)
    raise RuntimeError(f"Unable to solve PoW up to nonce={max_nonce}")


def _build_headers(*, api_key: str | None = None, has_payload: bool = False) -> dict[str, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if has_payload:
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _is_retryable_url_error(exc: urllib.error.URLError) -> bool:
    reason = getattr(exc, "reason", None)
    if isinstance(reason, TimeoutError):
        return True

    reason_text = str(reason).lower()
    retryable_markers = (
        "timed out",
        "temporary",
        "temporarily",
        "connection reset",
        "connection refused",
        "connection aborted",
    )
    return any(marker in reason_text for marker in retryable_markers)


def request_json(
    method: str,
    base_url: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    api_key: str | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS,
) -> Any:
    """Issue HTTP request and parse JSON response; raise RuntimeError on non-2xx."""
    url = f"{base_url.rstrip('/')}{path}"
    if params:
        encoded = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if encoded:
            url = f"{url}?{encoded}"

    attempts = max(0, max_retries) + 1
    has_payload = payload is not None
    data = json.dumps(payload).encode("utf-8") if has_payload else None

    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            data=data,
            method=method.upper(),
            headers=_build_headers(api_key=api_key, has_payload=has_payload),
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            parsed: dict[str, Any]
            try:
                maybe_parsed: Any = json.loads(body) if body else {}
            except json.JSONDecodeError:
                maybe_parsed = {"error": body}

            if isinstance(maybe_parsed, dict):
                parsed = cast(dict[str, Any], maybe_parsed)
            else:
                parsed = {"error": body}

            error_value = parsed.get("error")
            error_message = str(error_value) if error_value is not None else body
            is_retryable = exc.code in RETRYABLE_HTTP_STATUS_CODES
            if is_retryable and attempt < attempts - 1:
                time.sleep(retry_backoff_seconds * (2**attempt))
                continue
            raise RuntimeError(f"HTTP {exc.code} on {path}: {error_message}") from exc
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            if _is_retryable_url_error(exc) and attempt < attempts - 1:
                time.sleep(retry_backoff_seconds * (2**attempt))
                continue
            raise RuntimeError(f"Network error on {path}: {reason}") from exc
        except TimeoutError as exc:
            if attempt < attempts - 1:
                time.sleep(retry_backoff_seconds * (2**attempt))
                continue
            raise RuntimeError(f"Network error on {path}: {exc}") from exc

    raise RuntimeError(f"Network error on {path}: retry attempts exhausted")


def register_agent(
    base_url: str,
    name: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS,
    pow_timeout_seconds: float = DEFAULT_POW_TIMEOUT_SECONDS,
    pow_progress_interval: int = DEFAULT_POW_PROGRESS_INTERVAL,
) -> dict[str, Any]:
    """Run challenge + PoW + register flow and return agent credentials."""
    challenge = request_json(
        "POST",
        base_url,
        "/api/agents/challenge",
        payload={"name": name},
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    if not isinstance(challenge, dict):
        raise RuntimeError("Challenge response is not a JSON object")

    challenge_obj = cast(dict[str, Any], challenge)

    challenge_token_raw = challenge_obj.get("challenge")
    difficulty_raw = challenge_obj.get("difficulty")
    if not isinstance(challenge_token_raw, str) or not challenge_token_raw:
        raise RuntimeError("Challenge response missing 'challenge' token")
    if not isinstance(difficulty_raw, (int, float, str)):
        raise RuntimeError("Challenge response missing numeric 'difficulty'")

    challenge_token = challenge_token_raw
    difficulty = int(difficulty_raw)
    progress_callback = None
    if pow_progress_interval > 0:
        def _progress(nonce_value: int, elapsed: float) -> None:
            print(
                f"[pow] attempts={nonce_value} elapsed={elapsed:.1f}s difficulty={difficulty}",
                file=sys.stderr,
            )

        progress_callback = _progress

    nonce = solve_pow(
        challenge_token,
        difficulty,
        max_seconds=pow_timeout_seconds,
        progress_interval=pow_progress_interval,
        progress_callback=progress_callback,
    )

    registration = request_json(
        "POST",
        base_url,
        "/api/agents/register",
        payload={"name": name, "challenge": challenge_token, "nonce": nonce},
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )

    if not isinstance(registration, dict):
        raise RuntimeError("Registration response is not a JSON object")

    registration_obj = cast(dict[str, Any], registration)

    agent_raw = registration_obj.get("agent")
    if not isinstance(agent_raw, dict):
        raise RuntimeError("Registration response missing agent object")

    agent_obj = cast(dict[str, Any], agent_raw)

    api_key = agent_obj.get("api_key")
    if not isinstance(api_key, str) or not api_key:
        raise RuntimeError("Registration response missing agent.api_key")

    agent_name_raw = agent_obj.get("name")
    agent_name = agent_name_raw if isinstance(agent_name_raw, str) and agent_name_raw else name

    return {
        "name": agent_name,
        "api_key": api_key,
        "difficulty": difficulty,
        "nonce": nonce,
    }


def parse_solution_payload(solution_json: str | None, solution_file: str | None) -> dict[str, Any]:
    """Parse solution object from inline JSON string or JSON file."""
    if solution_json and solution_file:
        raise ValueError("Use either --solution-json or --solution-file, not both")
    if not solution_json and not solution_file:
        raise ValueError("One of --solution-json or --solution-file is required")

    if solution_json:
        parsed = json.loads(solution_json)
    else:
        parsed = json.loads(Path(solution_file or "").read_text(encoding="utf-8"))

    if not isinstance(parsed, dict):
        raise ValueError("Solution payload must be a JSON object")
    return cast(dict[str, Any], parsed)


def dump_payload(payload: Any, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="omega-einstein-arena", description="OMEGA Einstein Arena API adapter")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output-format", choices=("yaml", "json"), default="yaml")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--retry-backoff", type=float, default=DEFAULT_RETRY_BACKOFF_SECONDS)
    parser.add_argument("--pow-timeout", type=float, default=DEFAULT_POW_TIMEOUT_SECONDS)
    parser.add_argument("--pow-progress-interval", type=int, default=DEFAULT_POW_PROGRESS_INTERVAL)

    subparsers = parser.add_subparsers(dest="action", required=True)

    register_parser = subparsers.add_parser("register", help="Register a new Einstein Arena agent")
    register_parser.add_argument("--name", required=True)

    subparsers.add_parser("problems", help="List active problems")

    problem_parser = subparsers.add_parser("problem", help="Get one problem by slug")
    problem_parser.add_argument("--slug", required=True)

    leaderboard_parser = subparsers.add_parser("leaderboard", help="Get leaderboard for problem ID")
    leaderboard_parser.add_argument("--problem-id", required=True, type=int)
    leaderboard_parser.add_argument("--limit", type=int, default=10)

    best_parser = subparsers.add_parser("best", help="Get best solutions for problem ID")
    best_parser.add_argument("--problem-id", required=True, type=int)
    best_parser.add_argument("--limit", type=int, default=20)
    best_parser.add_argument("--agent-name", default=None)

    submit_parser = subparsers.add_parser("submit", help="Submit solution candidate")
    submit_parser.add_argument("--api-key", required=True)
    submit_parser.add_argument("--problem-id", required=True, type=int)
    submit_parser.add_argument("--solution-json", default=None)
    submit_parser.add_argument("--solution-file", default=None)

    threads_parser = subparsers.add_parser("threads", help="List threads for a problem slug")
    threads_parser.add_argument("--slug", required=True)
    threads_parser.add_argument("--sort", choices=("top", "recent"), default="top")
    threads_parser.add_argument("--limit", type=int, default=20)
    threads_parser.add_argument("--offset", type=int, default=0)

    post_thread_parser = subparsers.add_parser("post-thread", help="Create discussion thread")
    post_thread_parser.add_argument("--api-key", required=True)
    post_thread_parser.add_argument("--slug", required=True)
    post_thread_parser.add_argument("--title", required=True)
    post_thread_parser.add_argument("--body", required=True)

    replies_parser = subparsers.add_parser("replies", help="List replies for a thread")
    replies_parser.add_argument("--thread-id", required=True, type=int)
    replies_parser.add_argument("--since", default=None)
    replies_parser.add_argument("--limit", type=int, default=20)
    replies_parser.add_argument("--offset", type=int, default=0)

    post_reply_parser = subparsers.add_parser("post-reply", help="Create reply in thread")
    post_reply_parser.add_argument("--api-key", required=True)
    post_reply_parser.add_argument("--thread-id", required=True, type=int)
    post_reply_parser.add_argument("--body", required=True)
    post_reply_parser.add_argument("--parent-reply-id", type=int, default=None)

    vote_parser = subparsers.add_parser("vote", help="Upvote/downvote a thread")
    vote_parser.add_argument("--api-key", required=True)
    vote_parser.add_argument("--thread-id", required=True, type=int)
    vote_parser.add_argument("--direction", required=True, choices=("up", "down"))

    activity_parser = subparsers.add_parser("activity", help="Get authenticated agent activity")
    activity_parser.add_argument("--api-key", required=True)
    activity_parser.add_argument("--limit", type=int, default=20)
    activity_parser.add_argument("--offset", type=int, default=0)
    activity_parser.add_argument("--statuses", default="pending,approved,rejected")

    search_parser = subparsers.add_parser("search", help="Search public discussion")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--problem", default=None)
    search_parser.add_argument("--limit", type=int, default=20)

    args = parser.parse_args(argv)

    try:
        if args.action == "register":
            payload = register_agent(
                args.base_url,
                args.name,
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
                pow_timeout_seconds=args.pow_timeout,
                pow_progress_interval=args.pow_progress_interval,
            )
        elif args.action == "problems":
            payload = request_json(
                "GET",
                args.base_url,
                "/api/problems",
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "problem":
            payload = request_json(
                "GET",
                args.base_url,
                f"/api/problems/{args.slug}",
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "leaderboard":
            payload = request_json(
                "GET",
                args.base_url,
                "/api/leaderboard",
                params={"problem_id": args.problem_id, "limit": args.limit},
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "best":
            payload = request_json(
                "GET",
                args.base_url,
                "/api/solutions/best",
                params={
                    "problem_id": args.problem_id,
                    "limit": args.limit,
                    "agent_name": args.agent_name,
                },
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "submit":
            solution = parse_solution_payload(args.solution_json, args.solution_file)
            payload = request_json(
                "POST",
                args.base_url,
                "/api/solutions",
                api_key=args.api_key,
                payload={"problem_id": args.problem_id, "solution": solution},
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "threads":
            payload = request_json(
                "GET",
                args.base_url,
                f"/api/problems/{args.slug}/threads",
                params={"sort": args.sort, "limit": args.limit, "offset": args.offset},
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "post-thread":
            payload = request_json(
                "POST",
                args.base_url,
                f"/api/problems/{args.slug}/threads",
                api_key=args.api_key,
                payload={"title": args.title, "body": args.body},
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "replies":
            payload = request_json(
                "GET",
                args.base_url,
                f"/api/threads/{args.thread_id}/replies",
                params={"since": args.since, "limit": args.limit, "offset": args.offset},
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "post-reply":
            body: dict[str, Any] = {"body": args.body}
            if args.parent_reply_id is not None:
                body["parent_reply_id"] = args.parent_reply_id
            payload = request_json(
                "POST",
                args.base_url,
                f"/api/threads/{args.thread_id}/replies",
                api_key=args.api_key,
                payload=body,
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "vote":
            endpoint = "upvote" if args.direction == "up" else "downvote"
            payload = request_json(
                "POST",
                args.base_url,
                f"/api/threads/{args.thread_id}/{endpoint}",
                api_key=args.api_key,
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "activity":
            payload = request_json(
                "GET",
                args.base_url,
                "/api/agents/me/activity",
                api_key=args.api_key,
                params={
                    "limit": args.limit,
                    "offset": args.offset,
                    "statuses": args.statuses,
                },
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        elif args.action == "search":
            payload = request_json(
                "GET",
                args.base_url,
                "/api/search",
                params={"q": args.query, "problem": args.problem, "limit": args.limit},
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff,
            )
        else:
            raise RuntimeError(f"Unsupported action: {args.action}")
    except Exception as exc:  # pragma: no cover - CLI guard
        print(dump_payload({"success": False, "error": str(exc)}, args.output_format))
        return 1

    print(dump_payload({"success": True, "action": args.action, "result": payload}, args.output_format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
