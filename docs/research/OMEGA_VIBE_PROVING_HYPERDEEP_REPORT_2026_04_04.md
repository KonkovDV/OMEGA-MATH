---
title: "OMEGA Hyperdeep Report: Vibe-Proving and Modern Math Breakthroughs"
status: "active"
version: "1.0.0"
last_updated: "2026-04-04"
role: evidence
tags: [omega, mathematics, vibe-proving, formal-math, evidence]
---

# OMEGA Hyperdeep Report: Vibe-Proving and Modern Math Breakthroughs

## Scope

Этот отчёт фиксирует два слоя verified evidence по состоянию на 2026-04-04:

1. какие крупные математические прорывы 2024-2026 действительно подтверждаются проверяемыми источниками;
2. что именно доказано в arXiv:2602.18918 и какие workflow-сигналы OMEGA должен перенять из case study по vibe-proving.

Отчёт intentionally отделяет paper-backed claims от press framing и от неподтверждённых отраслевых пересказов.

## Evidence Base

### Primary papers and arXiv records checked

- arXiv:2602.18918, Verbeken et al. — consumer-LLM vibe-proving case study on Conjecture 20 of Ran and Teng
- arXiv:2601.22401, Feng et al. — semi-autonomous mathematics discovery with Gemini on Erdős problems
- arXiv:2602.10177, Feng et al. — Aletheia / autonomy framing for AI-assisted mathematics research
- arXiv:2601.14027, Liu et al. — Numina-Lean-Agent formal mathematics stack
- arXiv:2601.19532, Ballon et al. — Omni-MATH-2 / judge saturation and judge-induced noise
- arXiv:2502.17655, Wang and Zahl — 3D Kakeya result
- arXiv:2503.01800, Deng, Hani, and Ma — Hilbert's sixth problem via Boltzmann kinetic theory
- arXiv:2209.04736, Malle, Navarro, Schaeffer Fry, Tiep — Brauer's Height Zero Conjecture
- arXiv search records for the five-paper geometric Langlands proof series:
  - arXiv:2405.03599
  - arXiv:2405.03648
  - arXiv:2409.07051
  - arXiv:2409.08670
  - arXiv:2409.09856

### Institutional and editorial secondary sources checked

- VUB press release on arXiv:2602.18918
- SciTechDaily article summarizing the VUB result

### Maintained repositories checked

- `project-numina/numina-lean-agent`
- `jacopotagliabue/vibe-proving-with-llms`
- `StarExecMiami/StarExec-ARC`

## Executive Summary

1. Категория "исторически нерешаемых" задач остаётся временной, а не онтологической: verified 2024-2025 literature действительно содержит несколько очень сильных closure events или papers, которые прямо заявляют такое closure.
2. VUB case study не подтверждает fully autonomous proof verification. Она подтверждает более узкий и более важный тезис: consumer-access LLM способен materially contribute to research-level proof search on a strongly scaffolded problem, если люди жёстко контролируют correctness-critical closure.
3. Главный reusable signal для OMEGA — не лозунг "LLM сам доказал теорему", а operational loop `generate -> referee -> repair`, дополненный versioned drafts, explicit correctness obligations, bounded fresh-session critique, and regression control.
4. Open-source ecosystem April 2026 already splits into three strata:
   - natural-language research agents and autonomy studies;
   - formal theorem-proving agents around Lean;
   - infrastructure for scalable ATP or verifier-backed experimentation.
5. Judge reliability is now a first-class risk. Omni-MATH-2 shows that once models get strong enough, weak judges mask real capability differences. OMEGA must therefore treat LLM judging as diagnostic, not as proof verification.

## Verified Historical Arc

### Classical baselines

These are established historical anchor points rather than newly re-verified claims in this session:

- Fermat's Last Theorem: proved by Andrew Wiles in the 1990s via elliptic curves and modular forms.
- Poincaré Conjecture: proved by Grigori Perelman in 2002-2003 via Ricci flow with surgery.
- Kepler Conjecture: closure reinforced by formal verification, making it a key precursor for machine-checked mathematics.

### 2024-2025 breakthrough layer verified in this pass

