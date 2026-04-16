#!/usr/bin/env python3
"""Tests for EinsteinArena collection import script."""

from __future__ import annotations

import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import import_einstein_arena  # type: ignore


SAMPLE_README = """
# EinsteinArena state-of-the-art results

## Problems (Last update: April 1, 2026)

| Problem | Objective | Our Result | Previous Best | Improvement |
|---------|-----------|-----------|---------------|-------------|
| [Erdős' Minimum Overlap](erdos-minimum-overlap/) | minimize | **0.380871** | 0.380876 | −0.000005 |
| [Tammes Problem (n = 50)](tammes-problem/) | maximize | **0.5134721** | 0.5134719 | +0.0000002 |
| [Second Autocorrelation Inequality](second-autocorrelation/) | maximize | **0.961206**\\* | 0.962580† | — |
"""


class EinsteinArenaImportTests(unittest.TestCase):
    def test_clean_metric_normalizes_markdown_and_symbols(self) -> None:
        self.assertEqual(import_einstein_arena.clean_metric("**1.280932**\\*"), "1.280932")
        self.assertEqual(import_einstein_arena.clean_metric("0.962580†"), "0.962580")
        self.assertEqual(import_einstein_arena.clean_metric("−0.000005"), "-0.000005")
        self.assertEqual(import_einstein_arena.clean_metric("—"), "n/a")

    def test_parse_problem_rows_extracts_expected_fields(self) -> None:
        rows = import_einstein_arena.parse_problem_rows(SAMPLE_README)
        self.assertEqual(len(rows), 3)

        self.assertEqual(rows[0].name, "Erdős' Minimum Overlap")
        self.assertEqual(rows[0].slug, "erdos-minimum-overlap")
        self.assertEqual(rows[0].objective, "minimize")
        self.assertEqual(rows[0].our_result, "0.380871")
        self.assertEqual(rows[0].previous_best, "0.380876")
        self.assertEqual(rows[0].improvement, "-0.000005")

        self.assertEqual(rows[2].slug, "second-autocorrelation")
        self.assertEqual(rows[2].our_result, "0.961206")
        self.assertEqual(rows[2].previous_best, "0.962580")
        self.assertEqual(rows[2].improvement, "n/a")

    def test_parse_problem_rows_handles_extra_columns(self) -> None:
        readme = """
| Rank | Problem | Objective | Our Result | Previous Best | Improvement | Notes |
|------|---------|-----------|-----------|---------------|-------------|-------|
| 1 | [Tammes Problem (n = 50)](tammes-problem/) | maximize | **0.5134721** | 0.5134719 | +0.0000002 | verified |
| 2 | [Prime Number Theorem](prime-number-theorem/) | maximize | **0.994179**\\* | 0.921292 | +0.072887 | verified |
"""
        rows = import_einstein_arena.parse_problem_rows(readme)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].slug, "tammes-problem")
        self.assertEqual(rows[0].improvement, "+0.0000002")
        self.assertEqual(rows[1].slug, "prime-number-theorem")
        self.assertEqual(rows[1].our_result, "0.994179")

    def test_parse_problem_rows_handles_reordered_required_columns(self) -> None:
        readme = """
| Previous Best | Problem | Notes | Objective | Improvement | Our Result |
|---------------|---------|-------|-----------|-------------|------------|
| 0.5134719 | [Tammes Problem (n = 50)](tammes-problem/) | verified | maximize | +0.0000002 | **0.5134721** |
"""
        rows = import_einstein_arena.parse_problem_rows(readme)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].slug, "tammes-problem")
        self.assertEqual(rows[0].objective, "maximize")
        self.assertEqual(rows[0].our_result, "0.5134721")
        self.assertEqual(rows[0].previous_best, "0.5134719")

    def test_parse_problem_rows_handles_header_synonyms(self) -> None:
        readme = """
| Task | Direction | Our Score | Previous SOTA | Delta |
|------|-----------|-----------|---------------|-------|
| [Tammes Problem (n = 50)](tammes-problem/) | maximize | **0.5134721** | 0.5134719 | +0.0000002 |
"""
        rows = import_einstein_arena.parse_problem_rows(readme)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].slug, "tammes-problem")
        self.assertEqual(rows[0].objective, "maximize")
        self.assertEqual(rows[0].our_result, "0.5134721")
        self.assertEqual(rows[0].previous_best, "0.5134719")
        self.assertEqual(rows[0].improvement, "+0.0000002")

    def test_parse_problem_rows_defaults_optional_metrics_to_na(self) -> None:
        readme = """
| Problem | Objective | Our Result |
|---------|-----------|------------|
| [Tammes Problem (n = 50)](tammes-problem/) | maximize | **0.5134721** |
"""
        rows = import_einstein_arena.parse_problem_rows(readme)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].previous_best, "n/a")
        self.assertEqual(rows[0].improvement, "n/a")

    def test_parse_problem_rows_handles_non_markdown_problem_cells(self) -> None:
        readme = """
| Problem | Objective | Our Result | Previous Best | Improvement |
|---------|-----------|-----------|---------------|-------------|
| Tammes Problem (n = 50) | maximize | **0.5134721** | 0.5134719 | +0.0000002 |
| <a href=\"second-autocorrelation/\">Second Autocorrelation Inequality</a> | maximize | **0.961206** | 0.962580 | -0.001374 |
"""
        rows = import_einstein_arena.parse_problem_rows(readme)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].name, "Tammes Problem (n = 50)")
        self.assertEqual(rows[0].slug, "tammes-problem")
        self.assertEqual(rows[1].slug, "second-autocorrelation")

    def test_infer_registry_link_exact_and_alias(self) -> None:
        domain_ids = {"thomson-problem", "erdos-straus", "prime-number-theorem"}
        alias_map = {"tammes-problem": "thomson-problem"}

        self.assertIsNone(import_einstein_arena.infer_registry_link("erdos-minimum-overlap", domain_ids))
        self.assertEqual(import_einstein_arena.infer_registry_link("tammes-problem", domain_ids, alias_map), "thomson-problem")
        self.assertEqual(import_einstein_arena.infer_registry_link("prime-number-theorem", domain_ids), "prime-number-theorem")

    def test_load_aliases_from_file_merges_with_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            alias_file = Path(tmpdir) / "aliases.yaml"
            alias_file.write_text(
                "aliases:\n  tammes-problem: thomson-problem\n  custom-problem: prime-number-theorem\n",
                encoding="utf-8",
            )

            aliases = import_einstein_arena.load_aliases(alias_file)

        self.assertEqual(aliases.get("tammes-problem"), "thomson-problem")
        self.assertEqual(aliases.get("custom-problem"), "prime-number-theorem")

    def test_build_collection_respects_explicit_alias_map(self) -> None:
        rows = import_einstein_arena.parse_problem_rows(SAMPLE_README)
        aliases = {"tammes-problem": "prime-number-theorem"}
        with patch.object(import_einstein_arena, "load_domain_ids", return_value={"prime-number-theorem"}):
            payload = import_einstein_arena.build_collection(
                rows,
                "https://example.org/README.md",
                aliases=aliases,
            )

        tammes = next(p for p in payload["problems"] if p["source_problem_path"] == "tammes-problem")
        self.assertEqual(tammes.get("registry_id"), "prime-number-theorem")

    def test_build_collection_adds_registry_id_when_match_exists(self) -> None:
        rows = import_einstein_arena.parse_problem_rows(SAMPLE_README)
        with patch.object(import_einstein_arena, "load_domain_ids", return_value={"thomson-problem"}):
            payload = import_einstein_arena.build_collection(rows, "https://example.org/README.md")

        self.assertEqual(payload["collection"], "einstein-arena-benchmarks")
        self.assertEqual(payload["source"], "https://example.org/README.md")
        self.assertEqual(len(payload["problems"]), 3)

        tammes = next(p for p in payload["problems"] if p["source_problem_path"] == "tammes-problem")
        self.assertEqual(tammes.get("registry_id"), "thomson-problem")

        second = next(p for p in payload["problems"] if p["source_problem_path"] == "second-autocorrelation")
        self.assertEqual(second["improvement"], "n/a")

    def test_load_source_markdown_prefers_readme_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            local = Path(tmpdir) / "README.md"
            local.write_text("# local snapshot", encoding="utf-8")
            text = import_einstein_arena.load_source_markdown("https://example.org/readme.md", str(local))
            self.assertEqual(text, "# local snapshot")

    def test_load_source_markdown_uses_network_when_no_file(self) -> None:
        with patch.object(import_einstein_arena, "fetch_text", return_value="# remote snapshot"):
            text = import_einstein_arena.load_source_markdown("https://example.org/readme.md", None)
            self.assertEqual(text, "# remote snapshot")

    def test_copy_solution_snapshots_copies_files(self) -> None:
        rows = import_einstein_arena.parse_problem_rows(SAMPLE_README)

        with tempfile.TemporaryDirectory() as donor_tmp, tempfile.TemporaryDirectory() as out_tmp:
            donor = Path(donor_tmp)
            out_root = Path(out_tmp)

            # Create donor structure for one problem only
            sol_dir = donor / "tammes-problem" / "solutions"
            sol_dir.mkdir(parents=True)
            (sol_dir / "ours_2026.json").write_text('{"vectors": []}', encoding="utf-8")
            (sol_dir / "alphaevolve_2025.py").write_text("vectors=[]", encoding="utf-8")

            copied = import_einstein_arena.copy_solution_snapshots(rows, donor, out_root)

            self.assertIn("tammes-problem", copied)
            self.assertEqual(len(copied["tammes-problem"]), 2)
            self.assertTrue((out_root / "tammes-problem" / "solutions" / "ours_2026.json").exists())
            self.assertTrue((out_root / "tammes-problem" / "solutions" / "alphaevolve_2025.py").exists())

    def test_build_collection_includes_solution_files(self) -> None:
        rows = import_einstein_arena.parse_problem_rows(SAMPLE_README)
        with patch.object(import_einstein_arena, "load_domain_ids", return_value={"thomson-problem"}):
            payload = import_einstein_arena.build_collection(
                rows,
                "https://example.org/README.md",
                solution_files={
                    "tammes-problem": [
                        "research/benchmarks/einstein-arena/tammes-problem/solutions/ours_2026.json"
                    ]
                },
            )

        tammes = next(p for p in payload["problems"] if p["source_problem_path"] == "tammes-problem")
        self.assertEqual(tammes["solution_source"], "local-donor-checkout")
        self.assertEqual(len(tammes["solution_files"]), 1)


if __name__ == "__main__":
    unittest.main()
