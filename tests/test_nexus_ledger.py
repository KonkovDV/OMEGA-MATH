#!/usr/bin/env python3
"""The Nexus ledger must not promote a variant or a part to a closed problem."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "research" / "external" / "alphaproof_nexus_erdos_2026.yaml"

EXPECTED_FILES = {
    "erdos-12-i": "APNOutputs/ErdosProblems/erdos_12.parts.i.lean",
    "erdos-12-ii": "APNOutputs/ErdosProblems/erdos_12.parts.ii.lean",
    "erdos-125": "APNOutputs/ErdosProblems/erdos_125.variants.positive_lower_density.lean",
    "erdos-138": "APNOutputs/ErdosProblems/erdos_138.variants.difference.lean",
    "erdos-152": "APNOutputs/ErdosProblems/erdos_152.lean",
    "erdos-26-tenenbaum": "APNOutputs/ErdosProblems/erdos_26.variants.tenenbaum.lean",
    "erdos-741-i": "APNOutputs/ErdosProblems/erdos_741.parts.i.lean",
    "erdos-741-ii": "APNOutputs/ErdosProblems/erdos_741.parts.ii.lean",
    "erdos-846": "APNOutputs/ErdosProblems/erdos_846.lean",
}

NEGATIVE = {"erdos-12-ii", "erdos-125", "erdos-26-tenenbaum", "erdos-741-i", "erdos-846"}
STILL_OPEN = {"erdos-12-i", "erdos-12-ii", "erdos-138", "erdos-26-tenenbaum", "erdos-741-i", "erdos-741-ii"}


class NexusLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))

    def test_commit_and_nine_files(self) -> None:
        self.assertTrue(str(self.payload["commit"]).startswith("0647711a7118"))
        statements = self.payload["statements"]
        self.assertEqual(len(statements), 9)
        found = {item["id"]: item["file"] for item in statements}
        self.assertEqual(found, EXPECTED_FILES)

    def test_polarity_matches_the_lean_answer(self) -> None:
        for item in self.payload["statements"]:
            if item["id"] in NEGATIVE:
                self.assertEqual(item["polarity"], "negative")
                self.assertFalse(item["formal_answer"])
            else:
                self.assertEqual(item["polarity"], "affirmative")
                self.assertTrue(item["formal_answer"])

    def test_parts_and_variants_do_not_close_the_catalog_entry(self) -> None:
        for item in self.payload["statements"]:
            if item["id"] in STILL_OPEN:
                self.assertFalse(item["closes_catalog_problem"], item["id"])
        closed = {item["id"] for item in self.payload["statements"] if item["closes_catalog_problem"]}
        self.assertEqual(closed, {"erdos-125", "erdos-152", "erdos-846"})

    def test_erdos_straus_is_not_in_the_solved_ledger(self) -> None:
        blob = LEDGER.read_text(encoding="utf-8").lower()
        self.assertNotIn("erdos-straus", blob)
        self.assertNotIn("catalog_id: 242", blob)


if __name__ == "__main__":
    unittest.main()
