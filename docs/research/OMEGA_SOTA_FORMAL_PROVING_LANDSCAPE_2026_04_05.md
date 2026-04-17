---
title: "OMEGA SOTA Formal Proving Landscape Report"
status: active
version: "1.0.0"
last_updated: "2026-04-05"
date: "2026-04-05"
role: evidence
audience: internal
tags: [omega, formal-proving, SOTA, deepseek, kimina, leandojo, benchmark, academic]
evidence_class: E1
confidence: C3
---

# OMEGA SOTA Formal Proving Landscape Report (April 2026)

## Purpose

This report captures the externally verified state of the art in neural theorem proving,
formal mathematics tooling, and AI-for-math benchmarking as of April 2026. It serves as
the evidence surface for all OMEGA architectural and workflow decisions that reference
external proving capability.

This is not a press summary. Every claim is grounded in primary papers, maintained
repositories, or official documentation. Press narratives and secondary commentary are
cited only when no primary surface exists.

## Evidence Standard

- **E1 (official external authority)**: primary arXiv papers, official repos, maintained docs
- **E2 (qualified external comparison)**: benchmark results, reproducible evaluations
- **H (hypothesis)**: projections, roadmap items, unverified claims

## 1. Neural Theorem Proving: State of the Art

### 1.1 DeepSeek-Prover-V2

**Source**: DeepSeek-AI. *DeepSeek-Prover-V2: Advancing Formal Mathematical Reasoning via
Reinforcement Learning for Subgoal Decomposition.* 2025. GitHub: `deepseek-ai/DeepSeek-Prover-V2`.

**Evidence class**: E1

**Architecture**:

DeepSeek-Prover-V2 introduces a recursive theorem-proving pipeline built on two key innovations:

1. **Subgoal decomposition**: DeepSeek-V3 (671B) decomposes complex theorems into independent
   subgoals. Each subgoal is a self-contained Lean 4 `sorry`-bearing statement that can be
   proved individually.

2. **Chain-of-thought cold start for RL**: Proofs of resolved subgoals are synthesized into a
   chain-of-thought process. This combines DeepSeek-V3's step-by-step informal reasoning with
   formal Lean 4 proof steps, creating a unified model that spans both informal and formal
   mathematical reasoning.

3. **Reinforcement Learning**: The model is then trained via RL, where the Lean 4 compiler
   serves as the reward signal (binary: proof checks or it does not).

**Results (verified from repo)**:

| Benchmark | Model | Result | Evidence |
|-----------|-------|--------|----------|
| MiniF2F-test (244 problems) | DeepSeek-Prover-V2-671B | 88.9% pass rate | GitHub performance chart |
| PutnamBench (658 problems) | DeepSeek-Prover-V2-671B | 49 problems solved | GitHub performance chart |
| ProverBench (325 problems) | DeepSeek-Prover-V2-671B | strong performance (exact % TBD) | GitHub repo |

**Model variants**:

| Variant | Parameters | Open-weight | Context | Use case |
|---------|-----------|-------------|---------|----------|
| DeepSeek-Prover-V2-671B | 671B (MoE) | Yes (HuggingFace) | 163K | Frontier proving, subgoal decomposition |
| DeepSeek-Prover-V2-7B | 7B | Yes (HuggingFace) | 32K | Workstation proving, individual subgoals |

**Strategic implications for OMEGA**:

1. The subgoal-decomposition architecture is the dominant paradigm: large model decomposes,
   small model solves. OMEGA should adopt this two-level architecture.
2. The 7B variant is workstation-deployable via GGUF quantization and runs on consumer hardware.
3. RL with compiler-as-reward is the training recipe that produced SOTA. OMEGA need not
   replicate training, but should understand the feedback loop.
4. The recursive pipeline naturally maps to OMEGA's `proof-repair loop` concept.

### 1.2 Kimina-Prover

**Source**: Wang, H., Unsal, M., Lin, X., Baksys, M., et al. *Kimina-Prover Preview: Towards Large Formal Reasoning Models
with Reinforcement Learning.* arXiv:2504.11354 [cs.AI], April 2025. GitHub:
`MoonshotAI/Kimina-Prover-Preview`.

**Evidence class**: E1

**Architecture**:

Kimina-Prover pioneers a distinct approach from DeepSeek's subgoal decomposition:

