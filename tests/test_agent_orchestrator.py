"""Tests for OMEGA Agent Orchestrator.

Tests prompt construction, context assembly, artifact saving, YAML extraction,
and dry-run dispatch — all without requiring an LLM API key.
"""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import yaml


class TestLoadAgentDefinition(unittest.TestCase):
    """Test loading agent YAML definitions."""

    def test_load_known_roles(self) -> None:
        from agent_orchestrator import load_agent_definition

        for role in ("planner", "librarian", "analyst", "experimentalist", "prover", "writer", "reviewer"):
            defn = load_agent_definition(role)
            self.assertIn("id", defn)
            self.assertIn("role", defn)
            self.assertIn("purpose", defn)
            self.assertIn("inputs", defn)
            self.assertIn("outputs", defn)

    def test_load_unknown_role_raises(self) -> None:
        from agent_orchestrator import load_agent_definition

        with self.assertRaises(FileNotFoundError):
            load_agent_definition("nonexistent-agent-role")


class TestLoadTeamConfig(unittest.TestCase):
    """Test loading team orchestration config."""

    def test_team_has_required_keys(self) -> None:
        from agent_orchestrator import load_team_config

        config = load_team_config()
        self.assertIn("orchestration", config)
        self.assertIn("execution_order", config["orchestration"])
        self.assertIn("routing_rules", config["orchestration"])
        self.assertIn("artifacts", config)
        self.assertIn("quality_gates", config)


class TestBuildSystemPrompt(unittest.TestCase):
    """Test system prompt construction from agent definitions."""

    def test_system_prompt_contains_role_info(self) -> None:
        from agent_orchestrator import build_system_prompt

        agent_def = {
            "id": "test-agent",
            "role": "experimentalist",
            "purpose": "run computational experiments",
            "inputs": ["approach memo", "compute budget"],
            "outputs": ["experiment logs", "candidate constructions"],
            "success_criteria": ["run is reproducible", "parameters are recorded"],
        }
        prompt = build_system_prompt(agent_def)

        self.assertIn("experimentalist", prompt)
        self.assertIn("run computational experiments", prompt)
        self.assertIn("approach memo", prompt)
        self.assertIn("experiment logs", prompt)
        self.assertIn("run is reproducible", prompt)
        # Evidence governance rules included
        self.assertIn("R0", prompt)
        self.assertIn("E2", prompt)
        self.assertIn("Anti-overclaiming", prompt)


class TestBuildUserPrompt(unittest.TestCase):
    """Test user prompt construction with problem context."""

    def test_user_prompt_includes_stage_and_problem_id(self) -> None:
        from agent_orchestrator import build_user_prompt

        context = {
            "problem_id": "erdos-straus",
            "registry": {"title": "Erdős–Straus Conjecture", "domain": "number-theory", "status": "open"},
            "triage": {"tier": "T1-computational", "amenability_score": 8},
            "workspace": None,
            "workflow": None,
            "prior_runs": [],
        }
        prompt = build_user_prompt("experiment", context)

        self.assertIn("Stage: experiment", prompt)
        self.assertIn("erdos-straus", prompt)
        self.assertIn("Erdős–Straus Conjecture", prompt)
        self.assertIn("T1-computational", prompt)
        self.assertIn("Design and describe the computational experiment", prompt)

    def test_user_prompt_handles_empty_context(self) -> None:
        from agent_orchestrator import build_user_prompt

        context = {
            "problem_id": "unknown-problem",
            "registry": None,
            "triage": None,
            "workspace": None,
            "workflow": None,
            "prior_runs": [],
        }
        prompt = build_user_prompt("plan", context)
        self.assertIn("unknown-problem", prompt)
        self.assertIn("Stage: plan", prompt)

    def test_user_prompt_includes_benchmark_snapshot(self) -> None:
        from agent_orchestrator import build_user_prompt

        context = {
            "problem_id": "thomson-problem",
            "registry": {"title": "Thomson problem", "domain": "geometry", "status": "open"},
            "triage": {"tier": "T1-computational", "amenability_score": 8},
            "benchmark": {
                "objective": "maximize",
                "our_result": "0.5134721",
                "previous_best": "0.5134719",
                "improvement": "+0.0000002",
                "source_problem_path": "tammes-problem",
            },
            "workspace": None,
            "workflow": None,
            "prior_runs": [],
        }
        prompt = build_user_prompt("experiment", context)

        self.assertIn("External Benchmark Snapshot", prompt)
        self.assertIn("Current snapshot result: 0.5134721", prompt)
        self.assertIn("Benchmark Alignment Requirement", prompt)


