#!/usr/bin/env python3
"""OMEGA verifier-guided proof repair loop for Lean 4 files.

This utility implements a bounded self-correction loop:
1) find `sorry` placeholders;
2) generate tactic candidates from a model;
3) patch one `sorry` at a time;
4) verify each candidate using omega-lean check-file semantics;
5) keep only improving patches.

Usage:
  python scripts/proof_repair_loop.py repair proof/Example.lean --model goedel-prover-v2-32b
"""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path
from typing import Any, Callable

import yaml

from lean_adapter import LeanAdapter
from leancop_bridge import (
    build_generation_messages,
    normalize_tactic_candidates,
    request_openai_chat,
)


DEFAULT_BASE_URL = "http://localhost:8000/v1"
DEFAULT_MODEL = "goedel-prover-v2-32b"
DEFAULT_MAX_ITERATIONS = 32
DEFAULT_CANDIDATES = 5
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_TEMPERATURE_SCHEDULE = "0.1,0.2,0.3,0.5"

SORRY_RE = re.compile(r"\bsorry\b")


def count_sorries(source: str) -> int:
    return len(SORRY_RE.findall(source))


def replace_first_sorry(source: str, replacement: str) -> str:
    """Replace first `sorry` occurrence with replacement tactic."""
    if "sorry" not in source:
        return source
    return SORRY_RE.sub(replacement, source, count=1)


def parse_temperature_schedule(raw: str) -> list[float]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        return [0.1]
    parsed = [float(value) for value in values]
    return parsed


def _render_first_sorry_context(source: str, context_lines: int = 8) -> str:
    lines = source.splitlines()
    for idx, line in enumerate(lines):
        if SORRY_RE.search(line):
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + context_lines + 1)
            window = lines[start:end]
            return "\n".join(window)
    return source[-1500:]


def _summarize_diagnostics(result: dict[str, Any]) -> str:
    errors = result.get("errors", [])
    if not errors:
        return "No Lean diagnostics available."
    chunks: list[str] = []
    for item in errors[:5]:
        message = str(item.get("message", "")).strip()
        if message:
            chunks.append(message)
    return "\n".join(chunks) if chunks else "No Lean diagnostics available."


def _check_source(adapter: LeanAdapter, source: str, original_path: Path, timeout_seconds: int) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".lean",
        prefix=f"{original_path.stem}.repair.",
        encoding="utf-8",
        dir=str(original_path.parent),
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        handle.write(source)

    try:
        return adapter.check_file(temp_path, timeout_seconds=timeout_seconds)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _model_generate_candidates(
    goal_context: str,
    diagnostics: str,
    *,
    base_url: str,
    model: str,
    temperature: float,
    max_tokens: int,
    timeout_seconds: int,
    candidates: int,
    api_key: str,
) -> list[str]:
    messages = build_generation_messages(goal_context, "", candidates)
    messages[-1]["content"] = (
        messages[-1]["content"]
        + "\n\nLean diagnostics from previous attempt:\n"
        + diagnostics
    )
    raw = request_openai_chat(
        base_url=base_url,
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        api_key=api_key,
    )
    return normalize_tactic_candidates(raw, max_candidates=candidates)


