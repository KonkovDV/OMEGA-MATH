---
title: "OMEGA Internal Evidence Packet"
status: active
version: "1.0.0"
last_updated: "2026-04-05"
role: evidence
audience: internal
---

# OMEGA Internal Evidence Packet

## Purpose

This document maps startup-facing OMEGA claims to current repository reality.

Use it to answer one question:

What can we honestly say exists today, what is only scaffolded, and what is still aspirational?

## Repository Boundary

OMEGA currently exists as the standalone `math/` repository surface inside the broader workspace.

Important boundary conditions:
- separate git boundary from the main runtime
- no production dependency on the parent `src/` tree
- local Python package and CLI surface
- local protocol and research docs
- local registry, workflow, and evidence artifacts

This means OMEGA should currently be positioned as research software plus bounded operator tooling, not as a deployed enterprise platform.

## Implemented Surfaces, C2

Based on `math/README.md` and `math/docs/research/OMEGA_HYPER_DEEP_AUDIT_2026_04_04.md`, the following surfaces exist now:

1. machine-readable open-problem registry
2. triage matrix for prioritized exploration
3. protocol documents for research, verification, and publication
4. installable Python package surface via `pyproject.toml`
5. bounded local runner for experiment bookkeeping
6. deterministic workflow controller for per-problem stage transitions
7. experiment-history query surface
8. Lean 4 execution adapter
9. SAT/SMT execution adapter
10. CAS execution adapter
11. evidence-bundle generation with checksums
12. CITATION surface for research-software legibility
13. collection overlays and canonical registry separation
14. CI and registry validation rails

## Audit-Confirmed Improvements, C2

The April 2026 audit recorded these meaningful fixes and upgrades:
- corrected registry data drift
- improved collection-to-registry cross-linking
- clearer validation remediation in CI
- exact Python dependency pinning for validator rail
- `CITATION.cff` added for repository citation legibility
- clearer separation between canonical registry and quick-reference overlays
- bounded runner and workflow synchronization improvements
- experiment index generation
- standalone Python tests for runner and query surfaces
- operator runbook updated for real CLI workflow

These are real product-quality improvements, but they are still internal readiness signals rather than customer traction.

## What Exists But Is Still Bounded

### Lean and prover lane

What exists:
- Lean starter template
- Lean adapter commands
- prover-result contract
- bootstrap docs

What that means:
- OMEGA can structure prover-facing work and persist prover-visible outputs

What it does not mean:
- automated domain-complete proof authoring
- LLM-routed proof search at production quality
- broad proof coverage across arbitrary customer codebases

### Solver and CAS lanes

What exists:
- SAT/SMT adapter
- CAS adapter
- operator-facing CLI entrypoints

What that means:
- OMEGA can run bounded symbolic and algebraic support workflows

What it does not mean:
- end-to-end autonomous theorem discovery
- industrial-scale solver orchestration across many tenants

### Workflow and evidence lane

What exists:
- workflow-state materialization
- stage progression
- run ledgers
- experiment index
- evidence bundle generation

What that means:
- OMEGA's strongest current asset is operator-visible workflow discipline

What it does not mean:
- customer-ready multi-user SaaS control plane
- full autonomous agent team orchestration in production

## Not Yet Implemented, C1

These gaps remain material:

1. no real LLM-backed proof-search routing through LeanCopilot or similar model-specific proving stack
2. no literature retrieval adapter layer fully wired into runtime execution
3. no pilot-customer evidence
4. no external case-study proof of time saved, bugs found, or risk reduced
5. no compliance control matrix for finance, medtech, or aerospace
6. no enterprise tenancy, auth, billing, or deployment boundary specific to OMEGA
7. no proven distribution moat or data flywheel

## Evidence Classification

### C2 statements we can support now

- OMEGA is a structured research-software environment with bounded operator tooling.
- OMEGA supports experiment bookkeeping, query, workflow control, and evidence bundling.
- OMEGA already integrates formal-methods-oriented and symbolic-computation-oriented surfaces at the tool-contract level.
- OMEGA is materially more than a static idea document or registry-only repo.

### C1 statements we should keep as hypotheses

- OMEGA is ready for enterprise deployment.
- OMEGA can guarantee correctness of customer-critical logic.
- OMEGA already outperforms specialist formal verification vendors.
- OMEGA can serve regulated industries without additional compliance work.
- OMEGA has demonstrated product-market fit.

## Current Best External Story

If speaking externally today, the most honest product story is:

OMEGA is an operator-first verification workflow substrate for high-risk logic exploration and bounded formal-assurance experiments.

That story is stronger than:
- "just a research registry"

And weaker than:
- "production-ready zero-hallucination AI lab"

## Commercial Readiness Snapshot

### Technical readiness

Current level:
- meaningful internal substrate exists
- workflow discipline exists
- evidence packaging exists

### Commercial readiness

Current level:
- pre-pilot

### Compliance readiness

Current level:
- documentation-aware only

### Market readiness

Current level:
- wedge hypothesis only

## External-Use Guardrails

Before using OMEGA startup materials externally, require these checks:

1. every number source-tagged
2. every major claim labeled C1, C2, or C3
3. one wedge only
4. one buyer only per memo version
5. no absolute assurance wording
6. no regulated-sector readiness claim without a control matrix

## Next Proof Points

The highest-value next proof points are:

1. two to three bounded public case studies
2. one pilot-ready assurance packet for a narrow logic domain
3. one market-source ledger backing any TAM or loss figures
4. one assurance scope matrix defining checked properties and excluded failure modes

## Bottom Line

OMEGA already has enough substance to support an internal seed thesis.

OMEGA does not yet have enough substance to support external claims of universal verification, mission-critical deployment readiness, or a proven market moat.

The correct move is not to abandon the startup thesis.

The correct move is to narrow it, source it, and pair every narrative artifact with explicit evidence.