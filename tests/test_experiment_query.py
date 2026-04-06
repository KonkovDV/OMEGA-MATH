#!/usr/bin/env python3
"""Unit tests for the OMEGA experiment query layer."""

from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from experiment_query import query_ledger, query_global_index  # type: ignore


def _make_run(
    run_id: str,
    problem_id: str = "goldbach",
    route: str = "experiment-first",
    status: str = "completed",
    verdict: str | None = "positive",
    agent: str = "experimentalist",
    started: str = "2026-03-01T10:00:00Z",
    finished: str | None = "2026-03-01T11:00:00Z",
    artifacts: list[dict[str, Any]] | None = None,
    description: str = "bounded search",
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "problem_id": problem_id,
        "route": route,
        "status": status,
        "verdict": verdict,
        "agent": agent,
        "started": started,
        "finished": finished,
        "parameters": {"description": description},
        "artifacts": artifacts or [],
        "parent_run": None,
        "notes": None,
    }


SAMPLE_LEDGER: list[dict[str, Any]] = [
    _make_run("goldbach-20260301-001", verdict="negative", route="experiment-first",
              started="2026-03-01T10:00:00Z", finished="2026-03-01T11:00:00Z",
              artifacts=[{"path": "artifacts/log1.txt", "type": "log"}]),
    _make_run("goldbach-20260302-001", verdict="inconclusive", route="proof-first",
              started="2026-03-02T09:00:00Z", finished="2026-03-02T12:00:00Z", agent="prover",
              artifacts=[{"path": "artifacts/proof.lean", "type": "proof-draft"}]),
    _make_run("goldbach-20260310-001", verdict="positive", route="experiment-first",
              started="2026-03-10T08:00:00Z", finished="2026-03-10T09:00:00Z",
              artifacts=[{"path": "artifacts/data.csv", "type": "dataset"},
                         {"path": "artifacts/plot.png", "type": "plot"}]),
    _make_run("goldbach-20260315-001", status="running", verdict=None, route="proof-first",
              started="2026-03-15T14:00:00Z", finished=None, agent="prover"),
]


class TestQueryLedger(unittest.TestCase):
    """Tests for query_ledger() over an in-memory ledger list."""

    def test_no_filters_returns_all(self) -> None:
        results = query_ledger(SAMPLE_LEDGER)
        self.assertEqual(len(results), 4)

    def test_filter_by_route(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, route="proof-first")
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["route"], "proof-first")

    def test_filter_by_verdict(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, verdict="positive")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["run_id"], "goldbach-20260310-001")

    def test_filter_by_status(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, status="running")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["run_id"], "goldbach-20260315-001")

    def test_filter_by_agent(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, agent="prover")
        self.assertEqual(len(results), 2)

    def test_filter_by_artifact_type(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, artifact_type="proof-draft")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["run_id"], "goldbach-20260302-001")

    def test_filter_by_date_after(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, after="2026-03-09")
        self.assertEqual(len(results), 2)

    def test_filter_by_date_before(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, before="2026-03-02")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["run_id"], "goldbach-20260301-001")

    def test_filter_by_date_range(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, after="2026-03-02", before="2026-03-11")
        self.assertEqual(len(results), 2)

    def test_combined_filters(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, route="experiment-first", verdict="negative")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["run_id"], "goldbach-20260301-001")

    def test_no_match_returns_empty(self) -> None:
        results = query_ledger(SAMPLE_LEDGER, verdict="positive", route="proof-first")
        self.assertEqual(len(results), 0)

    def test_filter_by_problem_id(self) -> None:
        mixed = SAMPLE_LEDGER + [_make_run("twin-primes-20260301-001", problem_id="twin-primes")]
        results = query_ledger(mixed, problem_id="twin-primes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["problem_id"], "twin-primes")


class TestQueryGlobalIndex(unittest.TestCase):
    """Tests for query_global_index() over the experiment-index.yaml surface."""

    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent / "_test_query_workspace"
        if self.repo_root.exists():
            shutil.rmtree(self.repo_root)
        active = self.repo_root / "research" / "active"
        active.mkdir(parents=True)

        # Create two problem workspaces with ledgers
        for pid, verdict, runs in [("goldbach", "positive", 3), ("twin-primes", "inconclusive", 1)]:
            pdir = active / pid / "experiments"
            pdir.mkdir(parents=True)
            ledger = [_make_run(f"{pid}-20260301-{i:03d}", problem_id=pid,
                                verdict=verdict if i == runs else "negative")
                      for i in range(1, runs + 1)]
            (pdir / "ledger.yaml").write_text(
                yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8"
            )

        # Write a global index
        self.index_path = active / "experiment-index.yaml"
        index: list[dict[str, Any]] = [
            {"problem_id": "goldbach", "latest_run": "goldbach-20260301-003",
               "latest_verdict": "positive", "total_runs": 3, "active_route": "experiment-first",
               "current_stage": "results", "current_owner": "experimentalist", "workflow_status": "ready",
               "blocked": False, "active_run_id": None, "last_updated": "2026-03-01T12:00:00Z"},
            {"problem_id": "twin-primes", "latest_run": "twin-primes-20260301-001",
               "latest_verdict": "inconclusive", "total_runs": 1, "active_route": "proof-first",
               "current_stage": "plan", "current_owner": "planner", "workflow_status": "blocked",
               "blocked": True, "active_run_id": "twin-primes-20260301-001", "last_updated": "2026-03-01T12:00:00Z"},
        ]
        self.index_path.write_text(yaml.safe_dump(index, sort_keys=False), encoding="utf-8")

    def tearDown(self) -> None:
        if self.repo_root.exists():
            shutil.rmtree(self.repo_root)

    def test_query_all(self) -> None:
        results = query_global_index(self.repo_root)
        self.assertEqual(len(results), 2)

    def test_query_by_problem_id(self) -> None:
        results = query_global_index(self.repo_root, problem_id="goldbach")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["problem_id"], "goldbach")

    def test_query_by_verdict(self) -> None:
        results = query_global_index(self.repo_root, verdict="inconclusive")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["problem_id"], "twin-primes")

    def test_query_by_stage(self) -> None:
        results = query_global_index(self.repo_root, stage="plan")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["problem_id"], "twin-primes")

    def test_query_blocked_only(self) -> None:
        results = query_global_index(self.repo_root, blocked_only=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["workflow_status"], "blocked")

    def test_query_by_route(self) -> None:
        results = query_global_index(self.repo_root, route="experiment-first")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["problem_id"], "goldbach")

    def test_query_no_match(self) -> None:
        results = query_global_index(self.repo_root, verdict="positive", problem_id="twin-primes")
        self.assertEqual(len(results), 0)

    def test_query_problem_ledger_from_disk(self) -> None:
        """query_ledger can be called with a loaded per-problem ledger from disk."""
        ledger_path = self.repo_root / "research" / "active" / "goldbach" / "experiments" / "ledger.yaml"
        ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
        results = query_ledger(ledger, verdict="positive")
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
