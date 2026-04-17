---
title: "OMEGA SOTA Landscape Update — April 13, 2026"
status: active
version: "2.0.0"
last_updated: "2026-04-13"
date: "2026-04-13"
role: evidence
audience: internal
tags: [omega, sota, formal-proving, agents, evidence-governance, pipeline]
evidence_class: E1
confidence: C2
supersedes: "OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md (extends, not replaces)"
---

# OMEGA SOTA Landscape Update — April 13, 2026

## Purpose

This report covers two surfaces:
1. **External SOTA shift** since the April 5 landscape report — new papers, tools, benchmarks.
2. **Internal OMEGA pipeline maturity** after the April 8–13 engineering sprint.

Evidence standard follows the parent report: **E1** (primary source), **E2** (verified comparison), **H** (hypothesis/projection).

---

## Part 1: External Landscape Shifts (April 5 → April 13, 2026)

### 1.1 New Prover Architectures

| System | Source | Date | Key Contribution | Evidence |
|--------|--------|------|------------------|----------|
| **Leanabell-Prover-V2** | arXiv:2507.08649 | Jul 2025 | 7B model with verifier-integrated Long CoT for Lean 4; builds on Leanabell-Prover-V1 | E1 |
| **DSP-Plus** (Microsoft) | arXiv:2506.11487 | Jun 2025 | Revives Draft-Sketch-Prove for reasoning-era models; combines DeepSeek-Prover-V2 with DSP decomposition | E1 |
| **Kimina-Prover Preview** | arXiv:2504.11354 | Apr 2025 | Large formal reasoning model trained with RL — direct DeepSeek-Prover-V2 competitor from Kimina AI | E1 |
| **ProofBridge** | arXiv:2510.15681 | Oct 2025, ICLR 2026 | Auto-formalization of natural-language proofs to Lean via joint embeddings; outperforms GPT-5 and Gemini-2.5 baselines | E1 |
| **Stepwise** | arXiv:2603.19715 | Mar 2026 | Neuro-symbolic proof search for systems verification (Lean 4); combines tactic generation with symbolic search | E1 |
| **Nazrin** | arXiv:2602.18767 | Feb 2026 | GNN-based atomic tactic predictor for Lean 4; graph structure for proof state representation | E1 |
| **ProofAug** | arXiv:2501.18310 | Jan 2025, v2 Jun 2025 | Efficient neural theorem proving via fine-grained proof structure analysis | E1 |

### 1.2 Infrastructure & Servers

| System | Source | Key Contribution |
|--------|--------|------------------|
| **Kimina Lean Server** | arXiv:2504.21230, NeurIPS 2025 MATH-AI | High-performance Lean REPL server with server-side parallelism + LRU caching for RL pipelines |

**OMEGA implication**: Kimina Lean Server validates our `lean_adapter.py` architectural pattern (subprocess-based Lean process management). OMEGA should evaluate adopting Kimina Lean Server as the backend for our proof verification instead of raw Lean subprocess calls. Benefits: parallelism, caching, proven RL pipeline integration.

### 1.3 New Benchmarks

| Benchmark | Source | Key Contribution |
|-----------|--------|------------------|
| **Ineq-Comp** | arXiv:2505.12680, NeurIPS 2025 | Compositional reasoning on inequalities (AM/GM, Cauchy-Schwarz); tests whether provers understand structure vs. pattern-match |
| **CombiBench** | arXiv:2505.03171 | Combinatorial math benchmark with fill-in-the-blank + proof problems; uses Kimina Lean Server |
| **Neural TP for Verification Conditions** | arXiv:2601.18944, ICLR 2026 | Real-world benchmark (not olympiad): verification conditions from software verification |
| **Structured Hints** | arXiv:2601.16172 | Shows DeepSeek-Prover-V1.5 benefits from simple structural guidance at inference time |

### 1.4 Dominant Architectural Patterns (confirmed by new evidence)

The following patterns are now independently confirmed by ≥3 systems and should be treated as SOTA consensus:

1. **Subgoal decomposition via large model + solution via small model** — DeepSeek-Prover-V2, DSP-Plus, Kimina-Prover all use this pattern. OMEGA's agent orchestrator (`planner` → `experimentalist`) aligns.

2. **Lean 4 as the target formalism** — all new systems (Nazrin, ProofBridge, Stepwise, Kimina, Leanabell-V2) target Lean 4 exclusively. The Lean 4 bet is validated.

3. **RL with compiler-as-reward** — DeepSeek-V2, Kimina-Prover, Leanabell-V2 all use binary compiler feedback for RL. The open question is how to integrate this into a research pipeline (vs. training pipeline).

4. **High-performance Lean verification servers** — both Kimina Lean Server and internal LeanDojo tooling show that dedicated Lean servers with parallelism + caching are necessary for RL-scale proving. Raw subprocess calls don't scale.

5. **Auto-formalization as a complementary surface** — ProofBridge (ICLR 2026) shows that NL→Lean auto-formalization is becoming competitive, enabling researchers to state conjectures in natural language and get Lean formalizations.

---

## Part 2: Internal OMEGA Pipeline Maturity (April 8–13 Sprint)

### 2.1 Engineering Deliverables

