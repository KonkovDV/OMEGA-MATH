---
author: GitHub Copilot
date: "2026-04-21"
description: "Design for wiring synthetic packet scaffolding and global artifact-type discovery into OMEGA"
last_updated: "2026-04-21"
status: active
tags:
- omega
- synthetic-reasoning
- scaffold
- experiment-index
- query
title: OMEGA Synthetic Runtime Integration Design
version: 1.0.0
---

# OMEGA Synthetic Runtime Integration Design

## Goal

Finish the first executable slice of OMEGA's synthetic reasoning lane by:

1. creating synthetic packet files during workspace scaffolding,
2. surfacing synthetic artifact types in the global experiment index,
3. allowing global query filtering by artifact type.

## Trigger

The Simula-driven synthetic lane now exists in protocol docs and ledger enums, but two runtime gaps remain:

- `scaffold_problem.py` does not create the packet files it now recommends,
- `experiment-index.yaml` and `experiment_query.py` cannot expose or filter the latest artifact types per problem.

## Decision

Use the smallest sound implementation:

- scaffold synthetic packet stubs by default for all new workspaces,
- add `latest_artifact_types` to generated global index entries,
- extend `query_global_index()` and CLI filtering to use that field.

## Why This Path

1. It keeps the current OMEGA workspace contract internally consistent.
2. It avoids inventing a new runtime or command surface.
3. It upgrades discovery and filtering without changing the meaning of existing runs.

## Files

- `scripts/scaffold_problem.py`
- `scripts/omega_runner.py`
- `scripts/experiment_query.py`
- `tests/test_scaffold_problem.py`
- `tests/test_experiment_query.py`
- `tests/test_omega_runner.py`
- `protocol/experiment-ledger-spec.md`
- `protocol/operator-runbook.md`

## Validation

- changed-file diagnostics
- focused Python tests for scaffold/query/runner slices
- docs closure rail after protocol doc updates
