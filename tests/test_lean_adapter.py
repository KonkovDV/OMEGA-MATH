#!/usr/bin/env python3
"""Unit tests for the OMEGA Lean 4 execution adapter."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lean_adapter import LeanAdapter, parse_lean_diagnostics  # type: ignore


class TestParseLeanDiagnostics(unittest.TestCase):
    """Tests for Lean diagnostic output parsing."""

    def test_parse_single_error(self) -> None:
        stderr = "MyFile.lean:10:4: error: unknown identifier 'foo'\n"
        diags = parse_lean_diagnostics(stderr)
        self.assertEqual(len(diags), 1)
        self.assertEqual(diags[0]["file"], "MyFile.lean")
        self.assertEqual(diags[0]["line"], 10)
        self.assertEqual(diags[0]["column"], 4)
        self.assertEqual(diags[0]["severity"], "error")
        self.assertIn("unknown identifier", diags[0]["message"])

    def test_parse_warning(self) -> None:
        stderr = "Foo.lean:5:0: warning: unused variable 'x'\n"
        diags = parse_lean_diagnostics(stderr)
        self.assertEqual(len(diags), 1)
        self.assertEqual(diags[0]["severity"], "warning")

    def test_parse_multiple_diagnostics(self) -> None:
        stderr = (
            "A.lean:1:0: error: msg1\n"
            "B.lean:2:3: warning: msg2\n"
            "C.lean:99:1: error: msg3\n"
        )
        diags = parse_lean_diagnostics(stderr)
        self.assertEqual(len(diags), 3)
        self.assertEqual(diags[0]["file"], "A.lean")
        self.assertEqual(diags[2]["line"], 99)

    def test_parse_empty_output(self) -> None:
        self.assertEqual(parse_lean_diagnostics(""), [])

    def test_parse_multiline_message(self) -> None:
        stderr = (
            "File.lean:10:0: error: type mismatch\n"
            "  expected: Nat\n"
            "  got: String\n"
        )
        diags = parse_lean_diagnostics(stderr)
        self.assertEqual(len(diags), 1)
        self.assertIn("type mismatch", diags[0]["message"])
        self.assertIn("expected: Nat", diags[0]["message"])


class TestLeanAdapterCheckFile(unittest.TestCase):
    """Tests for LeanAdapter.check_file() with mocked subprocess."""

    def setUp(self) -> None:
        self.adapter = LeanAdapter()

    @patch("lean_adapter.subprocess.run")
    def test_check_file_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )
        result = self.adapter.check_file(Path("test.lean"))
        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["action"], "check-file")
        self.assertEqual(result["errors"], [])

    @patch("lean_adapter.subprocess.run")
    def test_check_file_with_errors(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="test.lean:5:2: error: unknown identifier 'bad'\n",
        )
        result = self.adapter.check_file(Path("test.lean"))
        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["line"], 5)

    @patch("lean_adapter.subprocess.run")
    def test_check_file_timeout(self, mock_run: MagicMock) -> None:
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="lean", timeout=120)
        result = self.adapter.check_file(Path("test.lean"), timeout_seconds=120)
        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], -1)
        self.assertIn("timed out", result["errors"][0]["message"])


class TestLeanAdapterBuildProject(unittest.TestCase):
    """Tests for LeanAdapter.build_project() with mocked subprocess."""

    def setUp(self) -> None:
        self.adapter = LeanAdapter()

    @patch("lean_adapter.subprocess.run")
    def test_build_project_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Build completed successfully.\n",
            stderr="",
        )
        result = self.adapter.build_project(Path("/tmp/my-lean-project"))
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "build-project")

    @patch("lean_adapter.subprocess.run")
    def test_build_project_failure(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Main.lean:3:0: error: declaration uses sorry\n",
        )
        result = self.adapter.build_project(Path("/tmp/my-lean-project"))
        self.assertFalse(result["success"])
        self.assertEqual(len(result["errors"]), 1)


class TestLeanAdapterRunCommand(unittest.TestCase):
    """Tests for LeanAdapter.run_command() with mocked subprocess."""

    def setUp(self) -> None:
        self.adapter = LeanAdapter()

    @patch("lean_adapter.subprocess.run")
    def test_run_arbitrary_command(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="lean (version 4.29.0)\n",
            stderr="",
        )
        result = self.adapter.run_command("lean --version")
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "run-command")
        self.assertIn("4.29.0", result["stdout"])


class TestLeanAdapterResultSchema(unittest.TestCase):
    """Tests that LeanResult conforms to the protocol contract."""

    def setUp(self) -> None:
        self.adapter = LeanAdapter()

    @patch("lean_adapter.subprocess.run")
    def test_result_has_required_fields(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = self.adapter.check_file(Path("test.lean"))
        required = {"success", "action", "exit_code", "stdout", "stderr",
                     "duration_seconds", "errors", "warnings"}
        self.assertTrue(required.issubset(result.keys()), f"Missing: {required - result.keys()}")
        self.assertIsInstance(result["duration_seconds"], float)
        self.assertIsInstance(result["errors"], list)
        self.assertIsInstance(result["warnings"], list)


if __name__ == "__main__":
    unittest.main()