def run_proof_repair_loop(
    lean_file: Path,
    *,
    model: str,
    base_url: str,
    api_key: str,
    max_iterations: int,
    candidates: int,
    timeout_seconds: int,
    temperature_schedule: list[float],
    in_place: bool,
    adapter: LeanAdapter | None = None,
    candidate_provider: Callable[[str, str, int, float], list[str]] | None = None,
) -> dict[str, Any]:
    """Run bounded verifier-guided self-correction loop for one Lean file."""
    if not lean_file.exists() or not lean_file.is_file():
        raise FileNotFoundError(f"Lean file not found: {lean_file}")

    engine = adapter or LeanAdapter()
    current_source = lean_file.read_text(encoding="utf-8")
    current_sorries = count_sorries(current_source)

    if current_sorries == 0:
        return {
            "success": False,
            "status": "no-sorry-found",
            "iterations": 0,
            "initial_sorries": 0,
            "final_sorries": 0,
            "output_path": str(lean_file),
        }

    history: list[dict[str, Any]] = []
    best_error_count = 10_000

    for iteration in range(max_iterations):
        temp_index = min(iteration, len(temperature_schedule) - 1)
        temp = temperature_schedule[temp_index]

        check_result = _check_source(engine, current_source, lean_file, timeout_seconds)
        error_count = len(check_result.get("errors", []))
        best_error_count = min(best_error_count, error_count)
        current_sorries = count_sorries(current_source)

        if check_result.get("success") and current_sorries == 0:
            output_path = lean_file if in_place else lean_file.with_suffix(".repaired.lean")
            output_path.write_text(current_source, encoding="utf-8")
            return {
                "success": True,
                "status": "verified",
                "iterations": iteration,
                "initial_sorries": count_sorries(lean_file.read_text(encoding="utf-8")),
                "final_sorries": 0,
                "output_path": str(output_path),
                "history": history,
            }

        if current_sorries == 0 and not check_result.get("success"):
            break

        goal_context = _render_first_sorry_context(current_source)
        diagnostics = _summarize_diagnostics(check_result)

        provider = candidate_provider
        if provider is None:
            def provider_fn(ctx: str, diags: str, n: int, temperature_value: float) -> list[str]:
                return _model_generate_candidates(
                    ctx,
                    diags,
                    base_url=base_url,
                    model=model,
                    temperature=temperature_value,
                    max_tokens=256,
                    timeout_seconds=timeout_seconds,
                    candidates=n,
                    api_key=api_key,
                )

            provider = provider_fn

        try:
            options = provider(goal_context, diagnostics, candidates, temp)
        except Exception as exc:  # pragma: no cover - runtime guard
            history.append({"iteration": iteration, "error": str(exc), "status": "candidate-generation-failed"})
            break

        improved = False
        best_source = current_source
        best_tuple = (current_sorries, error_count)

        for tactic in options:
            trial_source = replace_first_sorry(current_source, tactic)
            trial_result = _check_source(engine, trial_source, lean_file, timeout_seconds)
            trial_errors = len(trial_result.get("errors", []))
            trial_sorries = count_sorries(trial_source)
            trial_tuple = (trial_sorries, trial_errors)

            history.append(
                {
                    "iteration": iteration,
                    "tactic": tactic,
                    "sorries": trial_sorries,
                    "errors": trial_errors,
                    "success": bool(trial_result.get("success")),
                }
            )

            if trial_result.get("success") and trial_sorries == 0:
                output_path = lean_file if in_place else lean_file.with_suffix(".repaired.lean")
                output_path.write_text(trial_source, encoding="utf-8")
                return {
                    "success": True,
                    "status": "verified",
                    "iterations": iteration + 1,
                    "initial_sorries": count_sorries(lean_file.read_text(encoding="utf-8")),
                    "final_sorries": 0,
                    "output_path": str(output_path),
                    "history": history,
                }

            if trial_tuple < best_tuple:
                best_source = trial_source
                best_tuple = trial_tuple
                improved = True

        if not improved:
            break

        current_source = best_source

    output_path = lean_file if in_place else lean_file.with_suffix(".repaired.lean")
    output_path.write_text(current_source, encoding="utf-8")
    return {
        "success": False,
        "status": "exhausted",
        "iterations": max_iterations,
        "initial_sorries": count_sorries(lean_file.read_text(encoding="utf-8")),
        "final_sorries": count_sorries(current_source),
        "best_error_count": best_error_count,
        "output_path": str(output_path),
        "history": history,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OMEGA verifier-guided Lean proof repair loop")
    sub = parser.add_subparsers(dest="command", required=True)

    repair = sub.add_parser("repair", help="Run bounded proof repair loop for one Lean file")
    repair.add_argument("lean_file", type=Path)
    repair.add_argument("--model", default=DEFAULT_MODEL)
    repair.add_argument("--base-url", default=DEFAULT_BASE_URL)
    repair.add_argument("--api-key", default="")
    repair.add_argument("--max-iterations", type=int, default=DEFAULT_MAX_ITERATIONS)
    repair.add_argument("--candidates", type=int, default=DEFAULT_CANDIDATES)
    repair.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    repair.add_argument("--temperature-schedule", default=DEFAULT_TEMPERATURE_SCHEDULE)
    repair.add_argument("--in-place", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "repair":
        parser.error(f"Unsupported command: {args.command}")
        return 1

    schedule = parse_temperature_schedule(args.temperature_schedule)
    result = run_proof_repair_loop(
        args.lean_file,
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        max_iterations=args.max_iterations,
        candidates=args.candidates,
        timeout_seconds=args.timeout,
        temperature_schedule=schedule,
        in_place=args.in_place,
    )
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