1. **Whole-proof generation**: All proofs are generated without any prover feedback during
   training and test. No MCTS, no value functions, no process reward models.

2. **Formal Reasoning Pattern**: A carefully designed reasoning style that bridges formal
   verification and informal mathematical intuition. The model alternates between natural-language
   thinking and formal Lean 4 code within a single generation.

3. **Model size scaling**: First demonstration that scaling model size (up to 72B) improves
   formal theorem proving — a trend previously unobserved in neural theorem proving.

4. **Long context scaling**: Context window up to 32K tokens for both training and inference,
   the longest in the neural theorem proving community.

**Results (verified from repo and paper)**:

| Benchmark | Model | Result | Sampling | Evidence |
|-----------|-------|--------|----------|----------|
| MiniF2F-test | Kimina-Prover-72B | 80.7% | pass@8192 | README + paper |
| MiniF2F-test | Kimina-Prover-72B | 68.85% | pass@32 | README |
| MiniF2F-test | Kimina-Prover-72B | 65.16% | pass@8 | README |

**Open-source deliverables**:

| Artifact | Size | License | Hub |
|----------|------|---------|-----|
| Kimina-Prover-Distill-1.5B | 1.5B | open-weight | HuggingFace AI-MO |
| Kimina-Prover-Distill-7B | 7B | open-weight | HuggingFace AI-MO |
| Kimina-Lean-Server | — | open-source | GitHub project-numina |
| Autoformalization model | — | open-weight | HuggingFace AI-MO |

The 72B model was released July 2025.

**Strategic implications for OMEGA**:

1. Whole-proof generation without MCTS is viable and competitive. OMEGA does not need to
   implement tree search to get strong proving results.
2. The Formal Reasoning Pattern (think → formalize → verify) maps directly to OMEGA's
   `generate → referee → repair` loop.
3. Distilled 7B model is workstation-deployable and available on HuggingFace.
4. Kimina-Lean-Server provides a reusable Lean verification backend.

### 1.3 AlphaProof (DeepMind)

**Source**: DeepMind blog, July 2024. No primary paper published.

**Evidence class**: E2 (no peer-reviewed paper; blog claims only)

**Verified claim**: Solved 4 out of 6 IMO 2024 problems using Lean 4 + reinforcement learning.

**Strategic implications for OMEGA**:

1. Sets the ceiling: formal verification of competition-level math is achievable.
2. Closed-source: OMEGA cannot use AlphaProof, but can learn from the architecture.
3. Validates the Lean 4 + RL paradigm independently of DeepSeek and Kimina.

### 1.4 LeanDojo / ReProver

**Source**: Yang, K. et al. *LeanDojo: Theorem Proving with Retrieval-Augmented Language
Models over Lean.* arXiv:2306.15626, NeurIPS 2023. GitHub: `lean-dojo/LeanDojo`.

**Evidence class**: E1

LeanDojo provides:
- Open-source Lean 4 interaction toolkit
- Premise retrieval from mathlib4
- ReProver: retrieval-augmented prover trained on Lean 4 proofs

This is the foundation layer that LeanCopilot builds on.

### 1.5 LLEMMA

**Source**: Azerbayev, Z. et al. *LLEMMA: An Open Language Model For Mathematics.*
arXiv:2310.10631, 2023.

**Evidence class**: E1

LLEMMA provides:
- Open math-specialized LLMs (7B/34B)
- Trained on Proof-Pile-2 (mixed formal/informal math corpus)
- Baseline for math reasoning without formal-prover-specific fine-tuning

### 1.6 Process Advantage Verifiers (PAVs)

**Source**: Luo, L. et al. *Improve Mathematical Reasoning in Language Models by Automated
Process Supervision.* arXiv:2406.06592. Lu, S. et al. *Process Advantage Verifiers.*
arXiv:2410.08146, 2024.

**Evidence class**: E1

**Key findings**:

1. Process reward models give +8% accuracy improvement over outcome reward models in math reasoning.
2. 5-6× sample efficiency in online RL settings.
3. Step-level credit assignment produces more precise training signal than episode-level rewards.

**Strategic implications for OMEGA**:

When OMEGA's proof-repair loop generates multiple candidate tactics, PAV-style step-level
scoring should be used to rank candidates rather than random or majority-vote selection.

