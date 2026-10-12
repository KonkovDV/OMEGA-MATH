#!/usr/bin/env python3
"""The OpenAI catalog ledger must not close a registry problem or a domain."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "research" / "external" / "openai_math_catalog_2026.yaml"

WITHDRAWN = [
    "Algebraicity of Weil classes on split abelian eightfolds",
    "Algebraicity of Kuga–Satake Correspondences for K3 Surfaces",
    "The rational Hodge conjecture for products of K3 surfaces",
]

OPEN_ENTRIES = [
    ("registry/domains/analysis.yaml", "navier-stokes"),
    ("registry/domains/number-theory.yaml", "riemann-hypothesis"),
    ("registry/domains/geometry.yaml", "hodge-conjecture"),
    ("registry/domains/probability-theory.yaml", "self-avoiding-walk-connective"),
    ("registry/domains/geometry.yaml", "abundance-conjecture"),
    ("registry/domains/number-theory.yaml", "birch-swinnerton-dyer"),
]


def _problem(relative: str, problem_id: str) -> dict:
    payload = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
    for item in payload["problems"]:
        if item["id"] == problem_id:
            return item
    raise AssertionError(f"{problem_id} missing from {relative}")


class OpenAIMathCatalogLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))

    def test_repository_counts(self) -> None:
        self.assertEqual(self.payload["manuscripts"], 719)
        self.assertEqual(self.payload["families"], 372)
        self.assertEqual(self.payload["formalized_top_line_self_report"], 300)
        self.assertIn("300/719", self.payload["formalized_note"])
        self.assertTrue(str(self.payload["commit"]).startswith("fd4aeeb2ee4f"))
        self.assertFalse(self.payload["domain_closed"])
        catalog = self.payload["formalization_yaml"]
        self.assertEqual(catalog["sources"], 173)
        self.assertEqual(catalog["main_results"], 200)
        self.assertFalse(catalog["matches_self_report"])
        self.assertFalse(self.payload["secondary_manuscript_count_722_adopted"])
        protocol = self.payload["release_protocol"]
        self.assertEqual(protocol["comparator_challenges"], 416)
        self.assertEqual(protocol["scope_notes"], 242)
        self.assertTrue(protocol["comparator_same_party"])
        self.assertFalse(protocol["citation_url_tracks_commit"])
        self.assertFalse(protocol["withdrawn_titles_in_contents"])
        self.assertFalse(protocol["model_replayable"])
        self.assertEqual(len(protocol["support_challenges_not_main_theorems"]), 5)
        self.assertEqual(protocol["toolchain"], "leanprover/lean4:v4.34.1")
        self.assertIn("Not Clay", protocol["family_376"])

    def test_three_withdrawals_from_one_sign_error(self) -> None:
        titles = [item["title"] for item in self.payload["withdrawn"]]
        self.assertEqual(titles, WITHDRAWN)
        self.assertEqual(self.payload["withdrawn"][0]["role"], "source")
        self.assertTrue(all(item["role"] == "dependent" for item in self.payload["withdrawn"][1:]))

    def test_special_cases_do_not_close_millennium_problems(self) -> None:
        by_id = {item["id"]: item for item in self.payload["exceptions"]}
        self.assertFalse(by_id["zeta-zero-free-region"]["closes_riemann_hypothesis"])
        self.assertTrue(by_id["zeta-zero-free-region"]["human_edited_writeup"])
        self.assertFalse(by_id["hodge-cm-abelian"]["closes_hodge_conjecture"])
        navier = self.payload["navier_stokes"]
        self.assertEqual(navier["clay_statements_claimed"], ["C", "D"])
        self.assertTrue(navier["forced"])
        self.assertFalse(navier["unforced_claimed"])
        self.assertFalse(navier["closes_registry_entry"])
        self.assertFalse(navier["prize_claimed_by_openai"])

    def test_press_details_stay_unadopted(self) -> None:
        refused = self.payload["not_adopted"]
        self.assertIn("A research domain was annihilated", refused)
        self.assertIn("The unforced Navier-Stokes problem is solved", refused)
        self.assertIn("The square-lattice connective constant is known", refused)
        self.assertFalse(self.payload["le_monde"]["body_retrieved"])
        self.assertEqual(self.payload["le_monde"]["evidence_class"], "E2")

    def test_registry_entries_stay_open(self) -> None:
        for relative, problem_id in OPEN_ENTRIES:
            problem = _problem(relative, problem_id)
            self.assertEqual(problem["status"], "open", problem_id)
        navier = _problem("registry/domains/analysis.yaml", "navier-stokes")
        self.assertIn("Clay", navier["statement"])
        self.assertIn("(A)", navier["statement"])
        self.assertIn("(B)", navier["statement"])
        hadwiger = _problem("registry/domains/graph-theory.yaml", "hadwiger-conjecture")
        self.assertEqual(hadwiger["status"], "open")
        checks = {item["id"]: item for item in self.payload["statement_checks"]}
        self.assertTrue(checks["hadwiger-conjecture"]["matches_registry_sentence"])
        self.assertFalse(checks["hadwiger-conjecture"]["closes_registry_entry"])
        self.assertFalse(checks["hadwiger-conjecture"]["compiled_by_omega"])
        self.assertFalse(checks["riemann-seven-eighths"]["matches_registry_sentence"])
        self.assertFalse(checks["riemann-seven-eighths"]["closes_registry_entry"])


if __name__ == "__main__":
    unittest.main()
