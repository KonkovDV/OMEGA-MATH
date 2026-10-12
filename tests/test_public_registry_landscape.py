#!/usr/bin/env python3
"""Public-registry ideas stay a reading. They do not close entries or move scores."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "research" / "external" / "public_registry_landscape_2026.yaml"
NOTE = ROOT / "research" / "OMEGA_PUBLIC_REGISTRY_LANDSCAPE_2026_10_12.md"
PROTOCOL = ROOT / "PROTOCOL.md"


class PublicRegistryLandscapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
        self.note = NOTE.read_text(encoding="utf-8")
        self.protocol = PROTOCOL.read_text(encoding="utf-8")

    def test_statement_counts_stay_distinct_snapshots(self) -> None:
        paper = self.payload["snapshots"]["formal_conjectures_paper"]["indexed_statements"]
        stats = self.payload["snapshots"]["formal_conjectures_stats"]["indexed_statements"]
        ingest = self.payload["snapshots"]["qed_ingest"]["formal_conjectures_records"]
        self.assertEqual(paper, 2615)
        self.assertEqual(stats, 6329)
        mirror = self.payload["snapshots"]["formal_conjectures_firsching"]["indexed_statements"]
        self.assertEqual(mirror, 5172)
        self.assertFalse(
            self.payload["snapshots"]["formal_conjectures_firsching"]["reconciled_with_official_stats"]
        )
        self.assertEqual(ingest, 1417)
        self.assertEqual(len({paper, stats, mirror, ingest}), 4)
        self.assertEqual(self.payload["snapshots"]["qed_homepage"]["statements"], 1858)
        self.assertEqual(self.payload["snapshots"]["qed_homepage"]["machine_checked"], 37)
        self.assertEqual(self.payload["snapshots"]["qed_ingest"]["erdosproblems_proof_claims"], "unavailable")

    def test_mathdb_self_report_is_not_adopted(self) -> None:
        mathdb = self.payload["snapshots"]["mathdb_about"]
        self.assertEqual(mathdb["problems_catalogued"], 87328)
        self.assertEqual(mathdb["evidence_class"], "E2")
        self.assertFalse(mathdb["mechanical_check"])
        self.assertFalse(mathdb["claims_adopted"])
        self.assertIn("does not adopt those claims", self.note)

    def test_same_party_check_is_not_called_an_independent_rebuild(self) -> None:
        self.assertIn("not V3", self.note)
        self.assertIn("runner gate is unchanged", self.protocol)
        self.assertIn("not `statement_fidelity: faithful`", self.protocol)
        self.assertTrue(self.payload["runner_gate_unchanged"])
        self.assertIn("language-model filter", " ".join(self.payload["rejected"]))

    def test_sorry_count_and_titles_do_not_close_entries(self) -> None:
        self.assertIn("sorry` in a statement library is normal", self.note)
        self.assertIn("speaks for none", self.note)
        self.assertIn("## 1.12 Public Registries (October 2026)", self.protocol)
        self.assertIn("§1.5 still holds", self.note)
        self.assertFalse(self.payload["registry_growth"])
        self.assertEqual(self.payload["score_change"], "none")
        self.assertIn("not an independent corpus", self.note)
        self.assertNotIn("earlier the same day", self.note)
        self.assertNotIn("zero-contamination bench", self.note)
        self.assertNotIn("earlier or narrower", (ROOT / "research" / "OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md").read_text(encoding="utf-8"))
        self.assertIn("four readings", self.protocol)


if __name__ == "__main__":
    unittest.main()
