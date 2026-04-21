#!/usr/bin/env python3
"""Create a Denario-compatible OMEGA research workspace for one problem.

Usage:
    python scripts/scaffold_problem.py riemann-hypothesis --title "Riemann hypothesis"
    python scripts/scaffold_problem.py odd-perfect-numbers --title "Odd perfect numbers" --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIVE_RESEARCH_DIR = REPO_ROOT / "research" / "active"


def normalize_problem_id(raw: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", raw.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        raise ValueError("problem id must contain at least one ASCII letter or digit")
    return slug


def render_templates(problem_id: str, title: str) -> dict[str, str]:
    return {
        "README.md": f"# {title}\n\nRegistry ID: `{problem_id}`\n\nStatus: active\n",
        "input_files/data_description.md": (
            f"# Problem Brief\n\n"
            f"- Registry ID: {problem_id}\n"
            f"- Title: {title}\n"
            f"- Tier: TBD\n"
            f"- Route: experiment-first | proof-first | survey-first\n\n"
            "## Problem Statement\n\n"
            "[Write the precise mathematical problem statement here.]\n\n"
            "## Success Condition\n\n"
            "[Define the bounded goal for this run.]\n\n"
            "## Stop Conditions\n\n"
            "- budget exhausted\n"
            "- no novelty after literature review\n"
            "- result is only numerical evidence without publishable delta\n"
        ),
        "input_files/literature.md": (
            "# Literature Packet\n\n"
            "## Seed Papers\n\n"
            "## Known Results\n\n"
            "## Best Current Bounds\n\n"
            "## Supporting Evidence\n\n"
            "## Contrasting Evidence\n\n"
            "## Collision Check\n\n"
            "## Risks\n"
        ),
        "input_files/literature_graph.md": (
            "# Literature Graph\n\n"
            "## Core Nodes\n\n"
            "## Bridge Papers\n\n"
            "## Missing Links\n\n"
            "## Update Notes\n"
        ),
        "input_files/citation_evidence.md": (
            "# Citation Evidence\n\n"
            "## Supporting Citations\n\n"
            "## Contrasting Citations\n\n"
            "## Novelty Risk\n\n"
            "## Follow-Up Reads\n"
        ),
        "input_files/idea.md": "# Research Idea\n\n## Main Hypothesis\n\n## Why This Route\n\n## Assumptions\n",
        "input_files/methods.md": "# Methods\n\n## Plan\n\n## Compute / Proof Stack\n\n## Validation Strategy\n",
        "input_files/proof_obligations.md": (
            "# Proof Obligations\n\n"
            "## Load-Bearing Claims\n\n"
            "## Branch / Sign / Endpoint Checks\n\n"
            "## Mechanizable Substeps\n\n"
            "## Independent Patch Search\n\n"
            "## Deferred Risks\n"
        ),
        "input_files/synthetic_taxonomy.md": (
            "# Synthetic Reasoning Taxonomy\n\n"
            "> Replace this stub with `templates/synthetic-reasoning-taxonomy.md` before claiming a synthetic reasoning or benchmark-generation result.\n\n"
            f"- Registry ID: {problem_id}\n"
            f"- Problem name: {title}\n"
            "- Asset family: pending\n"
            "- Status: inactive until synthetic lane is explicitly used\n"
        ),
        "input_files/synthetic_evaluation_packet.md": (
            "# Synthetic Evaluation Packet\n\n"
            "> Replace this stub with `templates/synthetic-evaluation-packet.md` when synthetic reasoning assets are actually evaluated.\n\n"
            f"- Registry ID: {problem_id}\n"
            f"- Problem name: {title}\n"
            "- Taxonomy path: input_files/synthetic_taxonomy.md\n"
            "- Status: pending first synthetic run\n"
        ),
        "input_files/statement_spec.md": (
            "# Statement Specification\n\n"
            "## Claim Label\n\n"
            "## Formal Statement Draft\n\n"
            "## Assumptions\n\n"
            "## Acceptance Rule\n"
            "- the proof output must close against this statement without assumption drift\n"
        ),
        "input_files/results.md": "# Results\n\n## Executed Steps\n\n## Findings\n\n## Negative Results\n\n## Limitations\n",
        "input_files/referee.md": "# Referee Report\n\n## Blocking Issues\n\n## Warnings\n\n## Publication Recommendation\n",
        "artifacts/run-manifest.yaml": (
            f"problem_id: {problem_id}\n"
            f"title: {title}\n"
            "status: draft\n"
            "route: tbd\n"
            "evidence_class: tbd\n"
            "reproducibility: pending\n"
            "workflow_state: control/workflow-state.yaml\n"
            "literature_graph: input_files/literature_graph.md\n"
            "citation_evidence: input_files/citation_evidence.md\n"
            "proof_obligations: input_files/proof_obligations.md\n"
            "synthetic_taxonomy: input_files/synthetic_taxonomy.md\n"
            "synthetic_evaluation_packet: input_files/synthetic_evaluation_packet.md\n"
            "statement_spec: input_files/statement_spec.md\n"
            "experiment_ledger: experiments/ledger.yaml\n"
            "evidence_bundle: artifacts/evidence-bundle.yaml\n"
            "prover_results_dir: artifacts/prover-results/\n"
            "failure_channel: control/failure-patterns.jsonl\n"
            "lean_starter_template: templates/lean-starter/\n"
            "presentation_pack: presentation/\n"
        ),
        "reproducibility.md": (
            "# Reproducibility Manifest\n\n"
            "> Replace this stub with `templates/reproducibility-manifest.md` before claiming a completed result.\n\n"
            f"- Registry ID: {problem_id}\n"
            f"- Problem name: {title}\n"
            "- Ledger path: experiments/ledger.yaml\n"
            "- Evidence bundle path: artifacts/evidence-bundle.yaml\n"
            "- Prover results path: artifacts/prover-results/\n"
            "- Status: pending first completed run\n"
        ),
        "artifacts/evidence-bundle.yaml": (
            "version: \"1.0\"\n"
            "generated_at: null\n"
            f"problem_id: {problem_id}\n"
            "bundle_path: artifacts/evidence-bundle.yaml\n"
            "summary:\n"
            "  total_runs: 0\n"
            "  total_artifacts: 0\n"
            "  total_bytes: 0\n"
            "  by_type: {}\n"
            "documents: []\n"
            "runs: []\n"
        ),
        "experiments/ledger.yaml": (
            "# Append run records following protocol/experiment-ledger-spec.md\n"
            "[]\n"
        ),
        "control/failure-patterns.jsonl": "",
        "artifacts/prover-results/.gitkeep": "",
        "planning/.gitkeep": "",
        "control/.gitkeep": "",
        "paper/.gitkeep": "",
        "presentation/.gitkeep": "",
        "input_files/plots/.gitkeep": "",
    }


def write_workspace(root: Path, templates: dict[str, str], force: bool, dry_run: bool) -> None:
    for relative_path, content in templates.items():
        target = root / relative_path
        if target.exists() and not force:
            raise FileExistsError(f"{target} already exists; pass --force to overwrite")
        if dry_run:
            print(target)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Denario-compatible OMEGA problem workspace")
    parser.add_argument("problem_id", help="registry id or slug for the problem workspace")
    parser.add_argument("--title", required=True, help="human-readable problem title")
    parser.add_argument("--force", action="store_true", help="overwrite existing files in the target workspace")
    parser.add_argument("--dry-run", action="store_true", help="print the files that would be created without writing them")
    args = parser.parse_args(argv)

    problem_id = normalize_problem_id(args.problem_id)
    workspace_root = ACTIVE_RESEARCH_DIR / problem_id
    templates = render_templates(problem_id, args.title.strip())

    try:
        write_workspace(workspace_root, templates, force=args.force, dry_run=args.dry_run)
    except (FileExistsError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Dry run complete for {workspace_root}")
    else:
        print(f"Created OMEGA workspace at {workspace_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())