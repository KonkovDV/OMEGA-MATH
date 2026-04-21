#!/usr/bin/env python3

import os
import sys
import json
import subprocess
from datetime import datetime, timezone

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        return {
            "passed": res.returncode == 0,
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
            "returncode": res.returncode
        }
    except Exception as e:
        return {
            "passed": False,
            "stderr": str(e),
            "stdout": "",
            "returncode": 1
        }

def main():
    print("Generating OMEGA runtime evidence report v1...")
    
    commands = [
        "omega-validate-registry",
        "omega-verify-version-sync",
        "python -m pytest -q",
        "omega-workflow status erdos-straus",
        "omega-orchestrate run erdos-straus --stage plan --dry-run"
    ]
    
    gates = {}
    for cmd in commands:
        cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"Running: {cmd}")
        res = run_cmd(f"cd {cwd} && {cmd}")
        gates[cmd] = {
            "passed": res["passed"],
            "details": res["stdout"] if res["passed"] else f"{res['stdout']}\n{res['stderr']}"
        }

    report = {
        "project": "OMEGA-MATH",
        "artifact_type": "runtime_evidence_report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "v1",
        "command_bundle": commands,
        "metrics": {
            "commands_passed": sum(1 for v in gates.values() if v["passed"]),
            "commands_total": len(commands)
        },
        "gates": gates,
        "implemented_vs_planned_note": {
            "implemented": ["workflow orchestration", "model routing", "registry validation", "CLI runner"],
            "planned": ["FT scaffold for SFT/DPO", "automated deployment"],
            "non_claims": ["No FT models deployed yet", "No production inference yet"]
        },
        "verification": {
            "tests": ["pytest -q"],
            "preflight": "not applicable (python space)",
            "status": "APPROVED" if all(v["passed"] for v in gates.values()) else "WARNING"
        }
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "omega_runtime_evidence_report_v1.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"Report written to {out_file}")
    
if __name__ == "__main__":
    main()
