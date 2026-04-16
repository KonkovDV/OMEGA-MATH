"""End-to-end integration test for the OMEGA pipeline.

Exercises the full path: scaffold → triage → context-assembly → agent-dispatch →
artifact-save → evidence-bundle → verify for a T1 (computational) problem.

All LLM calls are mocked — this test validates the pipeline plumbing, not the
LLM output quality.  Runs without network, API keys, or external tools.
"""

from __future__ import annotations

import hashlib
import textwrap
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import yaml


def _fake_invoke_llm(
    messages: list[dict[str, str]],
    *,
    model: str = "mock",
    max_tokens: int = 4000,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """Fake LLM invocation that returns a plausible structured response."""
    # Detect stage from user prompt
    user_msg = messages[-1]["content"] if messages else ""
    stage = "unknown"
    for candidate in ("brief", "novelty", "plan", "experiment", "results", "paper", "referee"):
        if f"Stage: {candidate}" in user_msg:
            stage = candidate
            break

    content = textwrap.dedent(f"""\
        # {stage.title()} Output

        This is a mock {stage} artifact produced by the test harness.
        The analysis determined that the problem is well-suited for computational attack.

        Key points:
        - Point 1: identified relevant parametric families
        - Point 2: coverage analysis shows 94% of residue classes handled
        - Point 3: remaining cases require targeted SAT search

        ```yaml
        artifact_type: {stage}-artifact
        evidence_class: E2
        confidence: C2
        summary: Mock {stage} artifact for integration testing
        key_findings:
          - Finding A from {stage}
          - Finding B from {stage}
        ```
    """)

    return {
        "content": content,
        "model": "mock-model-v1",
        "prompt_tokens": len(user_msg) // 4,
        "completion_tokens": len(content) // 4,
        "duration_seconds": 0.1,
    }


class EndToEndPipelineTest(unittest.TestCase):
    """Full pipeline integration test with mocked LLM."""

    def setUp(self) -> None:
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_root = Path(self._tmpdir.name)

        # Copy minimal registry and agent files into temp root
        import shutil

        real_root = Path(__file__).resolve().parent.parent

        # Copy agents/
        agents_src = real_root / "agents"
        agents_dst = self.tmp_root / "agents"
        if agents_src.exists():
            shutil.copytree(agents_src, agents_dst)

        # Copy registry/
        registry_src = real_root / "registry"
        registry_dst = self.tmp_root / "registry"
        if registry_src.exists():
            shutil.copytree(registry_src, registry_dst)

        # Create workspace for erdos-straus
        ws = self.tmp_root / "research" / "active" / "erdos-straus"
        (ws / "control").mkdir(parents=True)
        (ws / "experiments").mkdir(parents=True)
        (ws / "artifacts").mkdir(parents=True)
        (ws / "input_files").mkdir(parents=True)

        # Write minimal workflow state
        wf_state = {
            "current_stage": "triage",
            "current_owner": "planner",
            "active_route": "experiment-first",
            "history": [],
        }
        (ws / "control" / "workflow-state.yaml").write_text(
            yaml.safe_dump(wf_state, sort_keys=False), encoding="utf-8"
        )

        # Write minimal README
        (ws / "README.md").write_text(
            "# Erdős–Straus Conjecture\n\nFor every n ≥ 2, 4/n = 1/x + 1/y + 1/z.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    @patch("agent_orchestrator.invoke_llm", side_effect=_fake_invoke_llm)
    @patch("agent_orchestrator.REPO_ROOT")
    def test_full_pipeline_brief_to_results(self, mock_root: Any, mock_llm: Any) -> None:
        """Run brief → novelty → triage → plan → experiment → results with mocked LLM."""
        mock_root.__truediv__ = self.tmp_root.__truediv__
        mock_root.__str__ = self.tmp_root.__str__
        mock_root.exists = self.tmp_root.exists

        # Use the actual Path methods from tmp_root
        import agent_orchestrator
        original_root = agent_orchestrator.REPO_ROOT
        agent_orchestrator.REPO_ROOT = self.tmp_root

        try:
            from agent_orchestrator import run_pipeline

            result = run_pipeline(
                "erdos-straus",
                from_stage="brief",
                to_stage="results",
                model="mock",
            )

            # Pipeline should succeed
            self.assertTrue(result["success"], f"Pipeline failed: {result}")

            # Should run 6 stages: brief, novelty, triage, plan, experiment, results
            self.assertEqual(len(result["stages_run"]), 6)
            self.assertEqual(
                result["stages_run"],
                ["brief", "novelty", "triage", "plan", "experiment", "results"],
            )

            # All stage results should be successful
            for sr in result["stage_results"]:
                self.assertTrue(sr["success"], f"Stage failed: {sr}")
                self.assertIn("artifact_path", sr)
                self.assertIn("metadata", sr)
                self.assertIn("yaml_block", sr)

            # Artifacts should exist on disk
            artifacts_dir = self.tmp_root / "research" / "active" / "erdos-straus" / "artifacts"
            artifact_files = list(artifacts_dir.glob("*.md"))
            self.assertEqual(len(artifact_files), 6, f"Expected 6 artifacts, got {artifact_files}")

            # Manifest should have 5 entries with checksums
            manifest_path = artifacts_dir / "manifest.yaml"
            self.assertTrue(manifest_path.exists())
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["artifacts"]), 6)

            for entry in manifest["artifacts"]:
                self.assertIn("checksum_sha256", entry)
                self.assertEqual(len(entry["checksum_sha256"]), 64)  # SHA-256 hex length
                self.assertIn("evidence_class", entry)
                self.assertIn("stage", entry)
                self.assertIn("prompt_packet_path", entry)
                self.assertIn("prompt_packet_sha256", entry)
                self.assertIn("prompt_packet_file_sha256", entry)

            # LLM was called 6 times (once per stage)
            self.assertEqual(mock_llm.call_count, 6)

            # Each call had system + user messages
            for call_args in mock_llm.call_args_list:
                messages = call_args[0][0]
                self.assertEqual(len(messages), 2)
                self.assertEqual(messages[0]["role"], "system")
                self.assertEqual(messages[1]["role"], "user")

        finally:
            agent_orchestrator.REPO_ROOT = original_root

    @patch("agent_orchestrator.invoke_llm", side_effect=_fake_invoke_llm)
    def test_single_dispatch_produces_verifiable_artifact(self, mock_llm: Any) -> None:
        """Dispatch one agent and verify the artifact is checksummed."""
        import agent_orchestrator
        original_root = agent_orchestrator.REPO_ROOT
        agent_orchestrator.REPO_ROOT = self.tmp_root

        try:
            from agent_orchestrator import dispatch_agent

            result = dispatch_agent(
                "erdos-straus",
                role="experimentalist",
                stage="experiment",
                model="mock",
            )

            self.assertTrue(result["success"])
            artifact_path = Path(result["artifact_path"])
            self.assertTrue(artifact_path.exists())

            # Read artifact and verify contents
            content = artifact_path.read_text(encoding="utf-8")
            self.assertIn("stage: experiment", content)
            self.assertIn("Mock experiment artifact", content)

            # Verify manifest checksum matches actual file
            artifacts_dir = artifact_path.parent
            manifest = yaml.safe_load(
                (artifacts_dir / "manifest.yaml").read_text(encoding="utf-8")
            )
            entry = manifest["artifacts"][0]
            expected_checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
            self.assertEqual(entry["checksum_sha256"], expected_checksum)

        finally:
            agent_orchestrator.REPO_ROOT = original_root

    @patch("agent_orchestrator.invoke_llm", side_effect=_fake_invoke_llm)
    def test_evidence_bundle_integration(self, mock_llm: Any) -> None:
        """Run experiment, then compute and verify evidence bundle."""
        import agent_orchestrator
        import verify_evidence

        original_orch_root = agent_orchestrator.REPO_ROOT
        original_ev_root = verify_evidence.REPO_ROOT
        agent_orchestrator.REPO_ROOT = self.tmp_root
        verify_evidence.REPO_ROOT = self.tmp_root

        try:
            from agent_orchestrator import dispatch_agent

            # Create some artifacts
            dispatch_agent("erdos-straus", role="experimentalist", stage="experiment", model="mock")
            dispatch_agent("erdos-straus", role="analyst", stage="results", model="mock")

            # Now compute evidence bundle (pass problem_id string, not Path)
            from verify_evidence import compute_evidence_bundle

            bundle_result = compute_evidence_bundle("erdos-straus")

            self.assertTrue(bundle_result["success"])
            self.assertGreaterEqual(bundle_result["artifact_count"], 2)

            # Verify the bundle
            from verify_evidence import verify_evidence_bundle

            verify_result = verify_evidence_bundle("erdos-straus")
            self.assertTrue(verify_result["success"])
            self.assertEqual(verify_result["verdict"], "PASS")
            self.assertEqual(verify_result["failed_count"], 0)
            self.assertEqual(verify_result["missing_count"], 0)

        finally:
            agent_orchestrator.REPO_ROOT = original_orch_root
            verify_evidence.REPO_ROOT = original_ev_root

    @patch("agent_orchestrator.invoke_llm", side_effect=_fake_invoke_llm)
    def test_proof_first_pipeline_routes_correctly(self, mock_llm: Any) -> None:
        """For T4-structural problems, pipeline should use 'prove' instead of 'experiment'."""
        import agent_orchestrator
        original_root = agent_orchestrator.REPO_ROOT
        agent_orchestrator.REPO_ROOT = self.tmp_root

        try:
            # Create a T4-structural triage entry for a test problem
            ws = self.tmp_root / "research" / "active" / "test-structural"
            (ws / "control").mkdir(parents=True)
            (ws / "experiments").mkdir(parents=True)
            (ws / "artifacts").mkdir(parents=True)

            # Patch triage to return T4 for this problem
            triage_path = self.tmp_root / "registry" / "triage-matrix.yaml"
            if triage_path.exists():
                triage_data = yaml.safe_load(triage_path.read_text(encoding="utf-8")) or {}
            else:
                triage_data = {}

            triage_data.setdefault("tier_4_structural", []).append({
                "id": "test-structural",
                "amenability_score": 5,
                "approach": "proof-theoretic",
            })
            triage_path.parent.mkdir(parents=True, exist_ok=True)
            triage_path.write_text(
                yaml.safe_dump(triage_data, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

            from agent_orchestrator import run_pipeline

            result = run_pipeline(
                "test-structural",
                from_stage="plan",
                to_stage="results",
                model="mock",
            )

            self.assertTrue(result["success"])
            # Should route through prove, not experiment
            self.assertIn("prove", result["stages_run"])
            self.assertNotIn("experiment", result["stages_run"])

        finally:
            agent_orchestrator.REPO_ROOT = original_root


class EndToEndDryRunSmokeTest(unittest.TestCase):
    """Smoke test using dry-run mode against real repo structure (no mocking)."""

    def test_dry_run_pipeline_erdos_straus(self) -> None:
        """Dry-run pipeline against real registry — no LLM calls, no tmp dir."""
        from agent_orchestrator import run_pipeline

        result = run_pipeline(
            "erdos-straus",
            from_stage="brief",
            to_stage="plan",
            dry_run=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["stages_run"], ["brief", "novelty", "triage", "plan"])

        # All dry-run results should have prompts
        for sr in result["stage_results"]:
            self.assertTrue(sr["success"])
            self.assertTrue(sr["dry_run"])
            self.assertIn("system_prompt", sr)
            self.assertIn("user_prompt", sr)

    def test_dry_run_all_stages_produce_valid_prompts(self) -> None:
        """Verify every stage produces non-empty system and user prompts."""
        from agent_orchestrator import STAGE_TO_ROLE, run_stage

        for stage in STAGE_TO_ROLE:
            with self.subTest(stage=stage):
                result = run_stage("erdos-straus", stage=stage, dry_run=True)
                self.assertTrue(result["success"], f"Stage {stage} failed: {result}")
                self.assertGreater(len(result["system_prompt"]), 100)
                self.assertGreater(len(result["user_prompt"]), 50)


if __name__ == "__main__":
    unittest.main()
