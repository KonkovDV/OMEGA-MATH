"""Tests for OMEGA Evidence Bundle Verification.

Tests checksum computation, bundle generation, verification, and status reporting.
"""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import yaml


class TestComputeFileChecksum(unittest.TestCase):
    """Test SHA-256 file checksum computation."""

    def test_checksum_is_deterministic(self) -> None:
        from verify_evidence import compute_file_checksum

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("hello world")
            f.flush()
            path = Path(f.name)

        try:
            c1 = compute_file_checksum(path)
            c2 = compute_file_checksum(path)
            self.assertEqual(c1, c2)
            # Verify against known SHA-256
            expected = hashlib.sha256(b"hello world").hexdigest()
            self.assertEqual(c1, expected)
        finally:
            path.unlink()

    def test_different_content_different_checksum(self) -> None:
        from verify_evidence import compute_file_checksum

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f1:
            f1.write("content A")
            f1.flush()
            path1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f2:
            f2.write("content B")
            f2.flush()
            path2 = Path(f2.name)

        try:
            self.assertNotEqual(
                compute_file_checksum(path1),
                compute_file_checksum(path2),
            )
        finally:
            path1.unlink()
            path2.unlink()


class TestComputeEvidenceBundle(unittest.TestCase):
    """Test evidence bundle computation for a workspace."""

    def _make_workspace(self, tmpdir: str, problem_id: str) -> Path:
        """Create a minimal workspace with some artifacts."""
        workspace = Path(tmpdir) / "research" / "active" / problem_id
        artifacts = workspace / "artifacts"
        artifacts.mkdir(parents=True)
        experiments = workspace / "experiments"
        experiments.mkdir(parents=True)
        control = workspace / "control"
        control.mkdir(parents=True)

        (artifacts / "result_001.md").write_text("# Result 1\nSome findings.", encoding="utf-8")
        (artifacts / "result_002.md").write_text("# Result 2\nMore findings.", encoding="utf-8")
        (experiments / "ledger.yaml").write_text("runs: []\n", encoding="utf-8")

        return Path(tmpdir)

    def test_compute_creates_bundle_with_checksums(self) -> None:
        from verify_evidence import compute_evidence_bundle

        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._make_workspace(tmpdir, "test-prob")
            from unittest.mock import patch
            with patch("verify_evidence.REPO_ROOT", root):
                result = compute_evidence_bundle("test-prob")

            self.assertTrue(result["success"])
            self.assertEqual(result["problem_id"], "test-prob")
            self.assertGreater(result["artifact_count"], 0)

            # Bundle file written
            bundle_path = root / "research" / "active" / "test-prob" / "control" / "evidence-bundle.yaml"
            self.assertTrue(bundle_path.exists())
            bundle = yaml.safe_load(bundle_path.read_text(encoding="utf-8"))
            self.assertIn("artifacts", bundle)
            for entry in bundle["artifacts"]:
                self.assertIn("checksum_sha256", entry)
                self.assertIn("size_bytes", entry)
                self.assertEqual(len(entry["checksum_sha256"]), 64)  # SHA-256 hex length

    def test_compute_nonexistent_workspace_fails(self) -> None:
        from verify_evidence import compute_evidence_bundle

        with tempfile.TemporaryDirectory() as tmpdir:
            from unittest.mock import patch
            with patch("verify_evidence.REPO_ROOT", Path(tmpdir)):
                result = compute_evidence_bundle("nonexistent-problem")

            self.assertFalse(result["success"])
            self.assertIn("not found", result["error"])


