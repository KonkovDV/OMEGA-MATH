#!/usr/bin/env python3
"""Generate the OMEGA registry index from active domain and collection files.

Usage: python scripts/generate_index.py
"""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = REPO_ROOT / "registry" / "domains"
COLLECTIONS_DIR = REPO_ROOT / "registry" / "collections"
TRIAGE_FILE = REPO_ROOT / "registry" / "triage-matrix.yaml"
INDEX_FILE = REPO_ROOT / "registry" / "index.yaml"
TRIAGE_SECTIONS = (
    "tier_1_computational",
    "tier_2_experimental",
    "tier_3_pattern",
    "tier_4_structural",
    "tier_5_foundational",
)
NON_OPEN_STATUSES = {
    "partially-resolved",
    "claimed-resolved",
    "resolved",
    "resolved-independent",
    "resolved-negative",
}


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def is_deprecated_domain_file(path: Path) -> bool:
    if path.name == "other-domains.yaml":
        return True
    text = path.read_text(encoding="utf-8").lower()
    head = text[:400]
    return "deprecated" in head and "redirect notice" in head


def get_active_domain_files() -> list[Path]:
    return [path for path in sorted(DOMAINS_DIR.glob("*.yaml")) if not is_deprecated_domain_file(path)]


def get_collection_files() -> list[Path]:
    return sorted(COLLECTIONS_DIR.glob("*.yaml"))


def resolve_snapshot_date() -> str:
    """Resolve deterministic snapshot date for generated index.

    Prefers the latest git commit date across registry source files so output
    remains stable when inputs are unchanged. Falls back to today's date when
    git metadata is unavailable.
    """
    source_files: list[Path] = [*get_active_domain_files(), *get_collection_files()]
    if TRIAGE_FILE.exists():
        source_files.append(TRIAGE_FILE)

    rel_paths = [path.relative_to(REPO_ROOT).as_posix() for path in source_files if path.exists()]
    if rel_paths:
        try:
            proc = subprocess.run(
                ["git", "log", "-1", "--format=%cs", "--", *rel_paths],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            candidate = proc.stdout.strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate):
                return candidate
        except OSError:
            pass

    return str(date.today())


def extract_triage_entry_count() -> int:
    if not TRIAGE_FILE.exists():
        return 0
    data = load_yaml(TRIAGE_FILE)
    if not isinstance(data, dict):
        return 0
    return sum(len(data.get(section, []) or []) for section in TRIAGE_SECTIONS)


def infer_note(problem: dict) -> str | None:
    triage_notes = (problem.get("ai_triage") or {}).get("notes")
    if triage_notes:
        return " ".join(str(triage_notes).split())

    partial_results = problem.get("partial_results") or []
    if partial_results:
        description = partial_results[-1].get("description")
        if description:
            return " ".join(str(description).split())

    return None


def build_index(*, snapshot_date: str | None = None) -> dict:
    snapshot_date = snapshot_date or resolve_snapshot_date()
    problems: list[dict] = []
    domain_counts: Counter[str] = Counter()
    tier_counts: Counter[str] = Counter()

    for path in get_active_domain_files():
        data = load_yaml(path)
        domain_name = path.stem
        domain_problems = data.get("problems", [])
        domain_counts[domain_name] += len(domain_problems)

        for problem in domain_problems:
            problems.append({"domain": domain_name, **problem})
            triage = problem.get("ai_triage")
            if triage and triage.get("tier"):
                tier_counts[triage["tier"]] += 1

    collection_stats = {}
    for path in get_collection_files():
        data = load_yaml(path)
        collection_problems = data.get("problems", [])
        stat = {
            "count": len(collection_problems),
            "file": f"collections/{path.name}",
        }
        open_count = sum(1 for problem in collection_problems if problem.get("status") == "open")
        if open_count:
            stat["open"] = open_count
        collection_stats[path.stem] = stat

    highlights = []
    for problem in problems:
        if problem.get("status") not in NON_OPEN_STATUSES:
            continue
        highlight = {
            "id": problem["id"],
            "domain": problem["domain"],
            "status": problem["status"],
        }
        note = infer_note(problem)
        if note:
            highlight["note"] = note
        highlights.append(highlight)

    highlights.sort(key=lambda item: (item["domain"], item["id"]))

    with_ai_triage = sum(1 for problem in problems if problem.get("ai_triage"))
    total_problems = len(problems)
    triage_coverage_pct = round((with_ai_triage / total_problems) * 100, 1) if total_problems else 0.0

    return {
        "summary": {
            "total_problems": total_problems,
            "with_ai_triage": with_ai_triage,
            "triage_coverage_pct": triage_coverage_pct,
            "triage_matrix_entries": extract_triage_entry_count(),
            "domain_files": len(get_active_domain_files()),
            "deprecated_domain_redirects": len(list(DOMAINS_DIR.glob("*.yaml"))) - len(get_active_domain_files()),
            "collection_files": len(collection_stats),
            "last_updated": snapshot_date,
        },
        "tier_distribution": {
            "T1-computational": tier_counts.get("T1-computational", 0),
            "T2-experimental": tier_counts.get("T2-experimental", 0),
            "T3-pattern": tier_counts.get("T3-pattern", 0),
            "T4-structural": tier_counts.get("T4-structural", 0),
            "T5-foundational": tier_counts.get("T5-foundational", 0),
            "untriaged": total_problems - with_ai_triage,
        },
        "domain_counts": dict(sorted(domain_counts.items(), key=lambda item: (-item[1], item[0]))),
        "collections": collection_stats,
        "status_notes": highlights,
    }


def write_index(index: dict, *, snapshot_date: str | None = None) -> None:
    summary = index.get("summary") if isinstance(index, dict) else None
    resolved_snapshot_date = (
        snapshot_date
        or (summary.get("last_updated") if isinstance(summary, dict) else None)
        or str(date.today())
    )
    header = [
        "# OMEGA Registry Index",
        f"# Auto-generated: {resolved_snapshot_date}",
        "# Generated by: scripts/generate_index.py",
        "",
    ]
    body = yaml.safe_dump(index, sort_keys=False, allow_unicode=True)
    INDEX_FILE.write_text("\n".join(header) + body, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    del argv
    snapshot_date = resolve_snapshot_date()
    write_index(build_index(snapshot_date=snapshot_date), snapshot_date=snapshot_date)
    print(f"Updated {INDEX_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())