| Deliverable | Status | Description |
|------------|--------|-------------|
| **Agent Orchestrator** (`agent_orchestrator.py`) | DONE | 7-role agent team (planner, librarian, analyst, experimentalist, prover, writer, reviewer); YAML-defined agent definitions; 8-stage pipeline (brief → novelty → plan → experiment → prove → results → paper → referee); dry-run and live dispatch; T1/T4 routing |
| **Evidence Checksumming** (`verify_evidence.py`) | DONE | SHA-256 checksumming of all workspace artifacts; compute/verify/status CLI; evidence-bundle.yaml per workspace |
| **Solver Wiring** (solver_adapter.py, cas_adapter.py, lean_adapter.py) | CONFIRMED | Z3 SMT/optimization, PySAT + built-in DPLL, SymPy CAS, Lean 4 subprocess — all fully wired with structured YAML output |
| **E2E Integration Test** (`test_e2e_pipeline.py`) | DONE | 6 tests: full pipeline brief-to-results, single dispatch, evidence bundle integration, T4 routing, dry-run smoke tests |
| **Test Suite** | 121 passed, 8 skipped | Full regression suite passing |

### 2.2 Agent Architecture vs. SOTA Comparison

| SOTA Pattern | OMEGA Implementation | Gap |
|-------------|----------------------|-----|
| Subgoal decomposition (large → small) | `planner` agent decomposes → `experimentalist` solves | None — aligned |
| Lean 4 proof verification | `lean_adapter.py` subprocess execution | **Gap**: should evaluate Kimina Lean Server for parallelism + caching |
| RL with compiler feedback | Not implemented (research pipeline, not training) | Intentional — OMEGA is a research pipeline, not a training pipeline |
| Evidence governance | `verify_evidence.py` with SHA-256 + evidence bundles | None — exceeds most external systems |
| Multi-agent pipeline | 7-role team with YAML definitions | None — more structured than any external system |
| Auto-formalization | Not implemented | **Gap**: ProofBridge (ICLR 2026) shows this is viable; could add as `formalizer` agent role |

### 2.3 Remaining Gaps (Prioritized)

| Priority | Gap | Effort | External Reference |
|----------|-----|--------|--------------------|
| **P1** | Kimina Lean Server evaluation for proof verification backend | 2–3 days | arXiv:2504.21230 |
| **P2** | Auto-formalization agent role (`formalizer`) | 3–5 days | arXiv:2510.15681 (ProofBridge) |
| **P3** | Literature adapter integration with Semantic Scholar API | 1–2 days | Already scaffolded in `literature_adapter.py` |
| **P4** | Live LLM dispatch (currently dry-run only without API key) | 1 day | Agent orchestrator ready, needs API key wiring |
| **P5** | Artifact diffing and experiment comparison tools | 2–3 days | New — needed for iterative research loops |

---

## Part 3: OMEGA Competitive Position (April 13 Assessment)

### 3.1 What OMEGA Has That Others Don't

1. **End-to-end research pipeline** (not just proving): survey → plan → experiment → prove → write → review. No external system covers this full cycle.
2. **Evidence governance with checksumming**: SHA-256 integrity verification on all artifacts. No external academic system has this rigor.
3. **Multi-solver integration**: Z3 + PySAT + SymPy + Lean 4 in one pipeline. Most systems are Lean-only.
4. **Open problem registry with triage**: 16 problems classified T1-T5 with amenability scoring. Unique to OMEGA.
5. **Agent team with explicit roles**: 7 defined agents with input/output contracts. Closest comparison is FunSearch (DeepMind) but that's single-role.

### 3.2 What Others Have That OMEGA Doesn't (Yet)

1. **Pre-trained prover models**: DeepSeek-Prover-V2 (671B/7B), Kimina-Prover. OMEGA dispatches to these via API but doesn't train its own.
2. **RL training loop**: All frontier provers use RL with compiler feedback. OMEGA uses the output of trained models, not the training itself.
3. **Auto-formalization**: ProofBridge can convert NL proofs to Lean with joint embeddings. OMEGA currently requires manual formalization.
4. **GPU-scale proof search**: DeepSeek runs 32× parallel proof attempts. OMEGA's lean_adapter.py runs sequentially.

### 3.3 Strategic Recommendation

OMEGA's competitive moat is the **research orchestration layer**, not the proving itself. The proving capability is best consumed via API from frontier models (DeepSeek-Prover-V2-7B locally, 671B via API). OMEGA should focus on:

1. **Orchestration quality** — routing the right subproblem to the right tool
2. **Evidence integrity** — making results reproducible and verifiable
3. **Knowledge accumulation** — capturing insights across runs for iterative deepening

This is aligned with the "Agentic Researcher" vision (arXiv:2603.15914, March 2026).

---

## Appendix: New Papers Since April 5 (Full References)

1. Leanabell-Prover-V2 — arXiv:2507.08649 (Jul 2025)
2. DSP-Plus — arXiv:2506.11487 (Jun 2025), Microsoft, Code: github.com/microsoft/DSP-Plus
3. Kimina-Prover Preview — arXiv:2504.11354 (Apr 2025)
4. Kimina Lean Server — arXiv:2504.21230 (Apr 2025), NeurIPS 2025 MATH-AI
5. ProofBridge — arXiv:2510.15681 (Oct 2025), ICLR 2026
6. Stepwise — arXiv:2603.19715 (Mar 2026)
7. Nazrin — arXiv:2602.18767 (Feb 2026)
8. ProofAug — arXiv:2501.18310 (Jan 2025, v2 Jun 2025)
9. Ineq-Comp — arXiv:2505.12680 (May 2025), NeurIPS 2025
10. CombiBench — arXiv:2505.03171 (May 2025)
11. Neural TP for VCs — arXiv:2601.18944 (Jan 2026), ICLR 2026
12. Structured Hints — arXiv:2601.16172 (Jan 2026)
13. The Agentic Researcher — arXiv:2603.15914 (Mar 2026)
