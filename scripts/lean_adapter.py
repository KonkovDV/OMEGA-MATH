#!/usr/bin/env python3
"""OMEGA Lean 4 execution adapter.

Wraps the Lean 4 CLI (lean, lake) and returns structured machine-readable results.
See protocol/lean-execution-adapter.md for the full contract.

Usage:
  python scripts/lean_adapter.py check-file path/to/File.lean
  python scripts/lean_adapter.py build-project path/to/lean-project/
  python scripts/lean_adapter.py run-command "lean --version"
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

# Regex for Lean 4 diagnostic lines: <file>:<line>:<col>: <severity>: <message>
_DIAG_RE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+):\s+(?P<severity>error|warning|info):\s+(?P<message>.*)$"
)


def parse_lean_diagnostics(output: str) -> list[dict[str, Any]]:
    """Parse Lean 4 diagnostic output into structured objects."""
    diagnostics: list[dict[str, Any]] = []
    for line in output.splitlines():
        m = _DIAG_RE.match(line)
        if m:
            diagnostics.append({
                "file": m.group("file"),
                "line": int(m.group("line")),
                "column": int(m.group("col")),
                "severity": m.group("severity"),
                "message": m.group("message"),
            })
        elif diagnostics:
            # Continuation of previous diagnostic message
            diagnostics[-1]["message"] += "\n" + line.rstrip()
    return diagnostics


class LeanAdapter:
    """Execution adapter for Lean 4 CLI interactions."""

    def __init__(
        self,
        lean_bin: str = "lean",
        lake_bin: str = "lake",
        sandbox_mode: str | None = None,
        sandbox_tool: str = "landrun",
    ) -> None:
        self._lean = lean_bin
        self._lake = lake_bin
        raw_mode = (sandbox_mode or os.environ.get("OMEGA_LEAN_SANDBOX", "auto")).strip().lower()
        if raw_mode not in {"off", "auto", "required"}:
            raise ValueError("sandbox_mode must be one of: off, auto, required")
        self._sandbox_mode = raw_mode
        self._sandbox_tool = sandbox_tool

    def _resolve_command(self, cmd: list[str]) -> tuple[list[str], dict[str, Any]]:
        sandbox_meta: dict[str, Any] = {
            "sandbox_mode": self._sandbox_mode,
            "sandbox_applied": False,
            "sandbox_tool": None,
        }

        if self._sandbox_mode == "off":
            return cmd, sandbox_meta

        tool_path = shutil.which(self._sandbox_tool)
        if tool_path:
            sandbox_meta.update({"sandbox_applied": True, "sandbox_tool": self._sandbox_tool})
            return [tool_path, "--", *cmd], sandbox_meta

        if self._sandbox_mode == "required":
            raise RuntimeError(
                f"Sandbox mode is 'required' but '{self._sandbox_tool}' is not available on PATH"
            )

        return cmd, sandbox_meta

    def _run(
        self,
        cmd: list[str],
        *,
        cwd: Path | None = None,
        timeout_seconds: int = 120,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run a subprocess and capture output."""
        start = time.monotonic()
        try:
            resolved_cmd, sandbox_meta = self._resolve_command(cmd)
            proc = subprocess.run(
                resolved_cmd,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=env,
            )
            duration = time.monotonic() - start
            return {
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "duration_seconds": round(duration, 3),
                "timed_out": False,
                **sandbox_meta,
            }
        except RuntimeError as exc:
            duration = time.monotonic() - start
            return {
                "exit_code": -2,
                "stdout": "",
                "stderr": str(exc),
                "duration_seconds": round(duration, 3),
                "timed_out": False,
                "sandbox_mode": self._sandbox_mode,
                "sandbox_applied": False,
                "sandbox_tool": None,
            }
        except subprocess.TimeoutExpired:
            duration = time.monotonic() - start
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "",
                "duration_seconds": round(duration, 3),
                "timed_out": True,
                "sandbox_mode": self._sandbox_mode,
                "sandbox_applied": False,
                "sandbox_tool": None,
            }
        except FileNotFoundError as exc:
            duration = time.monotonic() - start
            missing = resolved_cmd[0] if "resolved_cmd" in locals() and resolved_cmd else cmd[0]
            return {
                "exit_code": -3,
                "stdout": "",
                "stderr": (
                    f"Executable not found: '{missing}'. "
                    "Install Lean/Lake toolchain or pass explicit binary path. "
                    f"OS detail: {exc}"
                ),
                "duration_seconds": round(duration, 3),
                "timed_out": False,
                "sandbox_mode": self._sandbox_mode,
                "sandbox_applied": False,
                "sandbox_tool": None,
            }

    def _build_result(
        self,
        action: str,
        raw: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a LeanResult from raw subprocess output."""
        all_diags = parse_lean_diagnostics(raw["stderr"])
        errors = [d for d in all_diags if d["severity"] == "error"]
        warnings = [d for d in all_diags if d["severity"] == "warning"]

        if raw["timed_out"]:
            errors = [{"severity": "error", "message": f"Lean process timed out after {raw['duration_seconds']:.0f} seconds"}]

        return {
            "success": raw["exit_code"] == 0 and not errors,
            "action": action,
            "exit_code": raw["exit_code"],
            "stdout": raw["stdout"],
            "stderr": raw["stderr"],
            "duration_seconds": raw["duration_seconds"],
            "errors": errors,
            "warnings": warnings,
            "sandbox_mode": raw.get("sandbox_mode", "off"),
            "sandbox_applied": bool(raw.get("sandbox_applied", False)),
            "sandbox_tool": raw.get("sandbox_tool"),
        }

    def get_runtime_capabilities(self) -> dict[str, Any]:
        """Return machine-readable Lean/Lake runtime capability status."""
        lean_path = shutil.which(self._lean)
        lake_path = shutil.which(self._lake)
        sandbox_tool_path = (
            shutil.which(self._sandbox_tool) if self._sandbox_mode != "off" else None
        )
        return {
            "lean_available": lean_path is not None,
            "lake_available": lake_path is not None,
            "lean_executable": lean_path,
            "lake_executable": lake_path,
            "sandbox_mode": self._sandbox_mode,
            "sandbox_tool": self._sandbox_tool,
            "sandbox_tool_available": sandbox_tool_path is not None,
            "sandbox_tool_path": sandbox_tool_path,
        }

    def check_file(
        self,
        lean_file: Path,
        *,
        timeout_seconds: int = 120,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run `lean <file>` and return structured result."""
        raw = self._run(
            [self._lean, str(lean_file)],
            timeout_seconds=timeout_seconds,
            env=env,
        )
        return self._build_result("check-file", raw)

    def build_project(
        self,
        project_dir: Path,
        *,
        timeout_seconds: int = 300,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run `lake build` in a Lean project directory and return structured result."""
        raw = self._run(
            [self._lake, "build"],
            cwd=project_dir,
            timeout_seconds=timeout_seconds,
            env=env,
        )
        return self._build_result("build-project", raw)

    def run_command(
        self,
        command: str,
        *,
        cwd: Path | None = None,
        timeout_seconds: int = 120,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run an arbitrary lean/lake shell command and return structured result."""
        parts = shlex.split(command)
        raw = self._run(
            parts,
            cwd=cwd,
            timeout_seconds=timeout_seconds,
            env=env,
        )
        return self._build_result("run-command", raw)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omega-lean",
        description="OMEGA Lean 4 execution adapter.",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    check = sub.add_parser("check-file", help="Check a single Lean file")
    check.add_argument("file", type=Path, help="Path to .lean file")
    check.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")
    check.add_argument("--sandbox", choices=["off", "auto", "required"], default=None, help="Sandbox mode")

    build = sub.add_parser("build-project", help="Build a Lake project")
    build.add_argument("dir", type=Path, help="Path to Lake project root")
    build.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    build.add_argument("--sandbox", choices=["off", "auto", "required"], default=None, help="Sandbox mode")

    run = sub.add_parser("run-command", help="Run an arbitrary lean/lake command")
    run.add_argument("command", help="Command string to execute")
    run.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")
    run.add_argument("--sandbox", choices=["off", "auto", "required"], default=None, help="Sandbox mode")

    args = parser.parse_args()
    adapter = LeanAdapter(sandbox_mode=getattr(args, "sandbox", None))

    if args.action == "check-file":
        result = adapter.check_file(args.file, timeout_seconds=args.timeout)
    elif args.action == "build-project":
        result = adapter.build_project(args.dir, timeout_seconds=args.timeout)
    elif args.action == "run-command":
        result = adapter.run_command(args.command, timeout_seconds=args.timeout)
    else:
        parser.error(f"Unknown action: {args.action}")
        return

    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))


if __name__ == "__main__":
    main()
