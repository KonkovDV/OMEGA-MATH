#!/usr/bin/env python3
"""OMEGA CAS (Computer Algebra System) execution adapter.

Wraps SymPy (primary) for symbolic computation. See protocol/cas-execution-adapter.md.

Usage:
  python scripts/cas_adapter.py simplify "sin(x)**2 + cos(x)**2"
  python scripts/cas_adapter.py solve "x**2 - 5*x + 6" --variable x
  python scripts/cas_adapter.py factor "x**2 - 1"
  python scripts/cas_adapter.py differentiate "x**3" --variable x
  python scripts/cas_adapter.py integrate "2*x" --variable x
  python scripts/cas_adapter.py series "exp(x)" --variable x --order 6
  python scripts/cas_adapter.py custom "result = isprime(17)"
"""

from __future__ import annotations

import argparse
import re
import time
from typing import Any

import yaml

# Security: forbidden patterns in custom code strings
_FORBIDDEN_PATTERNS = re.compile(
    r"\b(import|exec|eval|compile|open|__import__|getattr|setattr|delattr|globals|locals|vars"
    r"|os\.|sys\.|subprocess|shutil|pathlib|socket|http|urllib)\b"
)


def _check_spec_security(spec: str) -> str | None:
    """Return an error message if spec contains forbidden patterns, else None."""
    m = _FORBIDDEN_PATTERNS.search(spec)
    if m:
        return f"Forbidden pattern in spec: {m.group()!r}"
    return None


def _import_sympy() -> Any:
    """Import sympy or raise ImportError with guidance."""
    try:
        import sympy  # type: ignore[import-untyped]
        return sympy
    except ImportError:
        raise ImportError("sympy not installed. Install with: pip install sympy")


