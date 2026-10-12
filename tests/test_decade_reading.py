#!/usr/bin/env python3
"""The decade reading must stay a triage note, not a score change or a forecast dressed as data."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTE = ROOT / "research" / "OMEGA_DECADE_FROM_2026_CATALOGS.md"
PROTOCOL = ROOT / "PROTOCOL.md"


class DecadeReadingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = NOTE.read_text(encoding="utf-8")

    def test_projections_are_not_labeled_as_established_fact(self) -> None:
        header, _, _ = self.text.partition("# What to keep")
        self.assertNotIn("evidence_class: E1\n", header)
        self.assertIn("H for cost projections", header)
        self.assertIn("class H", self.text)
        self.assertIn("post-hoc", self.text)

    def test_alphaproof_miss_is_not_called_a_small_model_result(self) -> None:
        self.assertIn("64 TPU-hours", self.text)
        self.assertNotIn("too small", self.text.lower())

    def test_empty_definition_list_does_not_ignore_the_theorem_type(self) -> None:
        self.assertIn("match that type", self.text)
        self.assertNotIn("certify a local redefinition", self.text)

    def test_deformalization_is_not_the_hansen_solution(self) -> None:
        self.assertIn("deformalization", self.text.lower())
        self.assertIn("does not show that the term", self.text)

    def test_triage_rejects_score_changes_and_theorem_counts(self) -> None:
        self.assertIn("Amenability change", self.text)
        self.assertIn("| Reject | None |", self.text)
        self.assertIn("No registry score", self.text)
        protocol = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("## 1.11 What To Keep For The Next Decade", protocol)
        self.assertIn("projection", protocol)


if __name__ == "__main__":
    unittest.main()
