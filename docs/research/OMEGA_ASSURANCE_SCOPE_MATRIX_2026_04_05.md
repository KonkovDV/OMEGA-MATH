---
title: "OMEGA Assurance Scope Matrix"
status: active
version: "1.0.0"
last_updated: "2026-04-05"
role: evidence
audience: internal
---

# OMEGA Assurance Scope Matrix

## Purpose

This matrix defines what OMEGA can currently claim to check, by what method, and what remains explicitly out of scope.

Use it to prevent magical assurance wording.

## Reading Guide

- `Implemented` means the repo contains an actual surface for the behavior.
- `Bounded` means the surface exists but is narrow and should not be generalized.
- `Planned` means it is not yet delivered.

## Matrix

| Claim area | Checked property | Evidence method | Current status | Excluded failure modes | Human oversight required | Sector notes |
| --- | --- | --- | --- | --- | --- | --- |
| Registry integrity | problem records and overlays can be validated structurally | local schema, validation scripts, collection cross-links, audit findings | Implemented, bounded | does not prove research novelty or problem correctness beyond recorded fields | low | useful across all sectors as metadata discipline |
| Workflow control | per-problem stage transitions can be materialized and advanced deterministically | workflow controller, workflow-state files, run ledger | Implemented, bounded | does not prove that the chosen workflow is optimal or commercially valuable | medium | strongest value today is operational traceability |
| Experiment provenance | runs, artifacts, and evidence bundles can be recorded and packaged | runner surfaces, experiment index, evidence bundle generation, checksum capture | Implemented, bounded | does not guarantee artifact completeness or scientific validity of conclusions | medium | strong for research-software positioning |
| Lean execution | Lean projects and files can be checked or built locally | Lean adapter commands and starter template | Implemented, bounded | does not imply automatic theorem discovery, full proof authoring, or universal formal coverage | high | supports proof-oriented workflows, not blanket assurance |
| SAT/SMT analysis | bounded logical or counterexample-style solver workflows can run | solver adapter | Implemented, bounded | does not prove global correctness of arbitrary business systems | high | useful for narrow logic obligations |
| CAS support | symbolic and algebraic computations can be executed reproducibly | CAS adapter | Implemented, bounded | does not replace full mathematical proof or customer-grade validation | high | useful for exploration, not final assurance alone |
| Searchable run history | prior experiments can be queried | query surface and experiment index | Implemented, bounded | does not create a moat by itself and does not imply successful outcome quality | low | helps operator efficiency |
| Citation and research packaging | repository and artifacts can be made more legible to research audiences | `CITATION.cff`, packaging docs, research object guidance | Implemented, bounded | does not prove novelty, correctness, or publication acceptance | medium | useful for academic and OSS trust surfaces |
| LLM-backed proof search | model-routed proof attempts through LeanCopilot or similar stacks | no full runtime wiring yet | Planned | cannot be claimed externally as delivered capability | high | keep as roadmap only |
| Enterprise assurance workflow | reusable customer-facing review packet for high-risk logic | startup memo plus evidence packet draft only | Partially implemented, mostly planned | no production tenancy, billing, auth, customer workflow, or SLAs | high | current best fit is pilot or design-partner preparation |
| Regulated-sector readiness | sector-specific compliance and approval pathways | no sector control matrix yet | Planned | no medtech, aerospace, or banking readiness claim is supportable | very high | expansion only, not beachhead |

## Safe Narrative Transformations

Use these transformations when writing startup materials.

Unsafe:
- `OMEGA proves customer code is correct.`

Safe:
- `OMEGA is designed to support bounded, machine-checkable assurance workflows for selected logic surfaces.`

Unsafe:
- `OMEGA guarantees no hallucinations.`

Safe:
- `OMEGA aims to reduce unverifiable reasoning by routing work through explicit artifacts, bounded proving paths, and operator-visible evidence.`

Unsafe:
- `OMEGA is ready for mission-critical deployment.`

Safe:
- `OMEGA currently supports internal and pilot-stage assurance workflows; regulated and mission-critical deployment remains out of scope.`

## Current External Claim Boundary

The strongest externally tolerable claim today is:

OMEGA provides a bounded, evidence-oriented workflow for high-risk logic exploration and proof-support experiments.

Anything stronger requires:
- pilot evidence
- sector-specific controls
- clearer proof of commercial delivery

## Required Human Review Gates

The following should stay human-approved even if tooling improves:

1. selection of proof obligations that matter commercially
2. interpretation of partial proof results
3. external claims about correctness or safety
4. any sector-specific compliance statement
5. any investor statement about moat or market readiness

## Immediate Application

When revising OMEGA startup docs:

1. keep only claim areas marked `Implemented, bounded` in the core product story
2. move `Planned` items into roadmap sections
3. explicitly note excluded failure modes whenever assurance language appears