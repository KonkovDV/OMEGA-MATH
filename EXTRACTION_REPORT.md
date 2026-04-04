# OMEGA Extraction Report

Date: 2026-04-04
Status: initial seed complete

## Scope

This workspace seeds an OMEGA research surface for open mathematics:

- a machine-readable registry of selected open problems
- a triage matrix ranked by AI amenability
- operational protocol docs for agent-led investigation
- initial team configuration files for research orchestration

## Sources Used

1. Wikipedia, List of unsolved problems in mathematics
   Role: master taxonomy and initial problem inventory
   Snapshot basis: page content fetched on 2026-04-04
2. Denario, arXiv:2510.26887
   Role: multi-agent paper-writing pattern
3. CMBAgent, arXiv:2507.07257 (Xu et al., 2025)
   Role: planner-executor control pattern for scientific workflows
   Secondary: arXiv:2412.00431 (Laverick et al., 2024)

## What Was Extracted

- domain-level registry files under math/registry/domains/
- one collection index for Millennium Prize Problems
- a global triage queue under math/registry/triage-matrix.yaml
- protocol docs under math/protocol/
- agent configuration files under math/agents/

## Current Coverage Level

The registry is intentionally curated rather than exhaustive.

Included now:
- highest-signal flagship problems across major domains
- computationally amenable problems prioritized for early agent work
- representative foundational problems for long-horizon tracking

Not yet complete:
- full one-to-one transcription of every Wikipedia entry
- notebook collections split into separate files
- problem provenance beyond seed-level references
- formal theorem-prover encodings

## Extraction Rules

- Problem statements were normalized into concise paraphrases.
- AI triage is based on current practical amenability, not prestige.
- Open, partially resolved, and historically disproved items are labeled distinctly where needed.
- The registry prefers stable identifiers and short problem summaries over encyclopedic detail.

## Known Gaps

1. Some domains remain grouped in math/registry/domains/other-domains.yaml instead of separate files.
2. Named collections beyond Millennium are not yet split into dedicated collection YAML files.
3. Partial-results sections are sparse and intended for incremental enrichment.
4. No execution code is included yet; this seed is protocol-plus-registry only.

## Recommended Next Additions

1. ~~Split grouped domains into dedicated files~~ — ✅ Done (April 2026): computer-science, set-theory, probability-theory, game-theory, model-theory
2. ~~Add collection indexes for Hilbert, Landau, and Smale problems~~ — ✅ Done (April 2026)
3. ~~Introduce a registry index file with coverage statistics~~ — ✅ Done: registry/index.yaml
4. Add experiment templates for T1 and T2 problems.
5. Add a paper template and reproducibility manifest.
6. Add Erdős problems collection (~50 problems, highest community activity).

## Output Intent

This extraction is designed to support a next step of actual research automation, not just documentation. The docs and YAML files are structured to be consumed by future orchestration code, scripts, or agent runners.
