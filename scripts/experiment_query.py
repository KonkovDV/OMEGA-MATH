#!/usr/bin/env python3
"""OMEGA experiment query layer — search and filter experiment ledger entries.

Usage:
  python scripts/experiment_query.py --problem goldbach --verdict positive
  python scripts/experiment_query.py --route proof-first --after 2026-03-01
  python scripts/experiment_query.py --global --verdict inconclusive
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_date(value: str) -> datetime:
    """Parse a date string (YYYY-MM-DD or ISO 8601) into a datetime for comparison."""
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S+00:00", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {value!r}")


def query_ledger(
    ledger: list[dict[str, Any]],
    *,
    problem_id: str | None = None,
    route: str | None = None,
    verdict: str | None = None,
    status: str | None = None,
    agent: str | None = None,
    artifact_type: str | None = None,
    after: str | None = None,
    before: str | None = None,
) -> list[dict[str, Any]]:
    """Filter a ledger (list of run records) by the given criteria.

    All filters are AND-combined. Returns matching entries in original order.
    """
    results: list[dict[str, Any]] = []

    after_dt = _parse_date(after) if after else None
    before_dt = _parse_date(before) if before else None

    for entry in ledger:
        if problem_id is not None and entry.get("problem_id") != problem_id:
            continue
        if route is not None and entry.get("route") != route:
            continue
        if verdict is not None and entry.get("verdict") != verdict:
            continue
        if status is not None and entry.get("status") != status:
            continue
        if agent is not None and entry.get("agent") != agent:
            continue

        if artifact_type is not None:
            entry_artifacts = cast(list[dict[str, Any]], entry.get("artifacts") or [])
            if not any(artifact.get("type") == artifact_type for artifact in entry_artifacts):
                continue

        if after_dt is not None or before_dt is not None:
            started_raw = entry.get("started")
            if not started_raw:
                continue
            try:
                started_dt = _parse_date(str(started_raw))
            except ValueError:
                continue
            if after_dt is not None and started_dt < after_dt:
                continue
            if before_dt is not None and started_dt >= before_dt:
                continue

        results.append(entry)

    return results


def query_global_index(
    repo_root: Path,
    *,
    problem_id: str | None = None,
    verdict: str | None = None,
    route: str | None = None,
    stage: str | None = None,
    owner: str | None = None,
    workflow_status: str | None = None,
    blocked_only: bool = False,
) -> list[dict[str, Any]]:
    """Filter the global experiment-index.yaml by problem, workflow, and verdict fields."""
    index_path = repo_root / "research" / "active" / "experiment-index.yaml"
    if not index_path.exists():
        return []
    data = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []

    results: list[dict[str, Any]] = []
    for entry in cast(list[dict[str, Any]], data):
        if problem_id is not None and entry.get("problem_id") != problem_id:
            continue
        if verdict is not None and entry.get("latest_verdict") != verdict:
            continue
        if route is not None and entry.get("active_route") != route:
            continue
        if stage is not None and entry.get("current_stage") != stage:
            continue
        if owner is not None and entry.get("current_owner") != owner:
            continue
        if workflow_status is not None and entry.get("workflow_status") != workflow_status:
            continue
        if blocked_only and not entry.get("blocked"):
            continue
        results.append(entry)
    return results


def _format_ledger_results(results: list[dict[str, Any]], *, output_format: str = "yaml") -> str:
    if not results:
        return "No matching entries found."
    if output_format == "table":
        lines: list[str] = []
        header = f"{'run_id':<40} {'route':<18} {'status':<12} {'verdict':<14} {'started'}"
        lines.append(header)
        lines.append("-" * len(header))
        for r in results:
            lines.append(
                f"{r.get('run_id', '?'):<40} {r.get('route', '?'):<18} "
                f"{r.get('status', '?'):<12} {str(r.get('verdict', '?')):<14} "
                f"{r.get('started', '?')}"
            )
        return "\n".join(lines)
    return yaml.safe_dump(results, sort_keys=False, allow_unicode=True)


def _format_global_results(results: list[dict[str, Any]], *, output_format: str = "yaml") -> str:
    if not results:
        return "No matching entries found."
    if output_format == "table":
        lines: list[str] = []
        header = (
            f"{'problem_id':<28} {'route':<18} {'stage':<12} {'owner':<16} "
            f"{'wf_status':<12} {'active_run':<28} {'verdict':<14}"
        )
        lines.append(header)
        lines.append("-" * len(header))
        for entry in results:
            lines.append(
                f"{str(entry.get('problem_id', '?')):<28} {str(entry.get('active_route', '?')):<18} "
                f"{str(entry.get('current_stage', '?')):<12} {str(entry.get('current_owner', '?')):<16} "
                f"{str(entry.get('workflow_status', '?')):<12} {str(entry.get('active_run_id', '-')):<28} "
                f"{str(entry.get('latest_verdict', '-')):<14}"
            )
        return "\n".join(lines)
    return yaml.safe_dump(results, sort_keys=False, allow_unicode=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omega-query",
        description="Search and filter OMEGA experiment ledger entries.",
    )
    parser.add_argument("--problem", help="Filter by problem ID")
    parser.add_argument("--route", choices=["experiment-first", "proof-first", "survey-first"])
    parser.add_argument("--verdict", choices=["positive", "negative", "inconclusive"])
    parser.add_argument("--status", choices=["running", "completed", "failed", "abandoned"])
    parser.add_argument("--agent", help="Filter by agent role")
    parser.add_argument("--artifact-type", help="Filter runs containing this artifact type")
    parser.add_argument("--after", help="Only runs started on or after this date (YYYY-MM-DD)")
    parser.add_argument("--before", help="Only runs started before this date (YYYY-MM-DD)")
    parser.add_argument("--stage", help="Filter global workflow entries by current stage")
    parser.add_argument("--owner", help="Filter global workflow entries by current owner")
    parser.add_argument("--workflow-status", choices=["ready", "running", "blocked", "completed"],
                        help="Filter global workflow entries by workflow status")
    parser.add_argument("--blocked-only", action="store_true",
                        help="Only return globally indexed workspaces whose workflow is blocked")
    parser.add_argument("--global", dest="global_index", action="store_true",
                        help="Query the global experiment-index.yaml instead of per-problem ledgers")
    parser.add_argument("--format", choices=["yaml", "table"], default="yaml",
                        help="Output format (default: yaml)")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT,
                        help="Repository root (default: auto-detected)")

    args = parser.parse_args()

    if args.global_index:
        results = query_global_index(
            args.repo_root,
            problem_id=args.problem,
            verdict=args.verdict,
            route=args.route,
            stage=args.stage,
            owner=args.owner,
            workflow_status=args.workflow_status,
            blocked_only=args.blocked_only,
        )
        print(_format_global_results(results, output_format=args.format))
    else:
        # Query all per-problem ledgers or a specific one
        active_root = args.repo_root / "research" / "active"
        if not active_root.exists():
            print("No active research workspaces found.", file=sys.stderr)
            sys.exit(1)

        all_entries: list[dict[str, Any]] = []
        if args.problem:
            ledger_path = active_root / args.problem / "experiments" / "ledger.yaml"
            if ledger_path.exists():
                data = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    all_entries.extend(cast(list[dict[str, Any]], data))
        else:
            for candidate in sorted(active_root.iterdir()):
                if not candidate.is_dir():
                    continue
                ledger_path = candidate / "experiments" / "ledger.yaml"
                if not ledger_path.exists():
                    continue
                data = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    all_entries.extend(cast(list[dict[str, Any]], data))

        results = query_ledger(
            all_entries,
            problem_id=args.problem,
            route=args.route,
            verdict=args.verdict,
            status=args.status,
            agent=args.agent,
            artifact_type=args.artifact_type,
            after=args.after,
            before=args.before,
        )
        print(_format_ledger_results(results, output_format=args.format))


if __name__ == "__main__":
    main()