class TestVerifyEvidenceBundle(unittest.TestCase):
    """Test evidence bundle verification."""

    def _make_workspace_with_bundle(self, tmpdir: str, problem_id: str) -> Path:
        root = Path(tmpdir)
        workspace = root / "research" / "active" / problem_id
        artifacts = workspace / "artifacts"
        artifacts.mkdir(parents=True)
        control = workspace / "control"
        control.mkdir(parents=True)

        content_a = "# File A\nContent."
        content_b = "# File B\nOther content."
        (artifacts / "a.md").write_text(content_a, encoding="utf-8")
        (artifacts / "b.md").write_text(content_b, encoding="utf-8")

        # Compute checksums from what's actually on disk (accounts for OS newline encoding)
        from verify_evidence import compute_file_checksum
        checksum_a = compute_file_checksum(artifacts / "a.md")
        checksum_b = compute_file_checksum(artifacts / "b.md")
        size_a = (artifacts / "a.md").stat().st_size
        size_b = (artifacts / "b.md").stat().st_size

        bundle = {
            "problem_id": problem_id,
            "timestamp": "2026-04-13T00:00:00Z",
            "artifact_count": 2,
            "total_size_bytes": size_a + size_b,
            "artifacts": [
                {
                    "path": "artifacts/a.md",
                    "checksum_sha256": checksum_a,
                    "size_bytes": size_a,
                },
                {
                    "path": "artifacts/b.md",
                    "checksum_sha256": checksum_b,
                    "size_bytes": size_b,
                },
            ],
        }
        (control / "evidence-bundle.yaml").write_text(
            yaml.safe_dump(bundle, sort_keys=False), encoding="utf-8"
        )
        return root

    def test_verify_passes_for_correct_checksums(self) -> None:
        from verify_evidence import verify_evidence_bundle

        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._make_workspace_with_bundle(tmpdir, "test-prob")
            from unittest.mock import patch
            with patch("verify_evidence.REPO_ROOT", root):
                result = verify_evidence_bundle("test-prob")

            self.assertTrue(result["success"])
            self.assertEqual(result["verdict"], "PASS")
            self.assertEqual(result["verified_count"], 2)
            self.assertEqual(result["failed_count"], 0)
            self.assertEqual(result["missing_count"], 0)

    def test_verify_detects_tampered_file(self) -> None:
        from verify_evidence import verify_evidence_bundle

        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._make_workspace_with_bundle(tmpdir, "test-prob")
            # Tamper with a file
            tampered = root / "research" / "active" / "test-prob" / "artifacts" / "a.md"
            tampered.write_text("# TAMPERED CONTENT", encoding="utf-8")

            from unittest.mock import patch
            with patch("verify_evidence.REPO_ROOT", root):
                result = verify_evidence_bundle("test-prob")

            self.assertFalse(result["success"])
            self.assertEqual(result["verdict"], "FAIL")
            self.assertEqual(result["failed_count"], 1)
            self.assertEqual(result["failures"][0]["status"], "MISMATCH")

    def test_verify_detects_missing_file(self) -> None:
        from verify_evidence import verify_evidence_bundle

        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._make_workspace_with_bundle(tmpdir, "test-prob")
            # Delete a file
            (root / "research" / "active" / "test-prob" / "artifacts" / "b.md").unlink()

            from unittest.mock import patch
            with patch("verify_evidence.REPO_ROOT", root):
                result = verify_evidence_bundle("test-prob")

            self.assertFalse(result["success"])
            self.assertEqual(result["missing_count"], 1)

    def test_verify_no_bundle_returns_error(self) -> None:
        from verify_evidence import verify_evidence_bundle

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace = root / "research" / "active" / "no-bundle"
            workspace.mkdir(parents=True)

            from unittest.mock import patch
            with patch("verify_evidence.REPO_ROOT", root):
                result = verify_evidence_bundle("no-bundle")

            self.assertFalse(result["success"])
            self.assertIn("No evidence bundle", result["error"])


class TestEvidenceStatus(unittest.TestCase):
    """Test evidence status reporting."""

    def test_status_for_nonexistent_workspace(self) -> None:
        from verify_evidence import evidence_status

        with tempfile.TemporaryDirectory() as tmpdir:
            from unittest.mock import patch
            with patch("verify_evidence.REPO_ROOT", Path(tmpdir)):
                result = evidence_status("nonexistent")

            self.assertFalse(result["success"])

    def test_status_reports_artifact_counts(self) -> None:
        from verify_evidence import evidence_status

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace = root / "research" / "active" / "test-prob"
            artifacts = workspace / "artifacts"
            artifacts.mkdir(parents=True)
            (artifacts / "file.md").write_text("content", encoding="utf-8")

            from unittest.mock import patch
            with patch("verify_evidence.REPO_ROOT", root):
                result = evidence_status("test-prob")

            self.assertTrue(result["success"])
            self.assertGreater(result["total_files"], 0)


if __name__ == "__main__":
    unittest.main()
