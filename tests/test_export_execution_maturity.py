#!/usr/bin/env python3
"""Unit tests for OMG-101 execution maturity exporter."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from export_execution_maturity import build_execution_maturity_report  # type: ignore


class TestBuildExecutionMaturityReport(unittest.TestCase):
    def test_degraded_when_hard_failure_exists(self) -> None:
        report = build_execution_maturity_report(
            lean_capabilities={"lean_available": True, "lake_available": True, "sandbox_mode": "auto"},
            solver_capabilities={"z3_available": True, "pysat_available": False},
            lean_smoke={"success": True, "exit_code": 0, "stderr": ""},
            sat_smoke={"success": False, "satisfiable": None, "backend": "pysat-builtin", "error": "fail"},
            smt_smoke={"success": True, "error": None},
        )

        self.assertEqual(report["verification"]["status"], "DEGRADED")

    def test_warning_when_only_warning_checks_fail(self) -> None:
        report = build_execution_maturity_report(
            lean_capabilities={"lean_available": False, "lake_available": False, "sandbox_mode": "auto"},
            solver_capabilities={"z3_available": False, "pysat_available": False},
            lean_smoke={"success": False, "exit_code": -3, "stderr": "not found"},
            sat_smoke={"success": True, "satisfiable": True, "backend": "pysat-builtin", "error": None},
            smt_smoke={"success": False, "error": "z3 missing"},
        )

        self.assertEqual(report["verification"]["status"], "WARNING")

    def test_approved_when_all_checks_green(self) -> None:
        report = build_execution_maturity_report(
            lean_capabilities={"lean_available": True, "lake_available": True, "sandbox_mode": "auto"},
            solver_capabilities={"z3_available": True, "pysat_available": True},
            lean_smoke={"success": True, "exit_code": 0, "stderr": ""},
            sat_smoke={"success": True, "satisfiable": True, "backend": "pysat", "error": None},
            smt_smoke={"success": True, "error": None},
        )

        self.assertEqual(report["verification"]["status"], "APPROVED")
        self.assertEqual(report["metrics"]["hard_failures"], 0)


if __name__ == "__main__":
    unittest.main()