## 2. Lean 4 Ecosystem: Integration Surfaces

### 2.1 LeanCopilot

**Source**: Song, P., Yang, K., Anandkumar, A. *Lean Copilot: Large Language Models as
Copilots for Theorem Proving in Lean.* arXiv:2404.12534. Published at NeuS 2025.
GitHub: `lean-dojo/LeanCopilot`. MIT License.

**Evidence class**: E1

**Current version**: v4.28.0 (tracks Lean 4 v4.28.0 stable)

**Capabilities (verified from repo)**:

| Feature | Description | Tactic |
|---------|-------------|--------|
| Tactic suggestion | LLM suggests next tactic step | `suggest_tactics` |
| Proof search | Multi-tactic proof via LLM + aesop | `search_proof` |
| Premise selection | Retrieval of useful lemmas from mathlib4 | `select_premises` |
| LLM inference | Run arbitrary models natively in Lean 4 | Model APIs |

**Model architecture**:

LeanCopilot supports three generator types:
1. `NativeGenerator`: local CTranslate2 models via FFI
2. `ExternalGenerator`: user-hosted models via Python API server
3. `GenericGenerator`: any model implementing `TextToText` typeclass

**Bring-your-own-model pattern**:

LeanCopilot exposes a Python API server (`python/`) that any model can plug into via
`external_model_api.yaml`. This is the primary integration surface for OMEGA.

```yaml
# LeanCopilot external model API contract (verified)
endpoints:
  - POST /generate
    input: { input: string, prefix: string }
    output: [{ text: string, score: float }]
  - POST /encode
    input: { input: string }
    output: { embedding: float[] }
```

**Performance (from paper)**:
- Automates 74.2% of proof steps (vs 40.1% for aesop alone)
- Requires only 2.08 manually-entered proof steps on average

**Verified integration with Kimina-Prover**:

LeanCopilot's `LeanCopilotTests/` directory includes Kimina Prover API integration,
confirming that Kimina models can serve as external generators through LeanCopilot.

**Strategic implications for OMEGA**:

1. LeanCopilot is the recommended integration surface for OMEGA's proof lane.
2. OMEGA should NOT build a custom Lean-LLM bridge — LeanCopilot already provides one.
3. The ExternalGenerator API allows OMEGA to route through local Ollama/vLLM endpoints.
4. Premise selection from mathlib4 gives OMEGA's prover lane access to the full standard library.

### 2.2 LLMLean

**Source**: GitHub `cmu-l3/llmlean`. Active development.

**Evidence class**: E1

Integrates LLMs with Lean for tactic suggestion and proof completion. Supports local Ollama
backends. Explicitly added BFS-Prover-V2 and Kimina support through Ollama in 2025.

### 2.3 llmstep

**Source**: GitHub `wellecks/llmstep`.

**Evidence class**: E1

Model-agnostic tactic suggester. Sends proof state to a server, which calls a language model
and returns suggestions. Minimal bridge from Lean proof state to any model endpoint.

### 2.4 LeanTool

**Source**: GitHub maintained tool.

**Evidence class**: E1

Uses LiteLLM for model routing, so it targets local runtimes via OpenAI-compatible APIs.
"Code interpreter" for Lean with self-correction of syntax and proof errors.

### 2.5 UlamAI

**Source**: GitHub `UlamAI`.

**Evidence class**: E1

CLI for LLM-guided reasoning with Lean 4 verification. Documents fully local use through
Ollama. Shell-driven workflow rather than editor-only tactic assistant.

## 3. Benchmarks and Calibration

### 3.1 MiniF2F

**Source**: Zheng, K. et al. *MiniF2F: a cross-system benchmark for formal olympiad-level
mathematics.* ICLR 2022.

**Evidence class**: E1

| System | Pass rate | Year |
|--------|-----------|------|
| DeepSeek-Prover-V2-671B | 88.9% | 2025 |
| Kimina-Prover-72B | 80.7% (pass@8192) | 2025 |
| BFS-Prover | 72.9% | 2024 |
| Hunyuan-Prover | ~65% | 2024 |
| DeepSeek-Prover-V1.5 | ~60% | 2024 |
| ReProver (LeanDojo) | ~34% | 2023 |

