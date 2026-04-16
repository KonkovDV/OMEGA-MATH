#!/usr/bin/env python3
"""OMEGA release-version sync validator.

Checks that release versions are aligned across:
- pyproject.toml      -> project.version
- CITATION.cff        -> version
- PROTOCOL.md header  -> # Version: X.Y.Z

Usage:
  python scripts/verify_version_sync.py
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_FILE = REPO_ROOT / "pyproject.toml"
CITATION_FILE = REPO_ROOT / "CITATION.cff"
PROTOCOL_FILE = REPO_ROOT / "PROTOCOL.md"
PROTOCOL_VERSION_RE = re.compile(r"^#\s*Version:\s*([0-9]+\.[0-9]+\.[0-9]+)\b")


def _require_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")


def read_pyproject_version(path: Path | None = None) -> str:
    path = path or PYPROJECT_FILE
    _require_file(path)
    payload = tomllib.loads(path.read_text(encoding="utf-8"))
    project = payload.get("project")
    if not isinstance(project, dict):
        raise ValueError(f"Missing [project] table in {path}")
    version = project.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"Missing project.version in {path}")
    return version.strip()


def read_citation_version(path: Path | None = None) -> str:
    path = path or CITATION_FILE
    _require_file(path)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid YAML mapping in {path}")
    version = payload.get("version")
    if isinstance(version, (int, float)):
        version = str(version)
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"Missing version field in {path}")
    return version.strip()


def read_protocol_version(path: Path | None = None) -> str:
    path = path or PROTOCOL_FILE
    _require_file(path)
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PROTOCOL_VERSION_RE.match(line.strip())
        if match:
            return match.group(1)
    raise ValueError(f"Missing '# Version: X.Y.Z' header in {path}")


def collect_versions() -> dict[str, str]:
    return {
        "pyproject": read_pyproject_version(),
        "citation": read_citation_version(),
        "protocol": read_protocol_version(),
    }


def validate_version_sync() -> tuple[bool, dict[str, Any]]:
    versions = collect_versions()
    unique_versions = sorted(set(versions.values()))
    if len(unique_versions) == 1:
        return True, {
            "success": True,
            "version": unique_versions[0],
            "sources": versions,
        }

    return False, {
        "success": False,
        "error": "Version mismatch across release metadata files",
        "sources": versions,
        "expected": unique_versions[0],
        "unique_versions": unique_versions,
    }


def main(argv: list[str] | None = None) -> int:
    del argv
    try:
        ok, payload = validate_version_sync()
    except Exception as exc:  # pragma: no cover - CLI guard
        payload = {
            "success": False,
            "error": str(exc),
        }
        ok = False

    print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
