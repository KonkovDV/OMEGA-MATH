#!/usr/bin/env python3
"""Unit tests for OMEGA proof_repair_loop utility."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import proof_repair_loop as repair  # type: ignore


class _FakeLeanAdapter:
    def check_file(self, lean_file: Path, *, timeout_seconds: int = 120):
        content = lean_file.read_text(encoding="utf-8")
        if "sorry" in content:
            return {
                "success": False,
                "errors": [{"message": "declaration uses sorry"}],
                "warnings": [],
            }
        if "exact True.intro" in content:
            return {
                "success": True,
                "errors": [],
                "warnings": [],
            }
        return {
            "success": False,
            "errors": [{"message": "unknown tactic"}],
            "warnings": [],
        }


class ProofRepairLoopTests(unittest.TestCase):
    def test_count_and_replace_sorry(self) -> None:
        source = "theorem t : True := by\n  sorry\n"
        self.assertEqual(repair.count_sorries(source), 1)
        patched = repair.replace_first_sorry(source, "exact True.intro")
        self.assertEqual(repair.count_sorries(patched), 0)
        self.assertIn("exact True.intro", patched)

    def test_parse_temperature_schedule(self) -> None:
        schedule = repair.parse_temperature_schedule("0.1, 0.2,0.5")
        self.assertEqual(schedule, [0.1, 0.2, 0.5])

    def test_run_loop_verifies_with_fake_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lean_file = Path(tmpdir) / "Example.lean"
            lean_file.write_text("theorem t : True := by\n  sorry\n", encoding="utf-8")

            def provider(_context: str, _diagnostics: str, _n: int, _temp: float):
                return ["exact True.intro"]

            result = repair.run_proof_repair_loop(
                lean_file,
                model="mock",
                base_url="http://localhost:8000/v1",
                api_key="",
                max_iterations=4,
                candidates=3,
                timeout_seconds=10,
                temperature_schedule=[0.1],
                in_place=True,
                adapter=_FakeLeanAdapter(),
                candidate_provider=provider,
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["status"], "verified")
            self.assertEqual(repair.count_sorries(lean_file.read_text(encoding="utf-8")), 0)

    def test_run_loop_returns_no_sorry_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lean_file = Path(tmpdir) / "NoSorry.lean"
            lean_file.write_text("theorem t : True := by\n  exact True.intro\n", encoding="utf-8")

            result = repair.run_proof_repair_loop(
                lean_file,
                model="mock",
                base_url="http://localhost:8000/v1",
                api_key="",
                max_iterations=2,
                candidates=2,
                timeout_seconds=10,
                temperature_schedule=[0.1],
                in_place=False,
                adapter=_FakeLeanAdapter(),
                candidate_provider=lambda *_: ["exact True.intro"],
            )

            self.assertFalse(result["success"])
            self.assertEqual(result["status"], "no-sorry-found")

    def test_run_loop_records_failure_channel_on_stagnation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lean_file = Path(tmpdir) / "Stagnant.lean"
            lean_file.write_text("theorem t : True := by\n  sorry\n", encoding="utf-8")
            failure_path = Path(tmpdir) / "failure-patterns.jsonl"

            def provider(_context: str, _diagnostics: str, _n: int, _temp: float):
                return ["sorry"]

            result = repair.run_proof_repair_loop(
                lean_file,
                model="mock",
                base_url="http://localhost:8000/v1",
                api_key="",
                max_iterations=5,
                candidates=1,
                timeout_seconds=10,
                temperature_schedule=[0.1],
                in_place=False,
                max_stagnant_iterations=1,
                problem_id="p1",
                run_id="r1",
                failure_channel_path=failure_path,
                adapter=_FakeLeanAdapter(),
                candidate_provider=provider,
            )

            self.assertFalse(result["success"])
            self.assertEqual(result["status"], "exhausted")
            self.assertTrue(failure_path.exists())
            lines = [line for line in failure_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertGreaterEqual(len(lines), 2)
            self.assertIn("repair-stagnation", lines[0])
            self.assertIn("repair-exhausted", lines[-1])


if __name__ == "__main__":
    unittest.main()
