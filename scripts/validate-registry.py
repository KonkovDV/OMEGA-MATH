#!/usr/bin/env python3
"""OMEGA Registry Validator — checks YAML consistency and cross-references.

Usage: python scripts/validate-registry.py
"""

import sys
import os
import re
from pathlib import Path
from collections import Counter

# Try to import PyYAML; fall back to a basic regex-based check if unavailable
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("WARNING: PyYAML not installed. Falling back to basic regex validation.", file=sys.stderr)

REPO_ROOT = Path(__file__).resolve().parent.parent  # math/
DOMAINS_DIR = REPO_ROOT / "registry" / "domains"
COLLECTIONS_DIR = REPO_ROOT / "registry" / "collections"
TRIAGE_FILE = REPO_ROOT / "registry" / "triage-matrix.yaml"

VALID_STATUSES = {"open", "resolved", "partially-resolved", "claimed-resolved", "resolved-independent", "resolved-negative"}
VALID_TIERS = {"T1-computational", "T2-experimental", "T3-pattern", "T4-structural", "T5-foundational"}

errors = []
warnings = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_yaml(path: Path):
    """Load YAML file, returns parsed dict or None."""
    if not HAS_YAML:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_ids_regex(path: Path) -> list[str]:
    """Extract problem IDs using regex (fallback when PyYAML unavailable)."""
    ids = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"^\s{2}- id:\s+(\S+)", text, re.MULTILINE):
        ids.append(m.group(1))
    return ids


def validate_domain_files():
    """Check each domain YAML for structure and content."""
    all_ids = []
    domain_files = sorted(DOMAINS_DIR.glob("*.yaml"))

    deprecated = [f for f in domain_files if "deprecated" in f.read_text(encoding="utf-8").lower()[:200]]

    for f in domain_files:
        if f in deprecated:
            continue

        if HAS_YAML:
            data = load_yaml(f)
            if data is None:
                error(f"{f.name}: Failed to parse YAML")
                continue

            problems = data.get("problems", [])
            if not problems:
                warn(f"{f.name}: No problems found")
                continue

            for p in problems:
                pid = p.get("id")
                if not pid:
                    error(f"{f.name}: Problem missing 'id' field")
                    continue

                all_ids.append(pid)

                if not p.get("name"):
                    error(f"{f.name}/{pid}: Missing 'name'")
                if not p.get("status"):
                    error(f"{f.name}/{pid}: Missing 'status'")
                elif p["status"] not in VALID_STATUSES:
                    warn(f"{f.name}/{pid}: Unknown status '{p['status']}'")
                if not p.get("statement"):
                    warn(f"{f.name}/{pid}: Missing 'statement'")
                if not p.get("tags"):
                    warn(f"{f.name}/{pid}: Missing 'tags'")

                triage = p.get("ai_triage")
                if triage:
                    tier = triage.get("tier")
                    if tier and tier not in VALID_TIERS:
                        error(f"{f.name}/{pid}: Invalid tier '{tier}'")
                    score = triage.get("amenability_score")
                    if score is not None and not (0 <= score <= 10):
                        error(f"{f.name}/{pid}: amenability_score {score} out of range 0-10")
        else:
            ids = extract_ids_regex(f)
            all_ids.extend(ids)
            if not ids:
                warn(f"{f.name}: No problems found (regex)")

    # Check for duplicate IDs
    id_counts = Counter(all_ids)
    for pid, count in id_counts.items():
        if count > 1:
            error(f"Duplicate problem ID '{pid}' appears {count} times across domain files")

    return all_ids, id_counts


def validate_triage_matrix(all_domain_ids: set[str]):
    """Check triage matrix references exist in domain files."""
    if not TRIAGE_FILE.exists():
        error("triage-matrix.yaml not found")
        return

    triage_ids = extract_ids_regex(TRIAGE_FILE)

    for tid in triage_ids:
        if tid not in all_domain_ids:
            warn(f"triage-matrix.yaml: ID '{tid}' not found in any domain file")


def validate_collections(all_domain_ids: set[str]):
    """Check collection references."""
    if not COLLECTIONS_DIR.exists():
        warn("collections/ directory not found")
        return

    for f in sorted(COLLECTIONS_DIR.glob("*.yaml")):
        ids = extract_ids_regex(f)
        if not ids:
            # Collections may use registry_id instead
            text = f.read_text(encoding="utf-8")
            for m in re.finditer(r"registry_id:\s+(\S+)", text):
                rid = m.group(1)
                if rid not in all_domain_ids:
                    warn(f"{f.name}: registry_id '{rid}' not found in domain files")


def print_summary(all_ids: list[str]):
    """Print validation summary."""
    print(f"\n{'='*60}")
    print("OMEGA Registry Validation Report")
    print(f"{'='*60}")
    print(f"Domain files:   {len(list(DOMAINS_DIR.glob('*.yaml')))}")
    print(f"Total problems: {len(all_ids)}")
    print(f"Unique IDs:     {len(set(all_ids))}")
    print(f"Errors:         {len(errors)}")
    print(f"Warnings:       {len(warnings)}")
    print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
        print()

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ⚠ {w}")
        print()

    if not errors:
        print("✓ Registry validation passed (0 errors)")
    else:
        print(f"✗ Registry validation FAILED ({len(errors)} errors)")


def main():
    if not DOMAINS_DIR.exists():
        print(f"ERROR: Domains directory not found at {DOMAINS_DIR}", file=sys.stderr)
        sys.exit(1)

    all_ids, _ = validate_domain_files()
    domain_id_set = set(all_ids)

    validate_triage_matrix(domain_id_set)
    validate_collections(domain_id_set)
    print_summary(all_ids)

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
