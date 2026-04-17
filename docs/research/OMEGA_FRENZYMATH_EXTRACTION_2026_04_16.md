---
title: "OMEGA FrenzyMath Extraction"
status: active
version: "1.0.0"
last_updated: "2026-04-16"
date: "2026-04-16"
role: evidence
audience: internal
tags: [omega, extraction, rethlas, archon, formal-verification, conjecture]
evidence_class: E1+E2
confidence: C2
---

# OMEGA FrenzyMath Extraction (April 16, 2026)

## Purpose

This extraction pass integrates reusable architecture and workflow signals from the
FrenzyMath stack into OMEGA's standalone research pipeline.

Target sources provided by the operator:

1. CRC Substack commentary page
2. `frenzymath/Rethlas`
3. `frenzymath/Archon`
4. `frenzymath/Anderson-Conjecture`
5. FrenzyMath conjecture technical post

The extraction is evidence-scoped: primary authority is the arXiv paper and
maintained repositories. Commentary pages are treated as secondary context only.

## Sources and Evidence Class

| Source | Type | Evidence class | Safe use in OMEGA |
| --- | --- | --- | --- |
| https://arxiv.org/abs/2604.03789 | primary paper | E1 | formal citation for architecture and claims |
| https://github.com/frenzymath/Rethlas | maintained repository | E1 | generation+verification split patterns, memory channeling |
| https://github.com/frenzymath/Archon | maintained repository | E1 | plan/prover/review staged orchestration, project-level Lean workflow |
| https://github.com/frenzymath/Anderson-Conjecture | maintained repository | E1 | statement/proof separation, comparator-based independent verification contract |
| https://frenzymath.com/blog/conjecture/ | project technical blog (paper mirror) | E2 | navigation and implementation narrative; cross-check against arXiv/repo |
| https://chinaresearchcollective.substack.com/p/a-new-breakthrough-in-ai-solving | commentary / translation | E2 | contextual signal only; not a primary claim source |

## Verified Reusable Signals

### 1. Dual-lane solving architecture (informal + formal)

- Signal: split natural-language discovery from formal verification into separate
  agent lanes.
- OMEGA adoption status: **adopt**.
- OMEGA mapping: preserve `experiment` (informal discovery) and `prove`
  (formalization/verification) as separate stages in orchestrator flows.

### 2. Strict verifier verdict contract

- Signal: verifier returns `correct` iff no critical errors and no gaps.
- OMEGA adoption status: **extend**.
- OMEGA mapping: align proof-result semantics so E2 proof artifacts are never
  promoted to stronger claims without explicit verifier closure.

### 3. Run-local persistent memory channels

- Signal: channelized JSONL memory (`events`, failures, checks, reports) per run.
- OMEGA adoption status: **extend**.
- OMEGA mapping: strengthen `experiments/ledger.yaml` + `artifacts/prover-results/`
  to keep run-scoped failure/repair traces queryable.

### 4. Statement trust separated from proof trust

- Signal: verifier checks statement declaration independently from full proof
  replay (challenge-file style).
- OMEGA adoption status: **adopt**.
- OMEGA mapping: for high-value theorem outputs, maintain a short
  statement-spec artifact and a separate machine-check replay artifact.

### 5. Independent kernel cross-check as optional assurance tier

- Signal: Lean-kernel replay plus optional second-kernel verification path.
- OMEGA adoption status: **build (optional advanced tier)**.
- OMEGA mapping: treat independent-kernel checks as a high-assurance add-on,
  not as baseline requirement for every run.

### 6. Long-horizon project observability

- Signal: explicit stage state files, iteration logs, and dashboard surfaces for
  auditability.
- OMEGA adoption status: **extend**.
- OMEGA mapping: keep orchestrator and evidence flows auditable at iteration
  boundaries; preserve state transitions in local artifacts.

## Non-portable or Restricted Signals

1. Unsafe unattended execution flags from donor scripts are **not** imported as
   default operating mode in OMEGA.
2. Marketing-level language from commentary sources is **not** admitted as claim
   evidence.
3. Model-specific superiority claims from non-paper sources remain **E2 only**.

## Adopt / Extend / Build Summary

| Decision | Items |
| --- | --- |
| Adopt | dual-lane architecture, statement/proof separation, strict verifier closure rule |
| Extend | run memory channels, audit logs, staged orchestration signals |
| Build | optional independent-kernel cross-check lane |
| Reject | unsafe execution defaults, commentary-only capability claims |

## OMEGA Surfaces Updated by This Extraction

- `Docs/reports/EXTRACTION_REPORT.md`
- `Docs/protocol/research-intelligence-stack.md`
- `Docs/research/OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md`
- `Docs/research/OMEGA_FRENZYMATH_EXTRACTION_2026_04_16.md` (this file)

## Next Execution Candidates

1. Add explicit `proof_result_status` promotion gates (`draft -> verifier-checked ->
   formally-checked`) in OMEGA proof artifacts.
2. Add optional challenge-spec artifact template for theorem-level outputs.
3. Add run-level `failure-pattern` channel to complement `experiments/ledger.yaml`.
