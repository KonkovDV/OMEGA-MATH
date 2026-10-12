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

    @patch("agent_orchestrator.resolve_with_fallback")
    def test_dispatch_agent_forwards_prefer_local(self, mock_resolve: Any) -> None:
        from agent_orchestrator import dispatch_agent

        mock_profile = MagicMock(model="goedel-prover-v2-32b", temperature=0.1, max_tokens=8000)
        mock_backend = MagicMock(name="vllm")
        mock_backend.name = "vllm"
        mock_resolve.return_value = (mock_profile, mock_backend)

        result = dispatch_agent(
            "erdos-straus",
            role="prover",
            stage="brief",
            prefer_local=True,
            dry_run=True,
        )

        self.assertTrue(result["success"])
        self.assertTrue(result.get("prefer_local"))
        self.assertEqual(result.get("resolved_backend"), "vllm")
        self.assertEqual(mock_resolve.call_args.kwargs.get("prefer_local"), True)


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

    @patch("agent_orchestrator.invoke_llm")
    def test_prove_stage_autocreates_statement_spec(self, mock_invoke_llm: Any) -> None:
        from agent_orchestrator import dispatch_agent
        import tempfile

        mock_invoke_llm.return_value = {
            "content": "analysis\n```yaml\nartifact_type: prove\n```",
            "model": "mock-model",
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "duration_seconds": 0.1,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            self._seed_agents(tmp_path)
            workspace = tmp_path / "research" / "active" / "test-problem"
            workspace.mkdir(parents=True)

            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                result = dispatch_agent(
                    "test-problem",
                    role="prover",
                    stage="prove",
                    model="mock",
                    dry_run=False,
                )

            self.assertTrue(result["success"])
            created = result["workspace_contract"].get("created_files", [])
            self.assertIn("input_files/proof_obligations.md", created)
            self.assertIn("input_files/statement_spec.md", created)
            self.assertTrue((workspace / "input_files" / "statement_spec.md").exists())


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
        self.assertEqual(result["stages_run"], ["brief", "novelty", "triage", "plan"])
        self.assertEqual(len(result["stage_results"]), 4)

    def test_pipeline_dual_lane_includes_experiment_and_prove(self) -> None:
        from agent_orchestrator import run_pipeline

        result = run_pipeline(
            "erdos-straus",
            from_stage="plan",
            to_stage="results",
            dual_lane=True,
            dry_run=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["stages_run"], ["plan", "experiment", "prove", "results"])
        self.assertTrue(result["dual_lane"])

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


class TestAuditGates(unittest.TestCase):
    """The model does not grade its own evidence, and paths stay inside the tree."""

    def test_model_evidence_label_is_not_stored_as_the_class(self) -> None:
        import tempfile
        from agent_orchestrator import dispatch_agent

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            agents = tmp_path / "agents"
            agents.mkdir()
            (agents / "experimentalist.yaml").write_text(
                "id: experimentalist\nrole: experimentalist\npurpose: test\ninputs: []\noutputs: []\nsuccess_criteria: []\n",
                encoding="utf-8",
            )
            (agents / "team.yaml").write_text("orchestration: {}\n", encoding="utf-8")
            workspace = tmp_path / "research" / "active" / "test-problem"
            workspace.mkdir(parents=True)
            with patch("agent_orchestrator.REPO_ROOT", tmp_path), patch(
                "agent_orchestrator.invoke_llm",
                return_value={
                    "content": "```yaml\nevidence_class: R0\nconfidence: C3\n```",
                    "model": "mock",
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "duration_seconds": 0,
                },
            ):
                result = dispatch_agent("test-problem", role="experimentalist", stage="experiment", model="mock")

        self.assertTrue(result["success"])
        self.assertEqual(result["metadata"]["evidence_class"], "H")
        self.assertEqual(result["metadata"]["confidence"], "C1")
        self.assertEqual(result["metadata"]["model_asserted_evidence_class"], "R0")
        self.assertEqual(result["metadata"]["evidence_assignment"], "default-unverified")

    def test_unchecked_caller_label_is_stored_as_hypothesis(self) -> None:
        import tempfile
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "research" / "active" / "test-problem").mkdir(parents=True)
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                first = save_artifact("test-problem", "experiment", "one", {"evidence_class": "R1", "confidence": "C2"})
                second = save_artifact("test-problem", "experiment", "two", {})
            manifest = yaml.safe_load((tmp_path / "research" / "active" / "test-problem" / "artifacts" / "manifest.yaml").read_text(encoding="utf-8"))

        self.assertNotEqual(first.name, second.name)
        self.assertEqual(len(manifest["artifacts"]), 2)
        self.assertEqual(manifest["artifacts"][0]["evidence_class"], "H")
        self.assertEqual(manifest["artifacts"][1]["confidence"], "C1")

    def test_checked_without_an_anchor_file_stays_a_hypothesis(self) -> None:
        import tempfile
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "research" / "active" / "test-problem").mkdir(parents=True)
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                save_artifact(
                    "test-problem",
                    "prove",
                    "checked",
                    {"evidence_class": "R0", "confidence": "C2", "evidence_assignment": "checked"},
                )
            manifest = yaml.safe_load((tmp_path / "research" / "active" / "test-problem" / "artifacts" / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["artifacts"][0]["evidence_class"], "H")
        self.assertNotIn("evidence_anchor_sha256", manifest["artifacts"][0])

    def test_checked_anchor_records_the_file_hash(self) -> None:
        import hashlib
        import tempfile
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            workspace = tmp_path / "research" / "active" / "test-problem"
            anchor = workspace / "input_files" / "ledger.txt"
            anchor.parent.mkdir(parents=True)
            anchor.write_text("replay me", encoding="utf-8")
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                save_artifact(
                    "test-problem",
                    "prove",
                    "checked",
                    {
                        "evidence_class": "R0",
                        "confidence": "C2",
                        "evidence_assignment": "checked",
                        "evidence_anchor": "input_files/ledger.txt",
                        "evidence_verifier": "human-line-check",
                        "evidence_claim": "the ledger command matches the prose",
                    },
                )
            manifest = yaml.safe_load((workspace / "artifacts" / "manifest.yaml").read_text(encoding="utf-8"))
        entry = manifest["artifacts"][0]
        self.assertEqual(entry["evidence_class"], "R0")
        self.assertEqual(entry["confidence"], "C2")
        self.assertEqual(entry["evidence_anchor_sha256"], hashlib.sha256(b"replay me").hexdigest())

    def test_anchor_without_a_named_verifier_stays_a_hypothesis(self) -> None:
        import tempfile
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            workspace = tmp_path / "research" / "active" / "test-problem"
            anchor = workspace / "input_files" / "ledger.txt"
            anchor.parent.mkdir(parents=True)
            anchor.write_text("replay me", encoding="utf-8")
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                save_artifact(
                    "test-problem",
                    "prove",
                    "checked",
                    {
                        "evidence_class": "R0",
                        "confidence": "C3",
                        "evidence_assignment": "checked",
                        "evidence_anchor": "input_files/ledger.txt",
                    },
                )
            manifest = yaml.safe_load((workspace / "artifacts" / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["artifacts"][0]["evidence_class"], "H")
        self.assertEqual(manifest["artifacts"][0]["confidence"], "C1")

    def test_c3_without_an_external_source_stays_c2(self) -> None:
        import tempfile
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            workspace = tmp_path / "research" / "active" / "test-problem"
            anchor = workspace / "input_files" / "ledger.txt"
            anchor.parent.mkdir(parents=True)
            anchor.write_text("replay me", encoding="utf-8")
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                save_artifact(
                    "test-problem",
                    "prove",
                    "checked",
                    {
                        "evidence_class": "R0",
                        "confidence": "C3",
                        "evidence_assignment": "checked",
                        "evidence_anchor": "input_files/ledger.txt",
                        "evidence_verifier": "human-line-check",
                        "evidence_claim": "the ledger command matches the prose",
                    },
                )
            manifest = yaml.safe_load((workspace / "artifacts" / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["artifacts"][0]["evidence_class"], "R0")
        self.assertEqual(manifest["artifacts"][0]["confidence"], "C2")

    def test_resolved_path_cannot_leave_the_workspace(self) -> None:
        import tempfile
        from agent_orchestrator import path_inside, save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            workspace = tmp_path / "research" / "active" / "test-problem"
            workspace.mkdir(parents=True)
            secret = tmp_path / "secret.txt"
            secret.write_text("hidden", encoding="utf-8")
            with self.assertRaises(ValueError):
                path_inside(workspace, workspace / ".." / ".." / ".." / "secret.txt")
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                save_artifact(
                    "test-problem",
                    "prove",
                    "escape",
                    {
                        "evidence_class": "R0",
                        "confidence": "C3",
                        "evidence_assignment": "checked",
                        "evidence_anchor": "../secret.txt",
                        "evidence_verifier": "human-line-check",
                        "evidence_claim": "outside file",
                    },
                )
            manifest = yaml.safe_load((workspace / "artifacts" / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["artifacts"][0]["evidence_class"], "H")

    def test_parallel_saves_keep_both_manifest_entries(self) -> None:
        import tempfile
        from concurrent.futures import ThreadPoolExecutor
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "research" / "active" / "test-problem").mkdir(parents=True)
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [
                        pool.submit(save_artifact, "test-problem", "experiment", str(index), {})
                        for index in (1, 2)
                    ]
                    paths = [future.result() for future in futures]
            manifest = yaml.safe_load((tmp_path / "research" / "active" / "test-problem" / "artifacts" / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len({path.name for path in paths}), 2)
        self.assertEqual(len(manifest["artifacts"]), 2)

    def test_saved_prompt_packet_redacts_an_api_key(self) -> None:
        import os
        import tempfile
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "research" / "active" / "test-problem").mkdir(parents=True)
            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-secret-value"}), patch(
                "agent_orchestrator.REPO_ROOT", tmp_path
            ):
                save_artifact(
                    "test-problem",
                    "experiment",
                    "key sk-test-secret-value stays out",
                    {},
                    prompt_packet={"messages": [{"role": "user", "content": "sk-test-secret-value"}]},
                )
            artifacts = tmp_path / "research" / "active" / "test-problem" / "artifacts"
            prompt = next((artifacts / "prompts").glob("*.prompt.json")).read_text(encoding="utf-8")
            body = next(artifacts.glob("experiment_*.md")).read_text(encoding="utf-8")
        self.assertNotIn("sk-test-secret-value", prompt)
        self.assertNotIn("sk-test-secret-value", body)
        self.assertIn("[redacted]", prompt)

    def test_stale_manifest_lock_is_replaced(self) -> None:
        import os
        import tempfile
        import time
        from agent_orchestrator import save_artifact

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            artifacts = tmp_path / "research" / "active" / "test-problem" / "artifacts"
            artifacts.mkdir(parents=True)
            lock = artifacts / "manifest.lock"
            lock.write_text("dead", encoding="ascii")
            old = time.time() - 60
            os.utime(lock, (old, old))
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                save_artifact("test-problem", "experiment", "after-lock", {})
            self.assertFalse(lock.exists())
            manifest = yaml.safe_load((artifacts / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["artifacts"]), 1)

    def test_path_identifiers_are_refused(self) -> None:
        from agent_orchestrator import require_identifier

        for raw in ("../agents", "Role", "a/b", "con", "nul"):
            with self.assertRaises(ValueError):
                require_identifier(raw, "problem_id")

    def test_novelty_packet_needs_a_paper_not_a_bare_value(self) -> None:
        import tempfile
        from agent_orchestrator import attach_literature_surfaces

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            packet = tmp_path / "research" / "active" / "test-problem" / "input_files"
            packet.mkdir(parents=True)
            (packet / "novelty-packet.yaml").write_text(
                "query: erdos\nsource: semantic-scholar\ncandidates:\n  - title: A paper\n    paper_id: p1\n",
                encoding="utf-8",
            )
            (packet / "literature.md").write_text("\n", encoding="utf-8")
            context: dict[str, Any] = {}
            with patch("agent_orchestrator.REPO_ROOT", tmp_path):
                attach_literature_surfaces(context, "test-problem")
        self.assertEqual(context["literature_retrieval"], "not_run")
        self.assertIsNone(context["novelty_packet"])

    def test_novelty_prompt_includes_local_literature_and_says_search_did_not_run(self) -> None:
        from agent_orchestrator import build_user_prompt

        prompt = build_user_prompt(
            "novelty",
            {
                "problem_id": "erdos-straus",
                "registry": {},
                "triage": {},
                "workflow": {},
                "prior_runs": [],
                "literature_retrieval": "not_run",
                "literature_files": {"literature.md": "UNIQUE-PAPER-TOKEN"},
            },
        )
        self.assertIn("UNIQUE-PAPER-TOKEN", prompt)
        self.assertIn("Retrieval: not_run", prompt)
        self.assertIn("preliminary", prompt)


if __name__ == "__main__":
    unittest.main()