class CASAdapter:
    """Execution adapter for symbolic computation via SymPy."""

    def _build_result(
        self,
        action: str,
        result_str: str,
        latex_str: str | None,
        duration: float,
    ) -> dict[str, Any]:
        return {
            "success": True,
            "action": action,
            "backend": "sympy",
            "result": result_str,
            "latex": latex_str,
            "duration_seconds": round(duration, 3),
            "error": None,
        }

    def _error_result(self, action: str, error: str, duration: float) -> dict[str, Any]:
        return {
            "success": False,
            "action": action,
            "backend": "sympy",
            "result": None,
            "latex": None,
            "duration_seconds": round(duration, 3),
            "error": error,
        }

    def _parse_expr(self, sympy: Any, expression: str, variable: str = "x") -> Any:
        """Parse a string expression into a SymPy expression."""
        var = sympy.Symbol(variable)
        # Parse with the local variable in scope
        local_dict = {variable: var}
        return sympy.sympify(expression, locals=local_dict)

    def simplify(self, expression: str, *, variable: str = "x") -> dict[str, Any]:
        start = time.monotonic()
        try:
            sp = _import_sympy()
            expr = self._parse_expr(sp, expression, variable)
            result = sp.simplify(expr)
            return self._build_result(
                "simplify", str(result), sp.latex(result), time.monotonic() - start
            )
        except Exception as exc:
            return self._error_result("simplify", str(exc), time.monotonic() - start)

    def solve(self, expression: str, *, variable: str = "x") -> dict[str, Any]:
        start = time.monotonic()
        try:
            sp = _import_sympy()
            var = sp.Symbol(variable)
            expr = self._parse_expr(sp, expression, variable)
            result = sp.solve(expr, var)
            return self._build_result(
                "solve", str(result), sp.latex(result), time.monotonic() - start
            )
        except Exception as exc:
            return self._error_result("solve", str(exc), time.monotonic() - start)

    def series(
        self,
        expression: str,
        *,
        variable: str = "x",
        point: int = 0,
        order: int = 6,
    ) -> dict[str, Any]:
        start = time.monotonic()
        try:
            sp = _import_sympy()
            var = sp.Symbol(variable)
            expr = self._parse_expr(sp, expression, variable)
            result = sp.series(expr, var, point, order)
            return self._build_result(
                "series", str(result), sp.latex(result), time.monotonic() - start
            )
        except Exception as exc:
            return self._error_result("series", str(exc), time.monotonic() - start)

    def factor(self, expression: str, *, variable: str = "x") -> dict[str, Any]:
        start = time.monotonic()
        try:
            sp = _import_sympy()
            expr = self._parse_expr(sp, expression, variable)
            result = sp.factor(expr)
            return self._build_result(
                "factor", str(result), sp.latex(result), time.monotonic() - start
            )
        except Exception as exc:
            return self._error_result("factor", str(exc), time.monotonic() - start)

    def integrate(self, expression: str, *, variable: str = "x") -> dict[str, Any]:
        start = time.monotonic()
        try:
            sp = _import_sympy()
            var = sp.Symbol(variable)
            expr = self._parse_expr(sp, expression, variable)
            result = sp.integrate(expr, var)
            return self._build_result(
                "integrate", str(result), sp.latex(result), time.monotonic() - start
            )
        except Exception as exc:
            return self._error_result("integrate", str(exc), time.monotonic() - start)

    def differentiate(self, expression: str, *, variable: str = "x") -> dict[str, Any]:
        start = time.monotonic()
        try:
            sp = _import_sympy()
            var = sp.Symbol(variable)
            expr = self._parse_expr(sp, expression, variable)
            result = sp.diff(expr, var)
            return self._build_result(
                "differentiate", str(result), sp.latex(result), time.monotonic() - start
            )
        except Exception as exc:
            return self._error_result("differentiate", str(exc), time.monotonic() - start)

    def evaluate(self, expression: str, *, precision: int = 15) -> dict[str, Any]:
        start = time.monotonic()
        try:
            sp = _import_sympy()
            expr = sp.sympify(expression)
            result = sp.N(expr, precision)
            return self._build_result(
                "evaluate", str(result), sp.latex(result), time.monotonic() - start
            )
        except Exception as exc:
            return self._error_result("evaluate", str(exc), time.monotonic() - start)

    def custom(self, code: str) -> dict[str, Any]:
        """Execute arbitrary SymPy code in a restricted namespace."""
        start = time.monotonic()

        sec_error = _check_spec_security(code)
        if sec_error:
            return self._error_result("custom", sec_error, time.monotonic() - start)

        try:
            sp = _import_sympy()
            namespace: dict[str, Any] = {"result": None}
            # Populate with SymPy public symbols
            for name in dir(sp):
                obj = getattr(sp, name)
                if callable(obj) or isinstance(obj, type):
                    namespace[name] = obj

            exec(code, {"__builtins__": {}}, namespace)  # noqa: S102 — sandboxed

            result_val = namespace.get("result")
            result_str = str(result_val) if result_val is not None else "None"
            try:
                latex_str = sp.latex(result_val) if result_val is not None else None
            except Exception:
                latex_str = None

            return self._build_result("custom", result_str, latex_str, time.monotonic() - start)
        except Exception as exc:
            return self._error_result("custom", str(exc), time.monotonic() - start)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omega-cas",
        description="OMEGA CAS (Computer Algebra System) execution adapter.",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    s = sub.add_parser("simplify", help="Simplify an expression")
    s.add_argument("expression")
    s.add_argument("--variable", default="x")

    sv = sub.add_parser("solve", help="Solve an equation")
    sv.add_argument("expression")
    sv.add_argument("--variable", default="x")

    sr = sub.add_parser("series", help="Series expansion")
    sr.add_argument("expression")
    sr.add_argument("--variable", default="x")
    sr.add_argument("--point", type=int, default=0)
    sr.add_argument("--order", type=int, default=6)

    f = sub.add_parser("factor", help="Factor expression")
    f.add_argument("expression")
    f.add_argument("--variable", default="x")

    i = sub.add_parser("integrate", help="Integrate expression")
    i.add_argument("expression")
    i.add_argument("--variable", default="x")

    d = sub.add_parser("differentiate", help="Differentiate expression")
    d.add_argument("expression")
    d.add_argument("--variable", default="x")

    e = sub.add_parser("evaluate", help="Numerical evaluation")
    e.add_argument("expression")
    e.add_argument("--precision", type=int, default=15)

    c = sub.add_parser("custom", help="Custom SymPy code")
    c.add_argument("code")

    args = parser.parse_args()
    adapter = CASAdapter()

    if args.action == "simplify":
        result = adapter.simplify(args.expression, variable=args.variable)
    elif args.action == "solve":
        result = adapter.solve(args.expression, variable=args.variable)
    elif args.action == "series":
        result = adapter.series(args.expression, variable=args.variable,
                                point=args.point, order=args.order)
    elif args.action == "factor":
        result = adapter.factor(args.expression, variable=args.variable)
    elif args.action == "integrate":
        result = adapter.integrate(args.expression, variable=args.variable)
    elif args.action == "differentiate":
        result = adapter.differentiate(args.expression, variable=args.variable)
    elif args.action == "evaluate":
        result = adapter.evaluate(args.expression, precision=args.precision)
    elif args.action == "custom":
        result = adapter.custom(args.code)
    else:
        parser.error(f"Unknown action: {args.action}")
        return

    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))


if __name__ == "__main__":
    main()