| Topic | Verified source signal | OMEGA reading |
|-------|------------------------|---------------|
| Geometric Langlands | arXiv search results show a five-paper series by Gaitsgory and collaborators; `Proof of the geometric Langlands conjecture V` explicitly states it is the final paper in the series proving GLC | treat as a real, multi-paper human breakthrough and not as hype shorthand |
| Brauer's Height Zero Conjecture | arXiv:2209.04736 states: "We complete the proof of Brauer's Height Zero Conjecture from 1955 by establishing the open implication for all odd primes"; comments say "To appear in Annals of Math" | the user draft's high-level claim is substantially supported, but the solution is collaborative rather than attributable to one person alone |
| 3D Kakeya | arXiv:2502.17655 proves every Kakeya set in `R^3` has Minkowski and Hausdorff dimension 3; later papers call the conjecture in `R^3` recently resolved | strong confirmation of the 3D breakthrough claim |
| Hilbert's sixth problem | arXiv:2503.01800 explicitly claims rigorous derivation of fluid equations from hard-sphere particle systems and says this resolves Hilbert's sixth problem in the stated Boltzmann/Newtonian program sense | report this with the paper's own scope qualification, not as an unrestricted solution to every reading of Hilbert 6 |

## What arXiv:2602.18918 Actually Shows

### Problem statement, without press inflation

The paper is not about "geometry" in the broad journalistic sense. Its actual target is:

- Conjecture 20 of Ran and Teng (2024)
- on the exact nonreal spectral region of a 4-cycle row-stochastic nonnegative matrix family
- using Karpelevich-region ideas, trigonometric reformulation, and inequality-heavy closure

So the clean OMEGA phrasing is:

> a consumer LLM materially assisted a human-verified proof of a structured spectral-region conjecture in matrix theory.

### Auditability claims that are genuinely supported

The paper provides unusually concrete workflow evidence:

- seven shareable ChatGPT threads
- four versioned proof drafts
- explicit generate/referee/repair framing
- transcript-linked appendices and draft evolution
- a detailed division of labor between model and humans

That makes it stronger than a generic "AI helped with a theorem" press story. It is an auditable workflow paper, not just a result announcement.

### What the model did

Supported by the paper text:

- proposed an early global roadmap for the proof
- helped specialize a Dmitriev-Dynkin-style trigonometric strategy to the 4-cycle family
- contributed algebraic manipulation support, including a key factorization
- produced a Lamport-style dependency rewrite for the final exposition
- surfaced missing guard conditions when used in referee mode

### What the humans still had to do

Also supported by the paper text:

- select the problem and formulate the target theorem
- identify correctness obligations
- track branch/quadrant issues and sign conditions
- manage endpoint admissibility and long expansions
- orchestrate independent patch search
- perform final correctness-critical closure

### Press-drift normalization table

| Surface | Claim style | OMEGA normalization |
|---------|-------------|---------------------|
| SciTechDaily title | "ChatGPT solved an unproven math problem in geometry" | overstates both autonomy and field label; use the paper's matrix/spectral formulation instead |
| VUB press release | "can autonomously provide mathematical proofs" | usable only if normalized to high-autonomy proof search with human closure |
| arXiv paper | early evidence, single auditable case study, human experts essential for correctness-critical closure | this is the authority surface |

### Limitations that must remain attached to any reuse

The paper itself explicitly narrows the claim:

- one case study only
- strong prior scaffolding existed
- the proof stayed within a classical template rather than inventing a new mathematical paradigm
- early drafts contained correctness-critical mistakes
- no formal Lean/Coq/Isabelle mechanization was attempted

OMEGA must preserve these caveats whenever the case is cited.

## Workflow Signals OMEGA Should Import

### Adopt

- `generate -> referee -> repair` as the default proof-first conversational loop
- explicit correctness-obligation lists instead of vague critique
- versioned drafts for regression control
- bounded fresh-session referee passes
- parallel patch search for load-bearing gaps
- Lamport-style dependency decomposition for local checkability

### Extend locally

- persist a dedicated `input_files/proof_obligations.md` in proof-first workspaces
- separate `supporting`, `contrasting`, and `press` evidence classes in novelty and public-facing packets
- track autonomy and novelty gradation instead of binary "autonomous / not autonomous"
- route algebra-heavy obligations toward future CAS or certified inequality tooling

