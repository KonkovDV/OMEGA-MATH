#!/usr/bin/env python3
"""OMEGA Evidence Bundle Verification.

Computes and verifies SHA-256 checksums for all artifacts referenced in an
evidence bundle, making the verification pipeline executable.

See protocol/evidence-governance.md for evidence class definitions.

Usage:
  python scripts/verify_evidence.py compute <problem-id>
  python scripts/verify_evidence.py verify <problem-id>
  python scripts/verify_evidence.py status <problem-id>
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def compute_file_checksum(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_workspace_artifacts(problem_id: str) -> list[Path]:
    """Find all artifact files in a problem workspace."""
    workspace = REPO_ROOT / "research" / "active" / problem_id
    artifacts: list[Path] = []

    # Artifacts directory
    art_dir = workspace / "artifacts"
    if art_dir.exists():
        artifacts.extend(
            f for f in sorted(art_dir.rglob("*"))
            if f.is_file() and f.name != "manifest.yaml"
        )

    # Experiment logs
    exp_dir = workspace / "experiments"
    if exp_dir.exists():
        artifacts.extend(
            f for f in sorted(exp_dir.rglob("*"))
            if f.is_file() and f.suffix in (".yaml", ".yml", ".json", ".md", ".log", ".txt", ".csv")
        )

    # Paper artifacts
    paper_dir = workspace / "paper"
    if paper_dir.exists():
        artifacts.extend(
            f for f in sorted(paper_dir.rglob("*"))
            if f.is_file()
        )

    return artifacts


def compute_evidence_bundle(problem_id: str) -> dict[str, Any]:
    """Compute checksums for all artifacts in a problem workspace."""
    workspace = REPO_ROOT / "research" / "active" / problem_id
    if not workspace.exists():
        return {
            "success": False,
            "error": f"Workspace not found: {workspace}",
        }

    artifacts = find_workspace_artifacts(problem_id)
    entries: list[dict[str, Any]] = []
    total_size = 0

    for artifact_path in artifacts:
        rel_path = artifact_path.relative_to(workspace)
        checksum = compute_file_checksum(artifact_path)
        size = artifact_path.stat().st_size
        total_size += size

        entries.append({
            "path": str(rel_path).replace("\\", "/"),
            "checksum_sha256": checksum,
            "size_bytes": size,
            "last_modified": datetime.fromtimestamp(
                artifact_path.stat().st_mtime, tz=UTC
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    bundle = {
        "problem_id": problem_id,
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifact_count": len(entries),
        "total_size_bytes": total_size,
        "artifacts": entries,
    }

    # Write bundle to workspace
    bundle_path = workspace / "control" / "evidence-bundle.yaml"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(
        yaml.safe_dump(bundle, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    return {
        "success": True,
        "problem_id": problem_id,
        "artifact_count": len(entries),
        "total_size_bytes": total_size,
        "bundle_path": str(bundle_path),
    }


def verify_evidence_bundle(problem_id: str) -> dict[str, Any]:
    """Verify all artifacts match their recorded checksums."""
    workspace = REPO_ROOT / "research" / "active" / problem_id
    bundle_path = workspace / "control" / "evidence-bundle.yaml"

    if not bundle_path.exists():
        return {
            "success": False,
            "error": f"No evidence bundle found at {bundle_path}. Run 'compute' first.",
        }

    bundle = yaml.safe_load(bundle_path.read_text(encoding="utf-8")) or {}
    entries = bundle.get("artifacts", [])

    verified: list[dict[str, str]] = []
    failed: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []

    for entry in entries:
        rel_path = entry["path"]
        expected_checksum = entry["checksum_sha256"]
        full_path = workspace / rel_path

        if not full_path.exists():
            missing.append({
                "path": rel_path,
                "expected_checksum": expected_checksum,
                "status": "MISSING",
            })
            continue

        actual_checksum = compute_file_checksum(full_path)
        if actual_checksum == expected_checksum:
            verified.append({
                "path": rel_path,
                "checksum": actual_checksum,
                "status": "OK",
            })
        else:
            failed.append({
                "path": rel_path,
                "expected": expected_checksum,
                "actual": actual_checksum,
                "status": "MISMATCH",
            })

    all_ok = len(failed) == 0 and len(missing) == 0
    return {
        "success": all_ok,
        "problem_id": problem_id,
        "bundle_timestamp": bundle.get("timestamp"),
        "total_artifacts": len(entries),
        "verified_count": len(verified),
        "failed_count": len(failed),
        "missing_count": len(missing),
        "verdict": "PASS" if all_ok else "FAIL",
        "failures": failed,
        "missing": missing,
    }


def evidence_status(problem_id: str) -> dict[str, Any]:
    """Report on the evidence status for a problem workspace."""
    workspace = REPO_ROOT / "research" / "active" / problem_id
    if not workspace.exists():
        return {"success": False, "error": f"Workspace not found: {workspace}"}

    bundle_path = workspace / "control" / "evidence-bundle.yaml"
    has_bundle = bundle_path.exists()

    artifacts = find_workspace_artifacts(problem_id)
    manifest_path = workspace / "artifacts" / "manifest.yaml"
    has_manifest = manifest_path.exists()

    # Count by evidence class if manifest exists
    class_counts: dict[str, int] = {"R0": 0, "R1": 0, "E1": 0, "E2": 0, "H": 0, "unknown": 0}
    if has_manifest:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        for entry in manifest.get("artifacts", []):
            ec = entry.get("evidence_class", "unknown")
            class_counts[ec] = class_counts.get(ec, 0) + 1

    return {
        "success": True,
        "problem_id": problem_id,
        "total_files": len(artifacts),
        "has_evidence_bundle": has_bundle,
        "has_artifact_manifest": has_manifest,
        "evidence_class_counts": class_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omega-verify-evidence",
        description="OMEGA Evidence Bundle Verification.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    compute_cmd = sub.add_parser("compute", help="Compute checksums for all artifacts")
    compute_cmd.add_argument("problem_id", help="Problem ID")

    verify_cmd = sub.add_parser("verify", help="Verify artifact checksums")
    verify_cmd.add_argument("problem_id", help="Problem ID")

    status_cmd = sub.add_parser("status", help="Report evidence status")
    status_cmd.add_argument("problem_id", help="Problem ID")

    args = parser.parse_args()

    if args.command == "compute":
        result = compute_evidence_bundle(args.problem_id)
    elif args.command == "verify":
        result = verify_evidence_bundle(args.problem_id)
    elif args.command == "status":
        result = evidence_status(args.problem_id)
    else:
        parser.error(f"Unknown command: {args.command}")
        return

    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
