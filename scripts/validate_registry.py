#!/usr/bin/env python3
"""OMEGA Registry Validator — checks YAML consistency and cross-references.

Usage: python scripts/validate-registry.py
"""

from __future__ import annotations

import importlib
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

yaml_module: Any | None = None
jsonschema_module: Any | None = None

try:
    yaml_module = importlib.import_module("yaml")
    has_yaml = True
except ImportError:
    has_yaml = False
    print("WARNING: PyYAML not installed. Falling back to basic regex validation.", file=sys.stderr)

try:
    jsonschema_module = importlib.import_module("jsonschema")
    has_jsonschema = True
except ImportError:
    has_jsonschema = False
    print("WARNING: jsonschema not installed. Schema validation is disabled.", file=sys.stderr)

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = REPO_ROOT / "registry" / "domains"
COLLECTIONS_DIR = REPO_ROOT / "registry" / "collections"
TRIAGE_FILE = REPO_ROOT / "registry" / "triage-matrix.yaml"
SCHEMA_FILE = REPO_ROOT / "registry" / "schema.json"

VALID_STATUSES = {"open", "resolved", "partially-resolved", "claimed-resolved", "resolved-independent", "resolved-negative"}
VALID_TIERS = {"T1-computational", "T2-experimental", "T3-pattern", "T4-structural", "T5-foundational"}

errors: list[str] = []
warnings: list[str] = []


def reset_messages() -> None:
    errors.clear()
    warnings.clear()


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_yaml(path: Path) -> dict[str, Any] | None:
    if not has_yaml:
        return None
    assert yaml_module is not None
    with open(path, "r", encoding="utf-8") as handle:
        return yaml_module.safe_load(handle)


def is_deprecated_domain_file(path: Path) -> bool:
    if path.name == "other-domains.yaml":
        return True
    text = path.read_text(encoding="utf-8").lower()
    head = text[:400]
    return "deprecated" in head and "redirect notice" in head


def get_active_domain_files() -> list[Path]:
    return [path for path in sorted(DOMAINS_DIR.glob("*.yaml")) if not is_deprecated_domain_file(path)]


def load_schema() -> dict[str, Any] | None:
    if not (has_yaml and has_jsonschema and SCHEMA_FILE.exists()):
        return None
    return load_yaml(SCHEMA_FILE)


def extract_ids_regex(path: Path) -> list[str]:
    ids: list[str] = []
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"^\s{2}- id:\s+(\S+)", text, re.MULTILINE):
        ids.append(match.group(1))
    return ids


def validate_domain_files() -> tuple[list[str], Counter[str]]:
    all_ids: list[str] = []
    domain_files = get_active_domain_files()
    schema = load_schema()

    for domain_file in domain_files:
        if has_yaml:
            data = load_yaml(domain_file)
            if data is None:
                error(f"{domain_file.name}: Failed to parse YAML")
                continue

            problems = data.get("problems", [])
            if not problems:
                warn(f"{domain_file.name}: No problems found")
                continue

            for problem in problems:
                problem_id = problem.get("id")
                if not problem_id:
                    error(f"{domain_file.name}: Problem missing 'id' field")
                    continue

                all_ids.append(problem_id)

                if not problem.get("name"):
                    error(f"{domain_file.name}/{problem_id}: Missing 'name'")
                if not problem.get("status"):
                    error(f"{domain_file.name}/{problem_id}: Missing 'status'")
                elif problem["status"] not in VALID_STATUSES:
                    warn(f"{domain_file.name}/{problem_id}: Unknown status '{problem['status']}'")
                if not problem.get("statement"):
                    warn(f"{domain_file.name}/{problem_id}: Missing 'statement'")
                if not problem.get("tags"):
                    warn(f"{domain_file.name}/{problem_id}: Missing 'tags'")

                triage = problem.get("ai_triage")
                if triage:
                    tier = triage.get("tier")
                    if tier and tier not in VALID_TIERS:
                        error(f"{domain_file.name}/{problem_id}: Invalid tier '{tier}'")
                    score = triage.get("amenability_score")
                    if score is not None and not (0 <= score <= 10):
                        error(f"{domain_file.name}/{problem_id}: amenability_score {score} out of range 0-10")

                if schema is not None:
                    assert jsonschema_module is not None
                    try:
                        jsonschema_module.validate({"domain": domain_file.stem, **problem}, schema)
                    except jsonschema_module.ValidationError as exc:
                        path_hint = ".".join(str(part) for part in exc.absolute_path) or "<root>"
                        error(f"{domain_file.name}/{problem_id}: Schema validation failed at {path_hint}: {exc.message}")
        else:
            ids = extract_ids_regex(domain_file)
            all_ids.extend(ids)
            if not ids:
                warn(f"{domain_file.name}: No problems found (regex)")

    id_counts = Counter(all_ids)
    for problem_id, count in id_counts.items():
        if count > 1:
            error(f"Duplicate problem ID '{problem_id}' appears {count} times across domain files")

    return all_ids, id_counts


def validate_triage_matrix(all_domain_ids: set[str]) -> None:
    if not TRIAGE_FILE.exists():
        error("triage-matrix.yaml not found")
        return

    triage_ids = extract_ids_regex(TRIAGE_FILE)
    for triage_id in triage_ids:
        if triage_id not in all_domain_ids:
            warn(f"triage-matrix.yaml: ID '{triage_id}' not found in any domain file")


def validate_collections(all_domain_ids: set[str]) -> None:
    if not COLLECTIONS_DIR.exists():
        warn("collections/ directory not found")
        return

    for collection_file in sorted(COLLECTIONS_DIR.glob("*.yaml")):
        if has_yaml:
            data = load_yaml(collection_file) or {}
            problems = data.get("problems", [])
            for problem in problems:
                registry_id = problem.get("registry_id")
                if registry_id and registry_id not in all_domain_ids:
                    warn(f"{collection_file.name}: registry_id '{registry_id}' not found in domain files")
        else:
            text = collection_file.read_text(encoding="utf-8")
            for match in re.finditer(r"registry_id:\s+(\S+)", text):
                registry_id = match.group(1)
                if registry_id not in all_domain_ids:
                    warn(f"{collection_file.name}: registry_id '{registry_id}' not found in domain files")


def print_summary(all_ids: list[str]) -> None:
    active_domain_files = get_active_domain_files()
    print(f"\n{'=' * 60}")
    print("OMEGA Registry Validation Report")
    print(f"{'=' * 60}")
    print(f"Domain files:   {len(active_domain_files)} active (+ deprecated redirects excluded)")
    print(f"Total problems: {len(all_ids)}")
    print(f"Unique IDs:     {len(set(all_ids))}")
    print(f"Errors:         {len(errors)}")
    print(f"Warnings:       {len(warnings)}")
    print()

    if errors:
        print("ERRORS:")
        for item in errors:
            print(f"  ✗ {item}")
        print()

    if warnings:
        print("WARNINGS:")
        for item in warnings:
            print(f"  ⚠ {item}")
        print()

    if not errors:
        print("✓ Registry validation passed (0 errors)")
    else:
        print(f"✗ Registry validation FAILED ({len(errors)} errors)")


def main(argv: list[str] | None = None) -> int:
    del argv
    reset_messages()
    if not DOMAINS_DIR.exists():
        print(f"ERROR: Domains directory not found at {DOMAINS_DIR}", file=sys.stderr)
        return 1

    all_ids, _ = validate_domain_files()
    domain_id_set = set(all_ids)
    validate_triage_matrix(domain_id_set)
    validate_collections(domain_id_set)
    print_summary(all_ids)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())