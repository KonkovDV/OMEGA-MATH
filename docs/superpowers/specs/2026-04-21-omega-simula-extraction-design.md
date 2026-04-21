---
author: GitHub Copilot
date: "2026-04-21"
description: "Design for integrating the Simula paper into OMEGA as a methodological donor without overclaiming runtime capability"
last_updated: "2026-04-21"
status: active
tags:
- omega
- simula
- extraction
- synthetic-data
- methodology
- docs
title: OMEGA Simula Extraction Design
version: 1.0.0
---

# OMEGA Simula Extraction Design

## Goal

Integrate the TMLR paper *Reasoning-Driven Synthetic Data Generation and Evaluation*
into OMEGA as a methodological donor for future synthetic reasoning and benchmark
generation work, while keeping OMEGA's current claim boundary intact: this is not a
proof-verification or theorem-discovery upgrade.

## Trigger

The operator requested a study plus extraction of the OpenReview paper `NALsdGEPhB`
into the OMEGA project. The repository already has an established pattern for external
methodology intake: create a dated extraction memo and wire the conclusions into the
active protocol, bibliography, and extraction report.

## Evidence Base

Internal surfaces reviewed:

- `math/PROTOCOL.md`
- `math/protocol/research-intelligence-stack.md`
- `math/research/OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md`
- `math/docs/reports/EXTRACTION_REPORT.md`
- `math/docs/research/OMEGA_FRENZYMATH_EXTRACTION_2026_04_16.md`

External surface reviewed:

- OpenReview `NALsdGEPhB` with title, abstract, public reviews, author responses, and
  acceptance status

## Decision

Use a docs-first extraction, not a runtime implementation.

Reasoning:

1. The paper is a methodology donor, not a drop-in repository or executable runtime.
2. OMEGA does not yet have a justified, mature synthetic-data execution lane that would
   make a direct code import sound.
3. The safest immediate value is to encode the paper's reusable logic in OMEGA's active
   documentation so future synthetic reasoning work inherits the right constraints.

## Reusable Mapping

### Adopt

- explicit taxonomy-first generation instead of free-form prompt churn
- critic-gated filtering before promotion into synthetic assets
- separate coverage and complexity evaluation instead of score-only reporting

### Extend

- reinterpret the paper's synthetic-data workflow for mathematical prompt families,
  benchmark packs, and future synthetic reasoning corpora
- preserve the paper's non-monotonic lesson: more scale or more complexity does not
  automatically improve downstream value

### Reject

- any reading that upgrades synthetic reasoning data into theorem correctness,
  mathematical novelty, or proof closure
- any transfer claim from the paper's multimodal data domain directly into research
  mathematics without local validation

## Files To Change

- `math/PROTOCOL.md`
- `math/protocol/research-intelligence-stack.md`
- `math/research/OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md`
- `math/docs/reports/EXTRACTION_REPORT.md`
- `math/docs/research/OMEGA_SIMULA_EXTRACTION_2026_04_21.md`

## Validation Plan

1. Run changed-file diagnostics.
2. Run the docs closure rail from the workspace root: `sync:metrics`, `sync:metrics:check`, `agent:preflight`.
3. If docs closure reveals unrelated pre-existing failures, report them separately and do
   not rewrite unrelated OMEGA content unless the failure is directly caused by this intake.