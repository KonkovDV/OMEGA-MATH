#!/usr/bin/env python3
"""OMEGA SAT/SMT solver execution adapter.

Wraps Z3 (SMT/optimization) and a built-in DPLL SAT solver. Optionally uses PySAT
when installed. See protocol/solver-execution-adapter.md for the full contract.

Usage:
  python scripts/solver_adapter.py smt "x = Int('x'); solver.add(x > 5)"
  python scripts/solver_adapter.py sat --clauses "[[1,2],[-1,3]]" --num-vars 3
  python scripts/solver_adapter.py optimize "x = Int('x'); solver.add(x >= 1); solver.minimize(x)"
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import time
from typing import Any

import yaml

# Security: forbidden patterns in Z3 spec strings
_FORBIDDEN_PATTERNS = re.compile(
    r"\b(import|exec|eval|compile|open|__import__|getattr|setattr|delattr|globals|locals|vars"
    r"|os\.|sys\.|subprocess|shutil|pathlib|socket|http|urllib)\b"
)


def _check_spec_security(spec: str) -> str | None:
    """Return an error message if the spec contains forbidden patterns, else None."""
    m = _FORBIDDEN_PATTERNS.search(spec)
    if m:
        return f"Forbidden pattern in spec: {m.group()!r}"
    return None


# ---------- Built-in DPLL SAT solver (no external deps) ----------

def _dpll_solve(num_vars: int, clauses: list[list[int]]) -> tuple[bool, dict[str, Any]]:
    """Minimal DPLL SAT solver for small instances (no PySAT dependency)."""
    if not clauses:
        return True, {}

    assignment: dict[int, bool] = {}

    def evaluate() -> bool | None:
        """Returns True if all clauses satisfied, False if any falsified, None if undetermined."""
        all_sat = True
        for clause in clauses:
            clause_sat = False
            clause_falsified = True
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    val = assignment[var] if lit > 0 else not assignment[var]
                    if val:
                        clause_sat = True
                        break
                else:
                    clause_falsified = False
            if not clause_sat:
                if clause_falsified:
                    return False
                all_sat = False
        return True if all_sat else None

    def unit_propagate() -> bool:
        """Apply unit propagation. Returns False if conflict detected."""
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                unassigned = []
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    if var in assignment:
                        val = assignment[var] if lit > 0 else not assignment[var]
                        if val:
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:
                    return False  # conflict
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    var = abs(lit)
                    assignment[var] = lit > 0
                    changed = True
        return True

    def solve() -> bool:
        if not unit_propagate():
            return False
        result = evaluate()
        if result is True:
            return True
        if result is False:
            return False

        # Pick an unassigned variable
        for v in range(1, num_vars + 1):
            if v not in assignment:
                # Try True
                assignment[v] = True
                saved = dict(assignment)
                if solve():
                    return True
                assignment.clear()
                assignment.update(saved)
                del assignment[v]

                # Try False
                assignment[v] = False
                saved = dict(assignment)
                if solve():
                    return True
                assignment.clear()
                assignment.update(saved)
                del assignment[v]
                return False
        return True

    sat = solve()
    model = {f"x{v}": assignment.get(v, False) for v in range(1, num_vars + 1)} if sat else {}
    return sat, model


class SolverAdapter:
    """Execution adapter for SAT/SMT solving."""

    def get_runtime_capabilities(self) -> dict[str, Any]:
        """Return machine-readable solver backend capability status."""
        has_z3 = importlib.util.find_spec("z3") is not None
        has_pysat = importlib.util.find_spec("pysat") is not None
        return {
            "z3_available": has_z3,
            "pysat_available": has_pysat,
            "sat_backend_default": "pysat" if has_pysat else "pysat-builtin",
            "smt_backend_default": "z3",
        }

    def solve_smt(
        self,
        spec: str,
        *,
        timeout_seconds: int = 60,
    ) -> dict[str, Any]:
        """Execute a Z3 SMT spec and return structured result."""
        return self._run_z3(spec, mode="smt", timeout_seconds=timeout_seconds)

    def solve_optimize(
        self,
        spec: str,
        *,
        timeout_seconds: int = 60,
    ) -> dict[str, Any]:
        """Execute a Z3 optimization spec and return structured result."""
        return self._run_z3(spec, mode="optimize", timeout_seconds=timeout_seconds)

    def solve_sat(
        self,
        num_vars: int,
        clauses: list[list[int]],
        *,
        timeout_seconds: int = 60,
    ) -> dict[str, Any]:
        """Solve a SAT problem given DIMACS-style clauses. Uses PySAT if available, else built-in DPLL."""
        start = time.monotonic()
        try:
            # Try PySAT first
            try:
                from pysat.solvers import Solver as PySATSolver  # type: ignore[import-untyped]
                backend = "pysat"
                if not clauses:
                    return self._sat_result(True, {}, backend, time.monotonic() - start)
                with PySATSolver(name="g4", bootstrap_with=clauses) as s:
                    sat = s.solve()
                    model_raw = s.get_model() if sat else []
                model = {f"x{abs(lit)}": lit > 0 for lit in (model_raw or [])}
                return self._sat_result(sat, model, backend, time.monotonic() - start)
            except ImportError:
                # Fall back to built-in DPLL
                backend = "pysat-builtin"
                sat, model = _dpll_solve(num_vars, clauses)
                return self._sat_result(sat, model, backend, time.monotonic() - start)
        except Exception as exc:
            return {
                "success": False,
                "backend": "pysat-builtin",
                "mode": "sat",
                "satisfiable": None,
                "model": {},
                "objective": None,
                "duration_seconds": round(time.monotonic() - start, 3),
                "error": str(exc),
            }

    def _sat_result(
        self, sat: bool, model: dict[str, Any], backend: str, duration: float
    ) -> dict[str, Any]:
        return {
            "success": True,
            "backend": backend,
            "mode": "sat",
            "satisfiable": sat,
            "model": model,
            "objective": None,
            "duration_seconds": round(duration, 3),
            "error": None,
        }

    def _run_z3(
        self,
        spec: str,
        *,
        mode: str,
        timeout_seconds: int = 60,
    ) -> dict[str, Any]:
        """Run a Z3 spec string in a sandboxed namespace."""
        start = time.monotonic()

        # Security check
        sec_error = _check_spec_security(spec)
        if sec_error:
            return {
                "success": False,
                "backend": "z3",
                "mode": mode,
                "satisfiable": None,
                "model": {},
                "objective": None,
                "duration_seconds": round(time.monotonic() - start, 3),
                "error": sec_error,
            }

        try:
            import z3  # type: ignore[import-untyped]
        except ImportError:
            return {
                "success": False,
                "backend": "z3",
                "mode": mode,
                "satisfiable": None,
                "model": {},
                "objective": None,
                "duration_seconds": round(time.monotonic() - start, 3),
                "error": "z3-solver package not installed. Install with: pip install z3-solver",
            }

        try:
            is_optimize = mode == "optimize"
            solver = z3.Optimize() if is_optimize else z3.Solver()
            solver.set("timeout", timeout_seconds * 1000)

            # Build restricted namespace with Z3 symbols
            namespace: dict[str, Any] = {"solver": solver}
            for name in dir(z3):
                obj = getattr(z3, name)
                if callable(obj) or isinstance(obj, type):
                    namespace[name] = obj

            exec(spec, {"__builtins__": {}}, namespace)  # noqa: S102 — sandboxed

            result = solver.check()
            duration = round(time.monotonic() - start, 3)

            if result == z3.sat:
                m = solver.model()
                model_dict: dict[str, Any] = {}
                for d in m.decls():
                    val = m[d]
                    # Convert Z3 values to Python
                    if z3.is_int_value(val):
                        model_dict[d.name()] = val.as_long()
                    elif z3.is_rational_value(val):
                        model_dict[d.name()] = float(val.as_fraction())
                    elif z3.is_true(val):
                        model_dict[d.name()] = True
                    elif z3.is_false(val):
                        model_dict[d.name()] = False
                    else:
                        model_dict[d.name()] = str(val)

                objective_val = None
                if is_optimize:
                    objs = solver.objectives()
                    if objs:
                        try:
                            obj_val = m.eval(objs[0])
                            if z3.is_int_value(obj_val):
                                objective_val = obj_val.as_long()
                            elif z3.is_rational_value(obj_val):
                                objective_val = float(obj_val.as_fraction())
                        except Exception:
                            pass

                return {
                    "success": True,
                    "backend": "z3",
                    "mode": mode,
                    "satisfiable": True,
                    "model": model_dict,
                    "objective": objective_val,
                    "duration_seconds": duration,
                    "error": None,
                }
            elif result == z3.unsat:
                return {
                    "success": True,
                    "backend": "z3",
                    "mode": mode,
                    "satisfiable": False,
                    "model": {},
                    "objective": None,
                    "duration_seconds": duration,
                    "error": None,
                }
            else:
                return {
                    "success": True,
                    "backend": "z3",
                    "mode": mode,
                    "satisfiable": None,
                    "model": {},
                    "objective": None,
                    "duration_seconds": duration,
                    "error": "Solver returned unknown (timeout or incomplete)",
                }

        except Exception as exc:
            return {
                "success": False,
                "backend": "z3",
                "mode": mode,
                "satisfiable": None,
                "model": {},
                "objective": None,
                "duration_seconds": round(time.monotonic() - start, 3),
                "error": str(exc),
            }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omega-solve",
        description="OMEGA SAT/SMT solver execution adapter.",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    smt_p = sub.add_parser("smt", help="Solve an SMT problem with Z3")
    smt_p.add_argument("spec", help="Z3 Python spec string")
    smt_p.add_argument("--timeout", type=int, default=60)

    opt_p = sub.add_parser("optimize", help="Solve an optimization problem with Z3")
    opt_p.add_argument("spec", help="Z3 Python spec string")
    opt_p.add_argument("--timeout", type=int, default=60)

    sat_p = sub.add_parser("sat", help="Solve a SAT problem")
    sat_p.add_argument("--clauses", required=True, help="JSON list of clauses")
    sat_p.add_argument("--num-vars", type=int, required=True, help="Number of variables")
    sat_p.add_argument("--timeout", type=int, default=60)

    args = parser.parse_args()
    adapter = SolverAdapter()

    if args.mode == "smt":
        result = adapter.solve_smt(args.spec, timeout_seconds=args.timeout)
    elif args.mode == "optimize":
        result = adapter.solve_optimize(args.spec, timeout_seconds=args.timeout)
    elif args.mode == "sat":
        clauses = json.loads(args.clauses)
        result = adapter.solve_sat(args.num_vars, clauses, timeout_seconds=args.timeout)
    else:
        parser.error(f"Unknown mode: {args.mode}")
        return

    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))


if __name__ == "__main__":
    main()