### Reject

- press-release autonomy phrasing as proof of correctness
- LLM-as-a-judge as a sufficient proof verifier
- any claim that consumer chat alone replaces human or formal closure
- unattributed ecosystem claims such as "Aristotle solved Erdős #124 in six hours" without primary evidence

## Open-Source Ecosystem Extraction

### Numina-Lean-Agent

Verified from arXiv:2601.14027 and the GitHub repo:

- open agentic formal-math system built around Claude Code plus a Lean MCP/LSP stack
- claims 12/12 Putnam 2025 problems solved
- reports a mathematician-facing formalization of Brascamp-Lieb inequalities
- operationally important because it shows that formal theorem proving is no longer limited to narrow, task-specific pipelines

OMEGA takeaway:

- adopt as a design reference for the future Prover lane and Lean bootstrap
- do not vendor its runtime wholesale into OMEGA today

### vibe-proving-with-llms

Verified from the GitHub repo:

- educational Python stack for a proof checker plus RL-trained proof generator
- uses a custom proof language and binary reward from a verifier
- explicitly positions itself as a build-your-own verifier-backed vibe-proving playground

OMEGA takeaway:

- useful as a minimal verifier/reward-loop reference
- not a drop-in research-level Lean or theorem-discovery stack

### StarExec-ARC

Verified from the GitHub repo:

- containerization and deployment framework for ATP systems
- supports Podman, Kubernetes, proxy provers, and scalable StarExec-style benchmarking
- relevant to future large-scale ATP or solver benchmarking workflows

OMEGA takeaway:

- adopt as infrastructure inspiration for future solver farms or ATP batch evaluation
- not needed for the current docs-and-registry-only OMEGA seed

### Gemini / Aletheia / autonomy-gradation layer

Verified from arXiv:2601.22401 and arXiv:2602.10177:

- large-scale semi-autonomous screening of open problems is already feasible
- literature collision and subconscious-plagiarism risk are real
- autonomy and novelty need graded reporting rather than raw hype labels
- human-AI interaction cards are a useful transparency idea for future OMEGA reporting

OMEGA takeaway:

- absorb the autonomy/novelty grading idea
- make literature-collision checks first-class before any novelty claim

### Omni-MATH-2 / judge saturation

Verified from arXiv:2601.19532:

- expert review found Omni-Judge wrong in most disagreements against a stronger judge on the audited dataset
- judge quality becomes the limiting factor as model quality rises

OMEGA takeaway:

- proof verification must not be delegated to a weak judge model
- reviewer passes remain necessary even when model outputs look internally coherent

## Claims Not Promoted To Active OMEGA Guidance

The following user-supplied or ecosystem claims were not promoted because the checked sources in this pass did not verify them strongly enough:

- the exact "Aristotle solved Erdős Problem #124 in 6 hours and Lean verified it in 1 minute" narrative
- any blanket claim that vibe-proving has already eliminated the human verification bottleneck
- any broad statement that the VUB result proves LLM creativity is now unconstrained

These may still be true in some narrower sense, but they are not strong enough for active OMEGA guidance without better primary evidence.

## OMEGA Build Implications

### Immediate documentation-level implications

1. Add `proof_obligations.md` to the default problem scaffold.
2. Treat press narratives as secondary evidence only.
3. Update proof-first and verification docs to require explicit obligation tracking.
4. Extend research-intelligence mapping to include formal-math and judge-reliability surfaces.

### Near-term engineering implications

1. Add a Lean 4 bootstrap path and toolchain contract.
2. Add a CAS-backed or certified inequality-check lane for algebra-heavy obligations.
3. Add autonomy and novelty metadata to future result manifests.
4. Preserve versioned proof drafts and independent referee notes as first-class local artefacts.

## Bottom Line

The strongest conclusion from this pass is narrower and more useful than the press version:

LLMs are now good enough to accelerate research-level theorem development on the right kinds of problems, but the decisive engineering problem has shifted from raw generation to obligation management, verification, and reproducibility. OMEGA should therefore optimize for auditable proof search plus explicit closure mechanisms, not for performative autonomy claims.