**OMEGA reading**: MiniF2F is approaching saturation. For competition-level formalization,
SOTA models are close to ceiling. OMEGA should use MiniF2F as a calibration baseline, not
as a research target.

### 3.2 PutnamBench

**Source**: DeepSeek-Prover-V2 repo. 658 problems from Putnam Competition.

**Evidence class**: E1

| System | Solved | Year |
|--------|--------|------|
| DeepSeek-Prover-V2-671B | 49/658 | 2025 |

**OMEGA reading**: PutnamBench represents undergraduate+ difficulty. 49/658 = 7.4% solve rate
shows the gap between competition-tuned and research-grade formal proving.

### 3.3 ProverBench

**Source**: DeepSeek-Prover-V2 repo. 325 problems (AIME 2024-25 + textbook).

**Evidence class**: E1

New benchmark calibrating from high-school competition through undergraduate textbook level.
Useful for OMEGA's T1-T2 tier calibration.

### 3.4 FrontierMath (Epoch AI)

**Source**: Glazer, E. et al. *FrontierMath: A Benchmark for Evaluating Advanced Mathematical
Reasoning in AI.* arXiv:2411.04872 [cs.AI], November 2024 (v7 December 2025).

**Evidence class**: E1

**Design**:
- Hundreds of original, unpublished mathematics problems
- Covers most major branches: number theory, real analysis, algebraic geometry, category theory
- Difficulty: typical problem requires multiple hours for a domain expert; upper-end problems
  require multiple days
- Automated verification to minimize data contamination risk

**Tier structure**:
- Tiers 1-3: undergraduate through early postdoc level
- Tier 4: research-level mathematics
- Open Problems: unsolved problems where AI solutions would advance human knowledge

**Results**:

Current SOTA AI models solve **under 2%** of FrontierMath problems.

**OMEGA reading**:

FrontierMath quantifies the massive gap between current AI and research-grade mathematical
capability. OMEGA should:
1. NOT claim FrontierMath-level capability
2. USE FrontierMath as a calibration surface for honest self-assessment
3. TARGET FrontierMath Tier 1-2 subproblems as stretch goals
4. TREAT FrontierMath Open Problems as aspirational only

### 3.5 Omni-MATH-2

**Source**: Ballon, B. et al. arXiv:2601.19532, 2026.

**Evidence class**: E1

**Key finding**: Judge-induced error can dominate evaluation once models outrun their judges.
LLM-based judging produces systematically biased assessments.

**OMEGA implication**: LLM judging is diagnostic only, never verification. Formal verification
(Lean 4 compiler, SAT solvers) must be the ground truth.

## 4. Research-Agent Systems

### 4.1 Aletheia

**Source**: Feng, T., Trinh, T.H., Bingham, G., Hwang, D., et al. *Towards Autonomous Mathematics Research.* arXiv:2602.10177, 2026.

**Evidence class**: E1

Introduces autonomy and novelty gradation for math research agents. Key insight: not all
agent contributions are equally autonomous or novel, and reporting should make this explicit.

### 4.2 Gemini on Erdős Problems

**Source**: Feng, T., Trinh, T., Bingham, G., Kang, J., et al. *Semi-Autonomous Mathematics Discovery with Gemini: A Case Study on the Erdős Problems.* arXiv:2601.22401, 2026.

**Evidence class**: E1

Semi-autonomous screening of 700 open-problem records. Of 13 addressed problems, 8 had
existing solutions in the literature. Main lesson: literature collision is a
first-class risk for any open-problem project.

### 4.3 Denario

**Source**: arXiv:2510.26887.

**Evidence class**: E1

Modular research pipeline: idea → novelty → methods → results → paper → referee.
OMEGA's architectural donor for pipeline modularity.

## 5. Formal Assurance Landscape

### 5.1 Post-Quantum Cryptography

**Source**: NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), 2024.

**Evidence class**: E1

NIST standardization creates sustained demand for formal assurance of PQC implementations.
Key properties amenable to formalization:

- Correctness of key generation, encapsulation, decapsulation
- Lattice-based hardness assumptions (LWE, RLWE)
- Hash-based signature correctness
- Constant-time implementation properties

This is OMEGA's strongest near-term applied wedge.

### 5.2 VUB Vibe-Proving Case Study