class TestExtractYamlBlock(unittest.TestCase):
    """Test YAML block extraction from LLM output."""

    def test_extract_valid_yaml_block(self) -> None:
        from agent_orchestrator import extract_yaml_block

        text = textwrap.dedent("""\
            Here is my analysis.

            ```yaml
            artifact_type: experiment-log
            evidence_class: R1
            confidence: C2
            summary: Found 3 new parametric families
            key_findings:
              - Family A covers residues mod 7
              - Family B covers residues mod 11
              - Combined coverage reaches 94%
            ```

            That concludes my work.
        """)
        result = extract_yaml_block(text)
        assert result is not None
        self.assertEqual(result["artifact_type"], "experiment-log")
        self.assertEqual(result["evidence_class"], "R1")
        self.assertEqual(len(result["key_findings"]), 3)

    def test_extract_returns_none_for_no_yaml(self) -> None:
        from agent_orchestrator import extract_yaml_block

        result = extract_yaml_block("Just plain text, no yaml here.")
        self.assertIsNone(result)

    def test_extract_returns_last_yaml_block(self) -> None:
        from agent_orchestrator import extract_yaml_block

        text = textwrap.dedent("""\
            ```yaml
            first: block
            ```
            Some text.
            ```yaml
            second: block
            artifact_type: result-summary
            ```
        """)
        result = extract_yaml_block(text)
        assert result is not None
        self.assertEqual(result["artifact_type"], "result-summary")


class TestSaveArtifact(unittest.TestCase):
    """Test artifact saving to workspace."""

    def test_save_creates_file_and_manifest(self, ) -> None:
        import tempfile
        from agent_orchestrator import save_artifact, REPO_ROOT

        with tempfile.TemporaryDirectory() as tmpdir:
            # Patch REPO_ROOT to temp dir
            tmp_path = Path(tmpdir)
            workspace = tmp_path / "research" / "active" / "test-problem"
            workspace.mkdir(parents=True)

            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                artifact_path = save_artifact(
                    "test-problem",
                    "experiment",
                    "# Experiment Results\nFound something interesting.",
                    {"role": "experimentalist", "evidence_class": "R1", "confidence": "C2"},
                )

            self.assertTrue(artifact_path.exists())
            content = artifact_path.read_text(encoding="utf-8")
            self.assertIn("stage: experiment", content)
            self.assertIn("Found something interesting", content)

            # Check manifest was created
            manifest_path = workspace / "artifacts" / "manifest.yaml"
            self.assertTrue(manifest_path.exists())
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["artifacts"]), 1)
            self.assertIn("checksum_sha256", manifest["artifacts"][0])

    def test_save_with_prompt_packet_persists_prompt_file(self) -> None:
        import tempfile
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            workspace = tmp_path / "research" / "active" / "test-problem"
            workspace.mkdir(parents=True)

            prompt_packet = {
                "version": "1.0",
                "problem_id": "test-problem",
                "stage": "experiment",
                "messages": [
                    {"role": "system", "content": "s"},
                    {"role": "user", "content": "u"},
                ],
            }

            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                artifact_path = save_artifact(
                    "test-problem",
                    "experiment",
                    "# Experiment Results\nPrompt packet test.",
                    {
                        "role": "experimentalist",
                        "evidence_class": "R1",
                        "confidence": "C2",
                        "prompt_packet_sha256": "abc123",
                    },
                    prompt_packet=prompt_packet,
                )

            self.assertTrue(artifact_path.exists())
            artifacts_dir = workspace / "artifacts"
            prompt_dir = artifacts_dir / "prompts"
            self.assertTrue(prompt_dir.exists())
            prompt_files = list(prompt_dir.glob("*.prompt.json"))
            self.assertEqual(len(prompt_files), 1)

            manifest = yaml.safe_load((artifacts_dir / "manifest.yaml").read_text(encoding="utf-8"))
            entry = manifest["artifacts"][0]
            self.assertIn("prompt_packet_path", entry)
            self.assertIn("prompt_packet_sha256", entry)
            self.assertIn("prompt_packet_file_sha256", entry)


class TestDryRun(unittest.TestCase):
    """Test dry-run mode (no LLM call)."""

    def test_run_stage_dry_run_returns_prompts(self) -> None:
        from agent_orchestrator import run_stage

        result = run_stage(
            "erdos-straus",
            stage="plan",
            dry_run=True,
        )
        self.assertTrue(result["success"])
        self.assertTrue(result["dry_run"])
        self.assertIn("system_prompt", result)
        self.assertIn("user_prompt", result)
        self.assertIn("OMEGA research agent", result["system_prompt"])

    def test_run_stage_unknown_stage_returns_error(self) -> None:
        from agent_orchestrator import run_stage

        result = run_stage("erdos-straus", stage="nonexistent-stage")
        self.assertFalse(result["success"])
        self.assertIn("Unknown stage", result["error"])

    def test_dispatch_agent_dry_run(self) -> None:
        from agent_orchestrator import dispatch_agent

        result = dispatch_agent(
            "thomson-problem",
            role="experimentalist",
            stage="experiment",
            dry_run=True,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["role"], "experimentalist")
        self.assertEqual(result["stage"], "experiment")
        self.assertIn("prompt_packet_sha256", result)
        self.assertIn("resolved_model", result)
        self.assertIn("resolved_backend", result)


