#!/usr/bin/env python3
"""Unit tests for OMEGA workspace scaffolding."""

from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import scaffold_problem  # type: ignore


class ScaffoldProblemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_active_dir = scaffold_problem.ACTIVE_RESEARCH_DIR
        self.temp_root = Path(__file__).resolve().parent / "_test_scaffold_workspace"
        if self.temp_root.exists():
            shutil.rmtree(self.temp_root)
        self.temp_root.mkdir(parents=True)
        scaffold_problem.ACTIVE_RESEARCH_DIR = self.temp_root

    def tearDown(self) -> None:
        scaffold_problem.ACTIVE_RESEARCH_DIR = self.original_active_dir
        if self.temp_root.exists():
            shutil.rmtree(self.temp_root)

    def test_render_templates_include_synthetic_packets(self) -> None:
        templates = scaffold_problem.render_templates("goldbach", "Goldbach conjecture")
        self.assertIn("input_files/synthetic_taxonomy.md", templates)
        self.assertIn("input_files/synthetic_evaluation_packet.md", templates)
        self.assertIn("synthetic_taxonomy:", templates["artifacts/run-manifest.yaml"])
        self.assertIn("synthetic_evaluation_packet:", templates["artifacts/run-manifest.yaml"])

    def test_main_writes_synthetic_packet_stubs(self) -> None:
        exit_code = scaffold_problem.main(["goldbach", "--title", "Goldbach conjecture"])
        self.assertEqual(exit_code, 0)

        workspace = self.temp_root / "goldbach"
        taxonomy = workspace / "input_files" / "synthetic_taxonomy.md"
        evaluation = workspace / "input_files" / "synthetic_evaluation_packet.md"

        self.assertTrue(taxonomy.exists())
        self.assertTrue(evaluation.exists())
        self.assertIn("Replace this stub with `templates/synthetic-reasoning-taxonomy.md`", taxonomy.read_text(encoding="utf-8"))
        self.assertIn("Replace this stub with `templates/synthetic-evaluation-packet.md`", evaluation.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()