**Source**: Verbeken, B., Vagenende, B., Guerry, M.-A., Algaba, A., Ginis, V. *Early Evidence of Vibe-Proving with Consumer LLMs.* arXiv:2602.18918, 2026.

**Evidence class**: E1

Consumer-LLM (ChatGPT) materially assisted a human-verified proof of Conjecture 20 of Ran
and Teng on spectral regions of row-stochastic matrices. The study provides:
- Seven shareable ChatGPT threads
- Four versioned proof drafts
- Explicit generate → referee → repair loop
- Human correctness closure

The key reusable pattern: consumer LLMs are useful proposal engines within a formally
verified loop, not autonomous provers.

## 6. OMEGA Capability Gap Analysis

### 6.1 Where OMEGA Can Realistically Operate (April 2026)

| Capability tier | External SOTA | OMEGA current state | Gap |
|----------------|--------------|--------------------|----|
| T1 computational (SAT/SMT/search) | Strong solver ecosystem | Adapter scaffolds exist | Gap: no repeatable pipeline |
| T2 experimental (numerical evidence) | SageMath + Python ecosystem | CAS adapter exists | Gap: no orchestrated experiments |
| T3 pattern (proof-search assist) | LeanCopilot 74.2% step automation | No LLM integration | Gap: entire LLM-prover lane missing |
| T4 structural (formal proofs) | 88.9% MiniF2F by DeepSeek-V2 | Lean adapter scaffold exists | Gap: no proof-repair loop |
| T5 foundational | FrontierMath <2% SOTA | No capability | Expected: out of scope |

### 6.2 Realistic Near-Term Targets

Based on the external landscape, OMEGA's realistic near-term targets are:

1. **T1 problems**: Erdős–Straus bound extension, Kobon triangles SAT encoding, Thomson problem
   optimization. These require only solver and CAS adapters, no LLM.

2. **Simple formalizations**: Known number-theoretic bounds verified in Lean 4. This tests the
   Lean adapter without requiring neural proving.

3. **LLM-assisted proof search on textbook-level problems**: Using DeepSeek-Prover-V2-7B via
   LeanCopilot's ExternalGenerator API. ProverBench-level difficulty.

4. **Literature-backed novelty verification**: Using Semantic Scholar API for automated
   collision detection before any claim of novelty.

## 7. Bibliography

### Primary Papers

1. DeepSeek-AI. DeepSeek-Prover-V2. GitHub: `deepseek-ai/DeepSeek-Prover-V2`, 2025.
2. Wang, H. et al. Kimina-Prover Preview. arXiv:2504.11354, 2025.
3. Song, P. et al. Lean Copilot. arXiv:2404.12534, NeuS 2025.
4. Yang, K. et al. LeanDojo. arXiv:2306.15626, NeurIPS 2023.
5. Azerbayev, Z. et al. LLEMMA. arXiv:2310.10631, 2023.
6. Lu, S. et al. Process Advantage Verifiers. arXiv:2410.08146, 2024.
7. Glazer, E. et al. FrontierMath. arXiv:2411.04872, 2024.
8. Verbeken, B. et al. VUB Vibe-Proving. arXiv:2602.18918, 2026.
9. Feng, T. et al. Semi-Autonomous Mathematics Discovery with Gemini. arXiv:2601.22401, 2026.
10. Feng, T. et al. Towards Autonomous Mathematics Research. arXiv:2602.10177, 2026.
11. Liu, T. et al. Numina-Lean-Agent. arXiv:2601.14027, 2026.
12. Ballon, B. et al. Omni-MATH-2. arXiv:2601.19532, 2026.
13. NIST. FIPS 203/204/205 (PQC Standards), 2024.

### Maintained Repositories

1. `deepseek-ai/DeepSeek-Prover-V2` — SOTA formal prover
2. `MoonshotAI/Kimina-Prover-Preview` — RL-trained formal prover
3. `lean-dojo/LeanCopilot` — LLM copilot for Lean 4 (MIT)
4. `lean-dojo/LeanDojo` — Lean 4 interaction toolkit
5. `project-numina/kimina-lean-server` — Lean verification backend
6. `cmu-l3/llmlean` — LLM-Lean bridge
7. `wellecks/llmstep` — model-agnostic tactic suggester
8. `leanprover-community/mathlib4` — Lean 4 standard math library

---

*This report is a living document. Update when new primary sources change the landscape.*
