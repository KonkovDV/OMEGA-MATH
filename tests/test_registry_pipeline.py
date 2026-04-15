#!/usr/bin/env python3
"""Direct tests for the generated registry index and registry validator."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import generate_index  # type: ignore
import validate_registry  # type: ignore


def _write_yaml(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


class RegistryPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent / "_test_registry_workspace"
        if self.repo_root.exists():
            shutil.rmtree(self.repo_root)

        (self.repo_root / "registry" / "domains").mkdir(parents=True)
        (self.repo_root / "registry" / "collections").mkdir(parents=True)
        self.index_file = self.repo_root / "registry" / "index.yaml"
        self.triage_file = self.repo_root / "registry" / "triage-matrix.yaml"

    def tearDown(self) -> None:
        if self.repo_root.exists():
            shutil.rmtree(self.repo_root)

    def _patch_generate_index(self):
        return patch.multiple(
            generate_index,
            REPO_ROOT=self.repo_root,
            DOMAINS_DIR=self.repo_root / "registry" / "domains",
            COLLECTIONS_DIR=self.repo_root / "registry" / "collections",
            TRIAGE_FILE=self.triage_file,
            INDEX_FILE=self.index_file,
        )

    def _patch_validate_registry(self):
        return patch.multiple(
            validate_registry,
            REPO_ROOT=self.repo_root,
            DOMAINS_DIR=self.repo_root / "registry" / "domains",
            COLLECTIONS_DIR=self.repo_root / "registry" / "collections",
            TRIAGE_FILE=self.triage_file,
            SCHEMA_FILE=self.repo_root / "registry" / "missing-schema.json",
        )

    def test_generate_index_counts_triage_entries_from_yaml_sections(self) -> None:
        _write_yaml(
            self.repo_root / "registry" / "domains" / "number-theory.yaml",
            {
                "problems": [
                    {
                        "id": "erdos-straus",
                        "name": "Erdos-Straus",
                        "status": "open",
                        "statement": "4/n = 1/x + 1/y + 1/z",
                        "tags": ["egyptian-fractions"],
                        "ai_triage": {"tier": "T1-computational", "amenability_score": 8},
                    },
                    {
                        "id": "goldbach-conjecture",
                        "name": "Goldbach",
                        "status": "open",
                        "statement": "Every even number > 2 is the sum of two primes",
                        "tags": ["primes"],
                        "ai_triage": {"tier": "T3-pattern", "amenability_score": 4},
                    },
                ]
            },
        )
        _write_yaml(
            self.triage_file,
            {
                "tier_1_computational": [{"id": "erdos-straus", "score": 8}],
                "tier_2_experimental": [],
                "tier_3_pattern": [{"id": "goldbach-conjecture", "score": 4}],
                "tier_4_structural": [],
                "tier_5_foundational": [],
            },
        )

        with self._patch_generate_index():
            index = generate_index.build_index()
            generate_index.write_index(index)

        self.assertEqual(index["summary"]["with_ai_triage"], 2)
        self.assertEqual(index["summary"]["triage_matrix_entries"], 2)
        self.assertEqual(index["tier_distribution"]["T1-computational"], 1)
        self.assertEqual(index["tier_distribution"]["T3-pattern"], 1)
        self.assertIn("scripts/generate_index.py", self.index_file.read_text(encoding="utf-8"))

    def test_validate_registry_accepts_consistent_tiers_and_triage_parity(self) -> None:
        _write_yaml(
            self.repo_root / "registry" / "domains" / "geometry.yaml",
            {
                "problems": [
                    {
                        "id": "kobon-triangles",
                        "name": "Kobon triangles",
                        "status": "open",
                        "statement": "maximize triangles",
                        "tags": ["geometry"],
                        "ai_triage": {"tier": "T1-computational", "amenability_score": 8},
                    }
                ]
            },
        )
        _write_yaml(
            self.triage_file,
            {
                "tier_1_computational": [{"id": "kobon-triangles", "score": 8}],
                "tier_2_experimental": [],
                "tier_3_pattern": [],
                "tier_4_structural": [],
                "tier_5_foundational": [],
            },
        )

        stdout = io.StringIO()
        with self._patch_validate_registry(), contextlib.redirect_stdout(stdout):
            exit_code = validate_registry.main([])

        self.assertEqual(exit_code, 0)
        self.assertIn("0 errors", stdout.getvalue())

    def test_validate_registry_rejects_tier_drift_and_missing_matrix_entry(self) -> None:
        _write_yaml(
            self.repo_root / "registry" / "domains" / "game-theory.yaml",
            {
                "problems": [
                    {
                        "id": "chess-first-move",
                        "name": "Solving chess",
                        "status": "open",
                        "statement": "perfect play outcome",
                        "tags": ["chess"],
                        "ai_triage": {"tier": "T1-computational", "amenability_score": 3},
                    }
                ]
            },
        )
        _write_yaml(
            self.triage_file,
            {
                "tier_1_computational": [],
                "tier_2_experimental": [],
                "tier_3_pattern": [],
                "tier_4_structural": [],
                "tier_5_foundational": [],
            },
        )

        stdout = io.StringIO()
        with self._patch_validate_registry(), contextlib.redirect_stdout(stdout):
            exit_code = validate_registry.main([])

        report = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("requires tier 'T3-pattern'", report)
        self.assertIn("Missing triaged domain ID 'chess-first-move'", report)


if __name__ == "__main__":
    unittest.main()