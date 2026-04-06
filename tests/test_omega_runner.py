#!/usr/bin/env python3
"""Unit tests for the OMEGA local runner substrate."""

from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from omega_runner import (  # type: ignore  # RED phase: module added after tests
    bootstrap_lean_starter,
    create_proof_result,
    finish_run,
    generate_evidence_bundle,
    generate_experiment_index,
    start_run,
)
from omega_workflow import load_workflow_state  # type: ignore


class OmegaRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent / "_test_workspace"
        if self.repo_root.exists():
            shutil.rmtree(self.repo_root)

        (self.repo_root / "research" / "active").mkdir(parents=True)
        (self.repo_root / "templates" / "lean-starter" / "OmegaWorkbench").mkdir(parents=True)

        (self.repo_root / "templates" / "lean-starter" / "README.md").write_text(
            "# Lean starter\n",
            encoding="utf-8",
        )
        (self.repo_root / "templates" / "lean-starter" / "lean-toolchain").write_text(
            "leanprover/lean4:v4.29.0\n",
            encoding="utf-8",
        )
        (self.repo_root / "templates" / "lean-starter" / "lakefile.lean").write_text(
            "import Lake\n",
            encoding="utf-8",
        )
        (self.repo_root / "templates" / "lean-starter" / "OmegaWorkbench" / "Test.lean").write_text(
            "theorem demo : True := by trivial\n",
            encoding="utf-8",
        )

        self.problem_id = "test-problem"
        self.problem_root = self.repo_root / "research" / "active" / self.problem_id
        self.problem_root.mkdir(parents=True)
        (self.problem_root / "README.md").write_text(
            "# Test Problem\n",
            encoding="utf-8",
        )
        (self.problem_root / "reproducibility.md").write_text(
            "# Reproducibility\n",
            encoding="utf-8",
        )
        (self.problem_root / "input_files").mkdir(parents=True)
        (self.problem_root / "input_files" / "proof_obligations.md").write_text(
            "# Proof Obligations\n\n## Load-Bearing Claims\n\n- obligation\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        if self.repo_root.exists():
            shutil.rmtree(self.repo_root)

    def _ledger_path(self) -> Path:
        return self.problem_root / "experiments" / "ledger.yaml"

    def _load_ledger(self) -> list[dict]:
        return yaml.safe_load(self._ledger_path().read_text(encoding="utf-8")) or []

    def _evidence_bundle_path(self) -> Path:
        return self.problem_root / "artifacts" / "evidence-bundle.yaml"

    def test_start_creates_running_run_and_global_index(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="bounded search",
        )

        self.assertRegex(run_id, rf"^{self.problem_id}-\d{{8}}-\d{{3}}$")

        ledger = self._load_ledger()
        self.assertEqual(len(ledger), 1)
        entry = ledger[0]
        self.assertEqual(entry["run_id"], run_id)
        self.assertEqual(entry["status"], "running")
        self.assertEqual(entry["route"], "experiment-first")
        self.assertEqual(entry["agent"], "experimentalist")
        self.assertEqual(entry["parameters"]["description"], "bounded search")
        self.assertIsNone(entry["finished"])

        index_path = self.repo_root / "research" / "active" / "experiment-index.yaml"
        self.assertTrue(index_path.exists())
        index = yaml.safe_load(index_path.read_text(encoding="utf-8")) or []
        self.assertEqual(index[0]["problem_id"], self.problem_id)
        self.assertEqual(index[0]["latest_run"], run_id)
        self.assertEqual(index[0]["total_runs"], 1)

    def test_start_allocates_next_sequence_number(self) -> None:
        first = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="first",
        )
        second = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="survey-first",
            agent="librarian",
            description="second",
        )

        self.assertTrue(first.endswith("-001"))
        self.assertTrue(second.endswith("-002"))

    def test_start_initializes_workflow_and_marks_execution_running(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="bounded search",
        )

        state = load_workflow_state(self.repo_root, self.problem_id)
        self.assertEqual(state["active_route"], "experiment-first")
        self.assertEqual(state["current_stage"], "experiment")
        self.assertEqual(state["stage_status"], "running")
        self.assertEqual(state["active_run_id"], run_id)
        self.assertEqual(state["last_run_status"], "running")

    def test_finish_updates_status_verdict_notes_and_artifacts(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="bounded search",
        )

        artifact_file = self.problem_root / "artifacts" / "search.log"
        artifact_file.parent.mkdir(parents=True)
        artifact_file.write_text("ok\n", encoding="utf-8")

        finish_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            run_id=run_id,
            status="completed",
            verdict="positive",
            artifacts=[{"path": "artifacts/search.log", "type": "log"}],
            notes="new upper bound",
        )

        entry = self._load_ledger()[0]
        self.assertEqual(entry["status"], "completed")
        self.assertEqual(entry["verdict"], "positive")
        self.assertEqual(entry["notes"], "new upper bound")
        self.assertEqual(entry["artifacts"][0]["path"], "artifacts/search.log")
        self.assertEqual(entry["artifacts"][0]["type"], "log")
        self.assertIsNotNone(entry["finished"])

    def test_finish_advances_workflow_to_results_and_clears_active_run(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="bounded search",
        )

        artifact_file = self.problem_root / "artifacts" / "search.log"
        artifact_file.parent.mkdir(parents=True)
        artifact_file.write_text("ok\n", encoding="utf-8")

        finish_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            run_id=run_id,
            status="completed",
            verdict="positive",
            artifacts=[{"path": "artifacts/search.log", "type": "log"}],
        )

        state = load_workflow_state(self.repo_root, self.problem_id)
        self.assertEqual(state["current_stage"], "results")
        self.assertEqual(state["current_owner"], "experimentalist")
        self.assertEqual(state["stage_status"], "ready")
        self.assertIsNone(state["active_run_id"])
        self.assertEqual(state["last_run_id"], run_id)
        self.assertEqual(state["last_verdict"], "positive")

    def test_finish_records_checksum_and_updates_evidence_bundle(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="bounded search",
        )

        artifact_file = self.problem_root / "artifacts" / "result.txt"
        artifact_file.parent.mkdir(parents=True)
        artifact_file.write_text("evidence\n", encoding="utf-8")

        finish_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            run_id=run_id,
            status="completed",
            verdict="positive",
            artifacts=[{"path": "artifacts/result.txt", "type": "log"}],
        )

        entry = self._load_ledger()[0]
        checksum = entry["artifacts"][0]["checksum"]
        self.assertRegex(checksum, r"^[a-f0-9]{64}$")

        bundle_path = self._evidence_bundle_path()
        self.assertTrue(bundle_path.exists())
        bundle = yaml.safe_load(bundle_path.read_text(encoding="utf-8"))
        self.assertEqual(bundle["problem_id"], self.problem_id)
        self.assertEqual(bundle["summary"]["total_runs"], 1)

    def test_finish_rejects_invalid_enums_and_absolute_artifact_paths(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="bounded search",
        )

        with self.assertRaises(ValueError):
            finish_run(
                repo_root=self.repo_root,
                problem_id=self.problem_id,
                run_id=run_id,
                status="invalid",
            )

        with self.assertRaises(ValueError):
            finish_run(
                repo_root=self.repo_root,
                problem_id=self.problem_id,
                run_id=run_id,
                status="completed",
                verdict="unknown",
            )

        with self.assertRaises(ValueError):
            finish_run(
                repo_root=self.repo_root,
                problem_id=self.problem_id,
                run_id=run_id,
                status="completed",
                artifacts=[{"path": str(self.problem_root / 'artifacts' / 'bad.log'), "type": "log"}],
            )

    def test_proof_result_writes_contract_and_links_ledger_artifact(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="proof-first",
            agent="prover",
            description="lemma search",
        )

        proof_file = self.problem_root / "artifacts" / "candidate.lean"
        proof_file.parent.mkdir(parents=True)
        proof_file.write_text("theorem candidate : True := by trivial\n", encoding="utf-8")

        proof_result_path = create_proof_result(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            run_id=run_id,
            claim_label="candidate theorem",
            claim_class="theorem",
            status="draft",
            verifier_kind="lean4",
            toolchain="leanprover/lean4:v4.29.0",
            command="lake env lean artifacts/candidate.lean",
            source_entry="artifacts/candidate.lean",
            artifacts=[{"path": "artifacts/candidate.lean", "type": "source"}],
        )

        self.assertEqual(
            proof_result_path,
            self.problem_root / "artifacts" / "prover-results" / f"{run_id}.yaml",
        )
        result = yaml.safe_load(proof_result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["run_id"], run_id)
        self.assertEqual(result["problem_id"], self.problem_id)
        self.assertEqual(result["ledger_run_id"], run_id)
        self.assertEqual(result["claim_class"], "theorem")
        self.assertEqual(result["verifier"]["kind"], "lean4")

        ledger_entry = self._load_ledger()[0]
        linked = [artifact for artifact in ledger_entry["artifacts"] if artifact["type"] == "prover-result"]
        self.assertEqual(len(linked), 1)
        self.assertEqual(linked[0]["path"], f"artifacts/prover-results/{run_id}.yaml")

        state = load_workflow_state(self.repo_root, self.problem_id)
        self.assertEqual(state["active_route"], "proof-first")
        self.assertEqual(state["current_stage"], "prove")
        self.assertEqual(state["last_proof_status"], "draft")
        self.assertEqual(state["last_proof_result_path"], f"artifacts/prover-results/{run_id}.yaml")

    def test_create_proof_result_requires_existing_proof_obligations(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="proof-first",
            agent="prover",
            description="lemma search",
        )

        proof_file = self.problem_root / "artifacts" / "candidate.lean"
        proof_file.parent.mkdir(parents=True)
        proof_file.write_text("theorem candidate : True := by trivial\n", encoding="utf-8")
        (self.problem_root / "input_files" / "proof_obligations.md").unlink()

        with self.assertRaises(FileNotFoundError):
            create_proof_result(
                repo_root=self.repo_root,
                problem_id=self.problem_id,
                run_id=run_id,
                claim_label="candidate theorem",
                claim_class="theorem",
                status="draft",
                verifier_kind="lean4",
                toolchain="leanprover/lean4:v4.29.0",
                command="lake env lean artifacts/candidate.lean",
                source_entry="artifacts/candidate.lean",
                artifacts=[{"path": "artifacts/candidate.lean", "type": "source"}],
            )

    def test_bootstrap_lean_copies_template_tree(self) -> None:
        target = bootstrap_lean_starter(repo_root=self.repo_root, problem_id=self.problem_id)

        self.assertEqual(target, self.problem_root / "proof" / "lean")
        self.assertTrue((target / "README.md").exists())
        self.assertTrue((target / "lean-toolchain").exists())
        self.assertTrue((target / "lakefile.lean").exists())
        self.assertTrue((target / "OmegaWorkbench" / "Test.lean").exists())

    def test_generate_experiment_index_aggregates_latest_run(self) -> None:
        other_problem = self.repo_root / "research" / "active" / "second-problem"
        other_problem.mkdir(parents=True)

        first_run = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="first",
        )
        second_run = start_run(
            repo_root=self.repo_root,
            problem_id="second-problem",
            route="survey-first",
            agent="librarian",
            description="survey",
        )

        finish_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            run_id=first_run,
            status="failed",
            verdict="negative",
        )

        index = generate_experiment_index(repo_root=self.repo_root)
        self.assertEqual(len(index), 2)

        first_entry = next(item for item in index if item["problem_id"] == self.problem_id)
        second_entry = next(item for item in index if item["problem_id"] == "second-problem")
        self.assertEqual(first_entry["latest_run"], first_run)
        self.assertEqual(first_entry["latest_verdict"], "negative")
        self.assertEqual(first_entry["total_runs"], 1)
        self.assertEqual(second_entry["latest_run"], second_run)
        self.assertIsNone(second_entry["latest_verdict"])

    def test_generate_experiment_index_includes_workflow_only_workspace(self) -> None:
        other_problem = self.repo_root / "research" / "active" / "survey-only"
        (other_problem / "control").mkdir(parents=True)
        (other_problem / "README.md").write_text("# Survey Only\n", encoding="utf-8")
        (other_problem / "control" / "workflow-state.yaml").write_text(
            yaml.safe_dump(
                {
                    "problem_id": "survey-only",
                    "title": "Survey Only",
                    "active_route": "survey-first",
                    "current_stage": "plan",
                    "current_owner": "planner",
                    "stage_status": "blocked",
                    "execution_role": "librarian",
                    "last_updated": "2026-03-01T12:00:00Z",
                    "stages": ["brief", "novelty", "triage", "plan", "survey", "results", "paper", "referee", "closed"],
                    "history": [],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        index = generate_experiment_index(repo_root=self.repo_root)
        entry = next(item for item in index if item["problem_id"] == "survey-only")
        self.assertEqual(entry["total_runs"], 0)
        self.assertTrue(entry["workflow_exists"])
        self.assertEqual(entry["current_stage"], "plan")
        self.assertTrue(entry["blocked"])

    def test_generate_evidence_bundle_is_stable_for_same_run(self) -> None:
        run_id = start_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            route="experiment-first",
            agent="experimentalist",
            description="bounded search",
        )

        artifact_file = self.problem_root / "artifacts" / "stable.txt"
        artifact_file.parent.mkdir(parents=True)
        artifact_file.write_text("stable evidence\n", encoding="utf-8")

        finish_run(
            repo_root=self.repo_root,
            problem_id=self.problem_id,
            run_id=run_id,
            status="completed",
            verdict="positive",
            artifacts=[{"path": "artifacts/stable.txt", "type": "log"}],
        )

        first_path = generate_evidence_bundle(repo_root=self.repo_root, problem_id=self.problem_id)
        first_bundle = yaml.safe_load(first_path.read_text(encoding="utf-8"))
        second_path = generate_evidence_bundle(repo_root=self.repo_root, problem_id=self.problem_id)
        second_bundle = yaml.safe_load(second_path.read_text(encoding="utf-8"))

        self.assertEqual(
            first_bundle["runs"][0]["artifacts"][0]["checksum"],
            second_bundle["runs"][0]["artifacts"][0]["checksum"],
        )


if __name__ == "__main__":
    unittest.main()