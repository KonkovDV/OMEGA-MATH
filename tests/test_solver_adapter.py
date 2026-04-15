#!/usr/bin/env python3
"""Unit tests for the OMEGA SAT/SMT solver execution adapter."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from solver_adapter import SolverAdapter  # type: ignore

# Z3 availability check — tests that need Z3 are skipped if not installed
HAS_Z3 = importlib.util.find_spec("z3") is not None


class TestSolverAdapterZ3(unittest.TestCase):
    """Tests for Z3 SMT solving via SolverAdapter."""

    def setUp(self) -> None:
        self.adapter = SolverAdapter()

    @unittest.skipUnless(HAS_Z3, "z3-solver not installed")
    def test_simple_sat(self) -> None:
        spec = "x = Int('x'); y = Int('y'); solver.add(x + y == 10); solver.add(x > 0, y > 0)"
        result = self.adapter.solve_smt(spec)
        self.assertTrue(result["success"])
        self.assertTrue(result["satisfiable"])
        self.assertIn("x", result["model"])
        self.assertIn("y", result["model"])
        x, y = result["model"]["x"], result["model"]["y"]
        self.assertEqual(x + y, 10)
        self.assertGreater(x, 0)
        self.assertGreater(y, 0)

    @unittest.skipUnless(HAS_Z3, "z3-solver not installed")
    def test_unsat(self) -> None:
        spec = "x = Int('x'); solver.add(x > 5); solver.add(x < 3)"
        result = self.adapter.solve_smt(spec)
        self.assertTrue(result["success"])
        self.assertFalse(result["satisfiable"])
        self.assertEqual(result["model"], {})

    @unittest.skipUnless(HAS_Z3, "z3-solver not installed")
    def test_boolean_sat(self) -> None:
        spec = "a = Bool('a'); b = Bool('b'); solver.add(Or(a, b)); solver.add(Not(And(a, b)))"
        result = self.adapter.solve_smt(spec)
        self.assertTrue(result["success"])
        self.assertTrue(result["satisfiable"])

    @unittest.skipUnless(HAS_Z3, "z3-solver not installed")
    def test_optimization(self) -> None:
        spec = "x = Int('x'); solver.add(x >= 1); solver.add(x <= 100); solver.minimize(x)"
        result = self.adapter.solve_optimize(spec)
        self.assertTrue(result["success"])
        self.assertTrue(result["satisfiable"])
        self.assertEqual(result["model"]["x"], 1)

    @unittest.skipUnless(HAS_Z3, "z3-solver not installed")
    def test_timeout(self) -> None:
        # A very constrained problem that should complete fine, just check the field exists
        spec = "x = Int('x'); solver.add(x == 42)"
        result = self.adapter.solve_smt(spec, timeout_seconds=10)
        self.assertTrue(result["success"])
        self.assertIn("duration_seconds", result)
        self.assertIsInstance(result["duration_seconds"], float)

    @unittest.skipUnless(HAS_Z3, "z3-solver not installed")
    def test_spec_security_blocks_import(self) -> None:
        spec = "import os; x = Int('x'); solver.add(x == 1)"
        result = self.adapter.solve_smt(spec)
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @unittest.skipUnless(HAS_Z3, "z3-solver not installed")
    def test_spec_security_blocks_open(self) -> None:
        spec = "f = open('/etc/passwd'); x = Int('x'); solver.add(x == 1)"
        result = self.adapter.solve_smt(spec)
        self.assertFalse(result["success"])

    @unittest.skipUnless(HAS_Z3, "z3-solver not installed")
    def test_result_schema(self) -> None:
        spec = "x = Int('x'); solver.add(x == 5)"
        result = self.adapter.solve_smt(spec)
        required = {"success", "backend", "mode", "satisfiable", "model",
                     "objective", "duration_seconds", "error"}
        self.assertTrue(required.issubset(result.keys()), f"Missing: {required - result.keys()}")
        self.assertEqual(result["backend"], "z3")
        self.assertEqual(result["mode"], "smt")


class TestSolverAdapterPySAT(unittest.TestCase):
    """Tests for PySAT solving via SolverAdapter."""

    def setUp(self) -> None:
        self.adapter = SolverAdapter()

    def test_simple_sat_clauses(self) -> None:
        # (x1 OR x2) AND (NOT x1 OR x3)
        result = self.adapter.solve_sat(num_vars=3, clauses=[[1, 2], [-1, 3]])
        self.assertTrue(result["success"])
        self.assertTrue(result["satisfiable"])
        self.assertIsInstance(result["model"], dict)

    def test_unsat_clauses(self) -> None:
        # x1 AND NOT x1
        result = self.adapter.solve_sat(num_vars=1, clauses=[[1], [-1]])
        self.assertTrue(result["success"])
        self.assertFalse(result["satisfiable"])

    def test_empty_clauses(self) -> None:
        result = self.adapter.solve_sat(num_vars=0, clauses=[])
        self.assertTrue(result["success"])
        self.assertTrue(result["satisfiable"])

    def test_result_schema(self) -> None:
        result = self.adapter.solve_sat(num_vars=2, clauses=[[1, 2]])
        required = {"success", "backend", "mode", "satisfiable", "model",
                     "objective", "duration_seconds", "error"}
        self.assertTrue(required.issubset(result.keys()))
        self.assertIn(result["backend"], {"pysat", "pysat-builtin"})
        self.assertEqual(result["mode"], "sat")


if __name__ == "__main__":
    unittest.main()
