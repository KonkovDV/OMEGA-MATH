---
title: "OMEGA 100/100 Upgrade Prompt 2026-04-04"
status: "active"
version: "1.0.0"
last_updated: "2026-04-04"
tags: [omega, prompt, upgrade, research, startup]
---

# OMEGA 100/100 Upgrade Prompt

Use this prompt with an AI programmer that can read and edit the repository directly.

```text
You are auditing and upgrading the standalone repository `math/` inside the MicroPhoenix workspace.

Mission:
Raise OMEGA from a strong research seed to a 100/100 research-software foundation without overclaiming current capabilities.

Operating constraints:
1. Treat `math/` as a standalone repository with its own git, CI, registry, protocol, and citation surface.
2. Do not blur implemented truth, planned direction, and external donor inspiration.
3. Keep canonical truth in `registry/domains/*.yaml`; collection files are quick-reference overlays.
4. Prefer minimal, high-signal diffs over architecture theater.
5. Every claim about tooling, theorem proving, packaging, reproducibility, citation, or startup readiness must be grounded either in current repo state or current official documentation.

Primary goals:
1. Improve OMEGA as research software.
2. Improve OMEGA as an autonomous-math-lab substrate.
3. Improve OMEGA as a future startup/spinoff candidate.

Deliverables:
1. A verified gap analysis with severity-ranked findings.
2. A concrete implementation backlog split into must-fix, should-fix, and can-add.
3. Code and doc changes that meaningfully improve the repository now.
4. A final verification report with explicit evidence.

What to inspect first:
- `README.md`
- `PROTOCOL.md`
- `EXTRACTION_REPORT.md`
- `registry/schema.json`
- `registry/index.yaml`
- `registry/domains/*.yaml`
- `registry/collections/*.yaml`
- `scripts/validate-registry.py`
- `scripts/generate-index.py`
- `scripts/scaffold-problem.py`
- `.github/workflows/validate.yml`
- `research/OMEGA_HYPER_DEEP_AUDIT_2026_04_04.md`

What to use from the parent MicroPhoenix project:
- Scientific Publication Protocol surfaces under `docs/scientific/**`
- MCP SPP / Docs / Extraction / Code-Intelligence ideas when they map cleanly
- startup governance under `docs/protocols/STARTUP_SPINOFF_PROTOCOL.md` and `docs/startups/**`
- research-related DI and MAS vocabulary only when it helps OMEGA stay more rigorous

Do not do these things:
- Do not claim that OMEGA is already fully autonomous or publication-ready if the runtime loop does not exist.
- Do not vendor huge external runtimes just because Denario or CMBAgent exist.
- Do not introduce a packaging surface that cannot actually build.
- Do not replace canonical registry records with collection overlays.

Required upgrade directions:

A. Registry correctness
- Eliminate semantic drift in canonical records.
- Make overlay collections point back to canonical records when possible.
- Strengthen validation, error messages, and operator guidance.

B. Research execution substrate
- Design a local-first experiment ledger.
- Add reproducibility contracts per active problem.
- Prepare a bounded runner model for `experiment-first`, `proof-first`, and `survey-first` routes.

C. Formal proving lane
- Add a realistic Lean 4 integration plan based on official Lean/mathlib workflow.
- Start from workspace bootstrap and deterministic buildability, not magical theorem proving.

D. Publication-grade research hygiene
- Use `CITATION.cff`, reproducibility manifests, artifact lineage, and explicit evidence classes.
- Reuse the strongest applicable pieces from `docs/scientific/**`.

E. Startup readiness
- Frame OMEGA as research infrastructure software, not as AGI hype.
- Use evidence-first startup language with explicit confidence labels.
- Identify the shortest path from internal research system to externally legible product candidate.

Implementation standard:
- Fix root causes.
- Keep the repo honest.
- Prefer deterministic and inspectable workflows.
- Add docs only when they reduce ambiguity for the next operator.
- Validate every meaningful change.

Verification required before completion:
- changed-file diagnostics
- registry validation passes
- index generation is clean
- scaffolder dry-run works
- any docs lane or preflight lane required by the surrounding workspace is green

Final output format:
1. Findings first, ordered by severity.
2. Then implemented changes.
3. Then remaining backlog.
4. Then exact verification evidence.
```