class TestWorkspaceContract(unittest.TestCase):
    """Test workspace contract checks and auto-materialization of required files."""

    def _seed_agents(self, tmp_path: Path) -> None:
        import shutil
        real_agents = Path(__file__).resolve().parent.parent / "agents"
        target_agents = tmp_path / "agents"
        if real_agents.exists():
            shutil.copytree(real_agents, target_agents)

    def test_non_brief_stage_requires_workspace(self) -> None:
        from agent_orchestrator import dispatch_agent
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            self._seed_agents(tmp_path)
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                result = dispatch_agent(
                    "missing-problem",
                    role="librarian",
                    stage="novelty",
                    dry_run=True,
                )

        self.assertFalse(result["success"])
        self.assertIn("requires an initialized workspace", result["error"])

    @patch("agent_orchestrator.invoke_llm")
    def test_workspace_contract_autocreates_required_files(self, mock_invoke_llm: Any) -> None:
        from agent_orchestrator import dispatch_agent
        import tempfile

        mock_invoke_llm.return_value = {
            "content": "analysis\n```yaml\nartifact_type: novelty\n```",
            "model": "mock-model",
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "duration_seconds": 0.1,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            self._seed_agents(tmp_path)
            workspace = tmp_path / "research" / "active" / "test-problem"
            (workspace / "input_files").mkdir(parents=True)

            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                result = dispatch_agent(
                    "test-problem",
                    role="librarian",
                    stage="novelty",
                    model="mock",
                    dry_run=False,
                )

            self.assertTrue(result["success"])
            created = result["workspace_contract"].get("created_files", [])
            self.assertIn("README.md", created)
            self.assertIn("input_files/data_description.md", created)
            self.assertIn("input_files/literature.md", created)
            self.assertIn("input_files/citation_evidence.md", created)

            self.assertTrue((workspace / "README.md").exists())
            self.assertTrue((workspace / "input_files" / "literature.md").exists())
            self.assertTrue((workspace / "input_files" / "citation_evidence.md").exists())


class TestPipelineDryRun(unittest.TestCase):
    """Test pipeline execution in dry-run mode."""

    def test_pipeline_dry_run_runs_all_stages(self) -> None:
        from agent_orchestrator import run_pipeline

        result = run_pipeline(
            "erdos-straus",
            from_stage="brief",
            to_stage="plan",
            dry_run=True,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["stages_run"], ["brief", "novelty", "plan"])
        self.assertEqual(len(result["stage_results"]), 3)

    def test_pipeline_invalid_stage_order_fails(self) -> None:
        from agent_orchestrator import run_pipeline

        result = run_pipeline(
            "erdos-straus",
            from_stage="results",
            to_stage="brief",
        )
        self.assertFalse(result["success"])
        self.assertIn("must be before", result["error"])


class TestLoadProblemContext(unittest.TestCase):
    """Test problem context assembly from registry + workspace."""

    def test_load_erdos_straus_context(self) -> None:
        from agent_orchestrator import load_problem_context

        context = load_problem_context("erdos-straus")
        self.assertEqual(context["problem_id"], "erdos-straus")
        # Should find workspace
        if context["workspace"]:
            self.assertIn("erdos-straus", context["workspace"])

    def test_load_unknown_problem_returns_none_registry(self) -> None:
        from agent_orchestrator import load_problem_context

        context = load_problem_context("nonexistent-problem-xyz")
        self.assertEqual(context["problem_id"], "nonexistent-problem-xyz")
        self.assertIsNone(context["registry"])

    def test_load_benchmark_snapshot_for_thomson_problem(self) -> None:
        from agent_orchestrator import load_problem_context

        context = load_problem_context("thomson-problem")
        self.assertIn("benchmark", context)
        # If collection exists, tammes->thomson alias should yield benchmark context.
        if context["benchmark"] is not None:
            self.assertEqual(context["benchmark"].get("source_repo"), "togethercomputer/EinsteinArena-new-SOTA")


class TestStageToRoleMapping(unittest.TestCase):
    """Test that all stages map to valid agent roles."""

    def test_all_stages_map_to_loadable_roles(self) -> None:
        from agent_orchestrator import STAGE_TO_ROLE, load_agent_definition

        for stage, role in STAGE_TO_ROLE.items():
            defn = load_agent_definition(role)
            self.assertIn("id", defn, f"Role {role} for stage {stage} missing 'id'")


if __name__ == "__main__":
    unittest.main()
