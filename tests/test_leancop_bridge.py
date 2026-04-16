#!/usr/bin/env python3
"""Unit tests for OMEGA LeanCopilot bridge helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import leancop_bridge as bridge  # type: ignore


class LeanCopBridgeTests(unittest.TestCase):
    def test_build_generation_messages_includes_goal_and_prefix(self) -> None:
        messages = bridge.build_generation_messages("⊢ True", "simp", 5)
        self.assertEqual(len(messages), 2)
        self.assertIn("Lean 4 tactic generator", messages[0]["content"])
        self.assertIn("⊢ True", messages[1]["content"])
        self.assertIn("Target prefix constraint: simp", messages[1]["content"])

    def test_normalize_tactic_candidates_filters_and_deduplicates(self) -> None:
        raw = """
        - exact True.intro
        1. exact True.intro
        ```lean
        simp
        ```
        apply And.intro
        """
        tactics = bridge.normalize_tactic_candidates(raw, max_candidates=3)
        self.assertEqual(tactics[0], "exact True.intro")
        self.assertEqual(tactics[1], "simp")
        self.assertEqual(tactics[2], "apply And.intro")

    def test_normalize_tactics_applies_prefix_filter(self) -> None:
        raw = "simp\nrfl\nsimp [Nat.add_comm]"
        tactics = bridge.normalize_tactic_candidates(raw, max_candidates=5, target_prefix="simp")
        self.assertEqual(tactics, ["simp", "simp [Nat.add_comm]"])

    def test_generate_tactics_scores_outputs(self) -> None:
        cfg = bridge.BridgeConfig(
            host="127.0.0.1",
            port=23337,
            base_url="http://localhost:8000/v1",
            model="goedel-prover-v2-32b",
            api_key_env="OPENAI_API_KEY",
            temperature=0.1,
            max_tokens=128,
            candidates=3,
            timeout_seconds=30,
        )
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False), patch.object(
            bridge,
            "request_openai_chat",
            return_value="exact True.intro\nconstructor\ntrivial",
        ):
            outputs = bridge.generate_tactics("⊢ True", "", cfg)

        self.assertEqual(len(outputs), 3)
        self.assertEqual(outputs[0]["output"], "exact True.intro")
        self.assertGreaterEqual(outputs[0]["score"], outputs[1]["score"])


if __name__ == "__main__":
    unittest.main()
