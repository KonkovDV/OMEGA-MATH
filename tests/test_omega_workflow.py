#!/usr/bin/env python3
"""Unit tests for the OMEGA deterministic workflow controller."""

from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from omega_workflow import advance_workflow_state, initialize_workflow_state, load_workflow_state  # type: ignore


def _write_yaml(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


class OmegaWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent / "_test_workflow_workspace"
        if self.repo_root.exists():
            shutil.rmtree(self.repo_root)

        (self.repo_root / "registry" / "domains").mkdir(parents=True)
        (self.repo_root / "research" / "active").mkdir(parents=True)
        _write_yaml(
            self.repo_root / "agents" / "team.yaml",
            {
                "orchestration": {
                    "routing_rules": {
                        "T1-computational": "experimentalist",
                        "T2-experimental": "experimentalist",
                        "T3-pattern": "analyst",
                        "T4-structural": "prover",
                        "T5-foundational": "librarian",
                    }
                }
            },
        )
        _write_yaml(self.repo_root / "registry" / "triage-matrix.yaml", {"tier_1_computational": [], "tier_4_structural": []})

    def tearDown(self) -> None:
        if self.repo_root.exists():
            shutil.rmtree(self.repo_root)

    def _create_workspace(self, problem_id: str, title: str) -> None:
        problem_root = self.repo_root / "research" / "active" / problem_id
        (problem_root / "control").mkdir(parents=True, exist_ok=True)
        (problem_root / "README.md").write_text(f"# {title}\n", encoding="utf-8")

    def _write_domain_problem(self, filename: str, payload: dict[str, object]) -> None:
        _write_yaml(self.repo_root / "registry" / "domains" / filename, {"problems": [payload]})

    def test_triage_creates_experiment_first_state_for_t1(self) -> None:
        self._create_workspace("kobon-triangles", "Kobon triangles")
        self._write_domain_problem(
            "geometry.yaml",
            {
                "id": "kobon-triangles",
                "name": "Kobon triangles",
                "status": "open",
                "statement": "Maximize triangles from n lines.",
                "ai_triage": {"tier": "T1-computational", "amenability_score": 8},
            },
        )
        _write_yaml(
            self.repo_root / "registry" / "triage-matrix.yaml",
            {
                "tier_1_computational": [
                    {"id": "kobon-triangles", "name": "Kobon triangles", "score": 8, "domain": "geometry", "approach": "search + SAT", "compute": "moderate"}
                ]
            },
        )

        state = initialize_workflow_state(self.repo_root, "kobon-triangles")

        self.assertEqual(state["active_route"], "experiment-first")
        self.assertEqual(state["execution_role"], "experimentalist")
        self.assertEqual(state["current_stage"], "brief")
        self.assertEqual(state["current_owner"], "planner")
        self.assertIn("experiment", state["stages"])

    def test_triage_creates_proof_first_state_for_t4(self) -> None:
        self._create_workspace("birch-swinnerton-dyer", "Birch and Swinnerton-Dyer")
        self._write_domain_problem(
            "number-theory.yaml",
            {
                "id": "birch-swinnerton-dyer",
                "name": "Birch and Swinnerton-Dyer",
                "status": "open",
                "statement": "Relates rank and L-function behavior.",
                "ai_triage": {"tier": "T4-structural", "amenability_score": 2},
            },
        )

        state = initialize_workflow_state(self.repo_root, "birch-swinnerton-dyer")

        self.assertEqual(state["active_route"], "proof-first")
        self.assertEqual(state["execution_role"], "prover")
        self.assertIn("prove", state["stages"])

    def test_untriaged_defaults_to_survey_first(self) -> None:
        self._create_workspace("odd-perfect-numbers", "Odd perfect numbers")
        self._write_domain_problem(
            "number-theory.yaml",
            {
                "id": "odd-perfect-numbers",
                "name": "Odd perfect numbers",
                "status": "open",
                "statement": "Do odd perfect numbers exist?",
            },
        )

        state = initialize_workflow_state(self.repo_root, "odd-perfect-numbers")

        self.assertEqual(state["tier"], "untriaged")
        self.assertEqual(state["active_route"], "survey-first")
        self.assertEqual(state["execution_role"], "librarian")

    def test_advance_complete_moves_to_next_stage(self) -> None:
        self._create_workspace("kobon-triangles", "Kobon triangles")
        self._write_domain_problem(
            "geometry.yaml",
            {
                "id": "kobon-triangles",
                "name": "Kobon triangles",
                "status": "open",
                "statement": "Maximize triangles from n lines.",
                "ai_triage": {"tier": "T1-computational", "amenability_score": 8},
            },
        )

        initialize_workflow_state(self.repo_root, "kobon-triangles")
        state = advance_workflow_state(self.repo_root, "kobon-triangles", outcome="complete")

        self.assertEqual(state["current_stage"], "novelty")
        self.assertEqual(state["current_owner"], "librarian")
        self.assertEqual(state["stage_status"], "ready")
        self.assertEqual(state["history"][-1]["event"], "completed")

    def test_block_and_resume_keep_same_stage(self) -> None:
        self._create_workspace("kobon-triangles", "Kobon triangles")
        self._write_domain_problem(
            "geometry.yaml",
            {
                "id": "kobon-triangles",
                "name": "Kobon triangles",
                "status": "open",
                "statement": "Maximize triangles from n lines.",
                "ai_triage": {"tier": "T1-computational", "amenability_score": 8},
            },
        )

        initialize_workflow_state(self.repo_root, "kobon-triangles")
        blocked = advance_workflow_state(self.repo_root, "kobon-triangles", outcome="block", notes="waiting for literature packet")
        resumed = advance_workflow_state(self.repo_root, "kobon-triangles", outcome="resume")

        self.assertEqual(blocked["current_stage"], "brief")
        self.assertEqual(blocked["stage_status"], "blocked")
        self.assertEqual(resumed["current_stage"], "brief")
        self.assertEqual(resumed["stage_status"], "ready")

    def test_transition_validation(self) -> None:
        self._create_workspace("kobon-triangles", "Kobon triangles")
        self._write_domain_problem(
            "geometry.yaml",
            {
                "id": "kobon-triangles",
                "name": "Kobon triangles",
                "status": "open",
                "statement": "Maximize triangles from n lines.",
                "ai_triage": {"tier": "T1-computational", "amenability_score": 8},
            },
        )

        initialize_workflow_state(self.repo_root, "kobon-triangles")
        
        # Test blocking an already blocked state
        advance_workflow_state(self.repo_root, "kobon-triangles", outcome="block")
        with self.assertRaisesRegex(ValueError, "Cannot block: workflow is already blocked"):
            advance_workflow_state(self.repo_root, "kobon-triangles", outcome="block")
            
        # Test completing a blocked state
        with self.assertRaisesRegex(ValueError, "Cannot complete stage .* Must be resolved first"):
            advance_workflow_state(self.repo_root, "kobon-triangles", outcome="complete")
        
        # Resume
        advance_workflow_state(self.repo_root, "kobon-triangles", outcome="resume")
        
        # Test resuming a ready state
        with self.assertRaisesRegex(ValueError, "Cannot resume: current status is 'ready'"):
            advance_workflow_state(self.repo_root, "kobon-triangles", outcome="resume")

        # Close
        advance_workflow_state(self.repo_root, "kobon-triangles", outcome="close")
        
        # Test advancing closed state
        with self.assertRaisesRegex(ValueError, "Cannot advance: workflow is already closed"):
            advance_workflow_state(self.repo_root, "kobon-triangles", outcome="complete")

    def test_load_workflow_state_reads_written_file(self) -> None:
        self._create_workspace("kobon-triangles", "Kobon triangles")
        self._write_domain_problem(
            "geometry.yaml",
            {
                "id": "kobon-triangles",
                "name": "Kobon triangles",
                "status": "open",
                "statement": "Maximize triangles from n lines.",
                "ai_triage": {"tier": "T1-computational", "amenability_score": 8},
            },
        )

        initialize_workflow_state(self.repo_root, "kobon-triangles")
        state = load_workflow_state(self.repo_root, "kobon-triangles")

        self.assertEqual(state["problem_id"], "kobon-triangles")
        self.assertEqual(state["title"], "Kobon triangles")


if __name__ == "__main__":
    unittest.main()