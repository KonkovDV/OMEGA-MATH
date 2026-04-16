#!/usr/bin/env python3
"""Tests for scripts/verify_version_sync.py."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import verify_version_sync as vsync  # type: ignore


class VersionSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.pyproject = self.root / "pyproject.toml"
        self.citation = self.root / "CITATION.cff"
        self.protocol = self.root / "PROTOCOL.md"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _write(self, version_a: str, version_b: str, version_c: str) -> None:
        self.pyproject.write_text(
            "[project]\n"
            f"version = \"{version_a}\"\n",
            encoding="utf-8",
        )
        self.citation.write_text(
            yaml.safe_dump({"cff-version": "1.2.0", "version": version_b}, sort_keys=False),
            encoding="utf-8",
        )
        self.protocol.write_text(
            "# OMEGA Research Protocol\n"
            f"# Version: {version_c} | Date: 2026-04-16\n",
            encoding="utf-8",
        )

    def _patch_paths(self):
        return patch.multiple(
            vsync,
            REPO_ROOT=self.root,
            PYPROJECT_FILE=self.pyproject,
            CITATION_FILE=self.citation,
            PROTOCOL_FILE=self.protocol,
        )

    def test_validate_version_sync_success(self) -> None:
        self._write("0.5.0", "0.5.0", "0.5.0")
        with self._patch_paths():
            ok, payload = vsync.validate_version_sync()
        self.assertTrue(ok)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["version"], "0.5.0")

    def test_validate_version_sync_detects_mismatch(self) -> None:
        self._write("0.5.0", "0.4.0", "0.5.0")
        with self._patch_paths():
            ok, payload = vsync.validate_version_sync()
        self.assertFalse(ok)
        self.assertFalse(payload["success"])
        self.assertIn("mismatch", payload["error"].lower())

    def test_main_returns_nonzero_on_error(self) -> None:
        self._write("0.5.0", "0.4.0", "0.5.0")
        with self._patch_paths():
            exit_code = vsync.main([])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
