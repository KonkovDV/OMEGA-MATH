#!/usr/bin/env python3
"""Unit tests for the OMEGA CAS (Computer Algebra System) execution adapter."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cas_adapter import CASAdapter  # type: ignore

# SymPy availability check
try:
    import sympy  # noqa: F401
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False


class TestCASAdapterSimplify(unittest.TestCase):
    """Tests for CASAdapter.simplify()."""

    def setUp(self) -> None:
        self.adapter = CASAdapter()

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_simplify_trig(self) -> None:
        result = self.adapter.simplify("sin(x)**2 + cos(x)**2")
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "1")
        self.assertEqual(result["action"], "simplify")

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_simplify_algebraic(self) -> None:
        result = self.adapter.simplify("(x**2 - 1)/(x - 1)")
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "x + 1")


class TestCASAdapterSolve(unittest.TestCase):
    """Tests for CASAdapter.solve()."""

    def setUp(self) -> None:
        self.adapter = CASAdapter()

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_solve_linear(self) -> None:
        result = self.adapter.solve("2*x + 3", variable="x")
        self.assertTrue(result["success"])
        self.assertIn("-3/2", result["result"])

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_solve_quadratic(self) -> None:
        result = self.adapter.solve("x**2 - 5*x + 6", variable="x")
        self.assertTrue(result["success"])
        # Should find roots 2 and 3
        self.assertIn("2", result["result"])
        self.assertIn("3", result["result"])


class TestCASAdapterSeries(unittest.TestCase):
    """Tests for CASAdapter.series()."""

    def setUp(self) -> None:
        self.adapter = CASAdapter()

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_exp_series(self) -> None:
        result = self.adapter.series("exp(x)", variable="x", point=0, order=4)
        self.assertTrue(result["success"])
        # First few terms of e^x
        self.assertIn("x**2/2", result["result"])
        self.assertIn("x**3/6", result["result"])


class TestCASAdapterFactor(unittest.TestCase):
    """Tests for CASAdapter.factor()."""

    def setUp(self) -> None:
        self.adapter = CASAdapter()

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_factor_polynomial(self) -> None:
        result = self.adapter.factor("x**2 - 1")
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "(x - 1)*(x + 1)")

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_factor_integer_via_custom(self) -> None:
        result = self.adapter.custom("result = factorint(60)")
        self.assertTrue(result["success"])
        # factorint returns {2: 2, 3: 1, 5: 1}
        self.assertIn("2", result["result"])
        self.assertIn("3", result["result"])
        self.assertIn("5", result["result"])


class TestCASAdapterCalculus(unittest.TestCase):
    """Tests for integrate() and differentiate()."""

    def setUp(self) -> None:
        self.adapter = CASAdapter()

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_differentiate(self) -> None:
        result = self.adapter.differentiate("x**3 + 2*x", variable="x")
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "3*x**2 + 2")

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_integrate(self) -> None:
        result = self.adapter.integrate("2*x", variable="x")
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "x**2")


class TestCASAdapterCustom(unittest.TestCase):
    """Tests for custom SymPy code execution."""

    def setUp(self) -> None:
        self.adapter = CASAdapter()

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_custom_expression(self) -> None:
        code = "result = isprime(17)"
        result = self.adapter.custom(code)
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "True")

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_custom_security_blocks_import(self) -> None:
        code = "import os; result = 1"
        result = self.adapter.custom(code)
        self.assertFalse(result["success"])
        self.assertIn("error", result)


class TestCASAdapterResultSchema(unittest.TestCase):
    """Tests that CASResult conforms to the protocol contract."""

    def setUp(self) -> None:
        self.adapter = CASAdapter()

    @unittest.skipUnless(HAS_SYMPY, "sympy not installed")
    def test_result_has_required_fields(self) -> None:
        result = self.adapter.simplify("x + 0")
        required = {"success", "action", "backend", "result", "latex",
                     "duration_seconds", "error"}
        self.assertTrue(required.issubset(result.keys()), f"Missing: {required - result.keys()}")
        self.assertEqual(result["backend"], "sympy")
        self.assertIsInstance(result["duration_seconds"], float)


if __name__ == "__main__":
    unittest.main()
