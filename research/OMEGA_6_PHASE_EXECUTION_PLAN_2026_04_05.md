---
title: "OMEGA 6-Phase Execution Plan"
status: active
version: "1.0.0"
last_updated: "2026-04-05"
date: "2026-04-05"
role: explanation
audience: internal
tags: [omega, execution-plan, roadmap, formal-proving, literature, orchestration]
---

# OMEGA 6-Phase Execution Plan (April 2026)

## Purpose

This document translates the OMEGA SOTA landscape analysis into a concrete, phased execution
plan with specific tasks, evidence gates, dependency structure, and academic grounding.

This is the operational companion to `OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md`. The roadmap
defines horizons and strategy; this document defines what to build, in what order, with what
verification.

## Strategic Context

### Current State Summary

OMEGA currently has:
- **239 problems** in the machine-readable registry across 12 mathematical domains
- **60 triaged records** with AI-amenability scoring (25.1% coverage)
- **14 Tier 1 problems** (computationally accessible, amenability ≥ 7)
- **Three execution adapters**: `lean_adapter.py`, `solver_adapter.py`, `cas_adapter.py`
- **Workflow controller**: `omega_workflow.py` (triage, status, advance)
- **Experiment runner**: `omega_runner.py` (start, finish, proof-result, evidence-bundle)
- **Protocol docs**: evidence governance, triage matrix, agent teams, lean bootstrap

OMEGA does NOT have:
- Real LLM integration in any adapter
- Automated literature retrieval
- Proof-repair loops (generate → verify → repair → retry)
- Orchestrated multi-agent execution
- A single end-to-end pipeline closure on any problem

### Strategic Bottleneck

The bottleneck is not registry breadth. The bottleneck is the absence of a repeatable
execution loop:

```
triage → workspace → experiments → proof attempt → evidence bundle → writeup → review
```

All six phases below serve to close this loop and then extend it.

## Dependency Diagram

```
Phase 1 (Pipeline Closure) ─────┬──► Phase 2 (LLM Proof Search) ──► Phase 4 (Orchestration) ──► Phase 5 (Publication)
                                │                                            ▲
                                └──► Phase 3 (Literature)  ──────────────────┘

                                Phase 6 (Formal Assurance) ─── parallel with Phase 5 ──►
```

Phase 1 is the sole blocking prerequisite for all subsequent work.
Phases 2 and 3 can proceed in parallel after Phase 1.
Phase 4 depends on both Phase 2 and Phase 3.
Phases 5 and 6 proceed in parallel after Phase 4.

---

## Phase 1: Pipeline Closure

### Goal

The first 3 Tier 1 problems complete the full lifecycle with real artifacts.

### Estimated Duration

8–12 weeks from start.

### Tasks

#### 1.1 Lean Execution Lane → Real

**What**: Connect `lean_adapter.py` to real `lake build` with pinned mathlib toolchain.

**Deliverables**:
- Integration test: create Lean 4 project → add mathlib → add `sorry` → run `check_file` → receive structured error
- Pinned `lean-toolchain` to Lean 4 v4.29.0
- `lake exe cache get` as part of reproducibility boundary

**Files**: `scripts/lean_adapter.py`, `tests/test_lean_adapter_integration.py`

**Academic basis**: DeepSeek-Prover-V2 requires repeated Lean file checks for subgoal-level
proving (arXiv:2504.21801). The adapter must support individual file checking, not just full
project builds.

#### 1.2 Solver Lane → Real

**What**: Write integration tests for `solver_adapter.py` with concrete problem instances.

**Deliverables**:
- Integration test: formulate Erdős–Straus conjecture for specific $n$ → call Z3 → receive SAT/UNSAT
- Integration test: encode Kobon triangles for $k = 5$ → call built-in DPLL → verify known optimal
- SAT encoding utilities for registry problems

**Files**: `scripts/solver_adapter.py`, `tests/test_solver_integration.py`

#### 1.3 Literature Lane → New

**What**: Create `scripts/literature_adapter.py` with retrieval from Semantic Scholar API.

**Contract**:
```yaml
input:
  query: string     # search keywords from problem record
  problem_id: string
  max_results: 50
output:
  papers:
    - title: string
      authors: [string]
      year: int
      citation_count: int
      abstract: string
      doi: string | null
      arxiv_id: string | null
      url: string
  novelty_assessment:
    total_related: int
    closest_matches: [string]
    known_partial_results: [string]
    confidence: "C1 | C2 | C3"
```

**Deliverables**:
- `scripts/literature_adapter.py` with Semantic Scholar API (100 req/sec, free tier)
- `protocol/literature-adapter.md` contract document
- `tests/test_literature_adapter.py`
- Optional arXiv API supplement for fresh preprints

**Academic basis**: Feng et al. (arXiv:2601.22401) showed that of 13 addressed "open" Erdős
problems, 8 already had existing solutions in the literature (≈62%), detectable by automated
screening. Literature collision is a first-class risk.

#### 1.4 Orchestration → Real

**What**: Extend `omega_workflow.py` so `advance` calls the appropriate adapter.

**Deliverables**:
- `advance erdos-straus --outcome complete` at experiment stage → calls solver → records in ledger → generates evidence bundle
- `advance kobon-triangles --outcome complete` → SAT solver → evidence bundle
- `advance thomson-problem --outcome complete` → CAS optimization → evidence bundle

**Files**: `scripts/omega_workflow.py`

#### 1.5 Pilot on 3 Problems

**What**: Execute the full lifecycle on three selected Tier 1 problems.

| Problem | Route | Primary adapter | Expected output |
|---------|-------|----------------|-----------------|
| `erdos-straus` | experiment-first | solver (Z3) | Parametric verification for $n \leq N$ |
| `kobon-triangles` | experiment-first | solver (SAT) | Optimal construction for $k = 5$ |
| `thomson-problem` | experiment-first | CAS (SymPy) | Numerical optimization of $E(n)$ for small $n$ |

For each: workspace → experiment → evidence bundle → `artifacts/evidence-bundle.yaml`.

### Evidence Gate

Three `artifacts/evidence-bundle.yaml` files with:
- Non-empty checksums
- Replayable commands in `reproducibility.md`
- Experiment ledger entries with `status: completed`

---

## Phase 2: LLM-Backed Proof Search

### Goal

OMEGA uses neural networks for proof generation for the first time.

### Estimated Duration

6–10 weeks after Phase 1 completion.

### Tasks

#### 2.1 Model Routing Layer

**What**: Create `scripts/model_router.py` that routes proof requests to available backends.

**Backends**:
1. **Ollama + DeepSeek-Prover-V2-7B** (GGUF): workstation-local proving
2. **LeanCopilot ExternalGenerator API**: Lean-native integration
3. **vLLM**: batch inference for multi-attempt proving

**Contract**:
```yaml
input:
  proof_state: string      # current Lean goal/tactic state
  context: string          # surrounding proof and imports
  max_candidates: 10
  model_preference: "local | copilot | batch"
output:
  candidates:
    - tactic: string
      score: float
      model: string
      generation_time_ms: int
```

**Files**: `scripts/model_router.py`, `tests/test_model_router.py`

**Academic basis**: LeanCopilot (arXiv:2404.12534) provides the ExternalGenerator API with a
standardized contract (`external_model_api.yaml`). DeepSeek-Prover-V2-7B (32K context) is the
recommended workstation model.

#### 2.2 Proof-Repair Loop

**What**: Implement bounded generate-repair cycle.

**Algorithm**:
```
for attempt in 1..max_k:
    candidates = model_router.generate(proof_state)
    for tactic in candidates:
        result = lean_adapter.check_file(proof_with_tactic)
        if result.success:
            return ProofResult(status="verified", tactic=tactic)
        else:
            proof_state = enrich_with_error(proof_state, result.errors)
    if no_candidate_worked:
        continue with enriched state
return ProofResult(status="exhausted", attempts=max_k)
```

**Key parameters**:
- `max_k`: maximum repair iterations (default: 64, tuned per problem tier)
- `max_candidates`: tactics per iteration (default: 10)
- Error enrichment: structured diagnostic from `lean_adapter.parse_lean_diagnostics()`

**Files**: `scripts/proof_repair.py`, `tests/test_proof_repair.py`

**Academic basis**: Kimina-Prover's Formal Reasoning Pattern (arXiv:2504.11354) alternates
informal reasoning with formal steps, repairing on verifier feedback. DeepSeek-Prover-V2 uses
Lean 4 compiler as binary reward signal.

#### 2.3 Subgoal Decomposition Pipeline

**What**: Implement two-level proving architecture.

**Architecture**:
1. Large model (API-hosted 72B or DeepSeek-Prover-V2-671B via API) decomposes theorem into subgoals
2. Each subgoal = self-contained Lean 4 `sorry`-bearing statement
3. Local 7B model solves each subgoal through proof-repair loop
4. Results assembled into complete proof

**Files**: `scripts/subgoal_decomposer.py`, `tests/test_subgoal_decomposer.py`

**Academic basis**: DeepSeek-Prover-V2 (arXiv:2504.21801) — this is the architecture that
achieved 88.9% MiniF2F and 49/658 PutnamBench. The key insight is that small models can solve
decomposed subgoals even when they cannot solve the full theorem.

#### 2.4 First Formal Proof

**What**: Select simplest formalizable problem and drive through the proof-repair loop to
`proof.verified.v1` evidence.

**Candidate problems**:
- Graceful tree conjecture for small $n$ (e.g., $n \leq 10$)
- Known textbook result from ProverBench difficulty level
- Erdős–Straus for specific $n$ (verified computationally, formalize the verification)

### Evidence Gate

At least one Lean 4 proof:
- Generated by neural model (not handwritten)
- Verified by Lean 4 compiler (zero remaining `sorry`)
- Stored in `artifacts/prover-results/<run-id>.yaml`
- Linked to experiment ledger entry

---

## Phase 3: Literature and Novelty Verification

### Goal

OMEGA gains the ability to verify novelty before claiming results.

### Estimated Duration

4–6 weeks, parallel with Phase 2.

### Tasks

#### 3.1 Semantic Scholar Adapter

**What**: Implement free-tier API client (api.semanticscholar.org, 100 req/sec).

**Per problem-id**:
1. Search by keywords extracted from problem record
2. Retrieve papers with: abstract, year, citation_count, fields of study
3. Build citation neighborhood graph
4. Output structured `literature.md` and `citation_evidence.md` in workspace

**Files**: `scripts/literature_adapter.py` (extend from Phase 1.3)

#### 3.2 arXiv Search Adapter

**What**: Supplement for fresh preprints not yet indexed by Semantic Scholar.

**API**: `export.arxiv.org/api/query` (REST, free)

**Files**: `scripts/arxiv_adapter.py`, `tests/test_arxiv_adapter.py`

#### 3.3 Novelty Packet Generator

**What**: Machine-readable novelty assessment for each problem.

**Output format**:
```yaml
problem_id: erdos-straus
timestamp: "2026-04-05T12:00:00Z"
search_queries: ["Erdős–Straus conjecture", "4/n = 1/x + 1/y + 1/z"]
total_papers_found: 47
closest_matches:
  - title: "The Erdos-Straus conjecture: new modular approaches"
    year: 2023
    citation_count: 12
    overlap_reason: "directly addresses same conjecture"
known_partial_results:
  - "Verified for n ≤ 10^14 (Swisher et al., 2015)"
  - "Verified for n with at most 2 prime factors > 13 (multiple authors)"
novelty_assessment: "extending computational bound is incremental but publishable"
confidence: C2
evidence_class: R0+E1
```

**Files**: `scripts/novelty_generator.py`, `tests/test_novelty_generator.py`

#### 3.4 Anti-Rediscovery Gate

**What**: Mandatory novelty check before entering experimentation or proving phase.

**Integration point**: `omega_workflow.py advance` at TRIAGE → PLAN transition must call
novelty check. If novelty packet shows `confidence: C1` or worse, warn operator.

**Academic basis**: Feng et al. (arXiv:2601.22401) — of 13 addressed Erdős problems, 8 had
existing solutions in the literature (≈62%).

### Evidence Gate

For each of the 3 pilot problems from Phase 1, a completed novelty packet with:
- Real citations from Semantic Scholar
- Assessed overlap with existing work
- Confidence label per evidence governance protocol

---

## Phase 4: Multi-Agent Orchestration

### Goal

OMEGA agents work as an interacting system instead of isolated scripts.

### Estimated Duration

8–12 weeks after Phase 2 + Phase 3.

### Tasks

#### 4.1 Agent Dispatch Framework

**What**: Extend `omega_workflow.py` so each stage calls the appropriate adapter or LLM chain.

**Contract**: Each agent receives structured input (problem record + workspace state) and
returns structured output (artifact + metadata).

**Stage → Agent mapping**:
```
BRIEF    → Planner (generates data_description.md)
NOVELTY  → Librarian (calls literature_adapter → novelty packet)
TRIAGE   → Analyst (scores amenability, selects route)
PLAN     → Planner + Reviewer (bounded plan with stop conditions)
EXPERIMENT → Experimentalist (calls solver/CAS adapters)
PROVE    → Prover (calls model_router → proof_repair loop)
RESULTS  → Analyst (synthesis from ledger + prover results)
PAPER    → Writer (LaTeX/Markdown from stored artifacts)
REFEREE  → Reviewer (adversarial review against evidence)
```

**Files**: `scripts/omega_workflow.py`, `scripts/agent_dispatcher.py`

#### 4.2 Librarian Agent

**Input**: problem record
**Process**: calls `literature_adapter.py` → `novelty_generator.py`
**Output**: `literature.md`, `literature_graph.md`, `citation_evidence.md`, novelty packet

#### 4.3 Experimentalist Agent

**Input**: problem record + analysis notes + route
**Process**: calls `solver_adapter.py` or `cas_adapter.py`
**Output**: experiment ledger entry, computed evidence files

#### 4.4 Prover Agent

**Input**: formalized statement + proof obligations
**Process**: calls `model_router.py` → `proof_repair.py` → `lean_adapter.py`
**Output**: `artifacts/prover-results/<run-id>.yaml`

#### 4.5 Writer Agent

**Input**: collected evidence from workspace
**Process**: generates paper/report from stored artifacts
**Output**: `paper/main.tex` or `paper/main.md`

#### 4.6 Reviewer Agent

**Input**: draft paper + evidence bundle
**Process**: adversarial review of claims vs evidence
**Output**: `input_files/referee.md` with structured findings

### Evidence Gate

One problem passes the full pipeline (BRIEF → REFEREE) without manual stage transitions.

---

## Phase 5: Benchmark Calibration and First Publication

### Goal

External calibration and first publishable result.

### Estimated Duration

6–8 weeks after Phase 4.

### Tasks

#### 5.1 ProverBench Baseline

Run OMEGA proof pipeline on a subset of ProverBench (325 problems). Record pass@k curves.
This gives objective calibration against the external benchmark.

#### 5.2 Registry Extension

Increase AI-triage coverage from 25.1% (60/239) to 50%+.
Priority: number theory (largest domain, ~120 problems) and graph theory (~60 problems).

#### 5.3 First Result Paper

Select a problem where OMEGA produced computationally novel evidence:
- Extended bound beyond published results
- Found new counterexample
- Partial formalization not previously available

Format as academic paper with:
- Full evidence bundle (evidence class ≥ C2)
- Reproducibility manifest
- Honest limitations section
- Reviewer agent sign-off

#### 5.4 FrontierMath Calibration

Do NOT claim FrontierMath capability. Instead:
- Identify which FrontierMath Tier 1 subproblems OMEGA can partially solve
- Record solve rates as calibration data
- Use for honest capability reporting

### Evidence Gate

Paper draft with:
- Evidence class ≥ C2
- Reviewer agent approval
- Reproducibility manifest with replayable commands
- All claims verifiable from stored artifacts

---

## Phase 6: Formal Assurance Wedge

### Goal

Build medium-term applied value through formal verification of real artifacts.

### Estimated Duration

12–16 weeks, parallel with Phase 5.

### Tasks

#### 6.1 PQC Formalization Spike

**What**: Select one NIST PQC standard and formalize key correctness properties in Lean 4.

**Candidate**: ML-KEM (CRYSTALS-Kyber, FIPS 203)

**Target properties**:
- Correctness: decapsulation recovers the shared secret from valid ciphertexts
- Key generation: output key pair satisfies structural constraints
- Error bounds: decryption failure probability under stated parameters

**Academic basis**: NIST FIPS 203/204/205 (2024). Long-duration demand for formal assurance
of PQC implementations.

#### 6.2 Known Results Formalization

**What**: Formalize 3–5 known number-theoretic results in Lean 4.

**Candidates**:
- Bertrand's postulate (already in mathlib4, verify OMEGA can produce it)
- Euler's formula for polyhedra (partially formalized)
- Specific Ramsey number bounds (verified computationally)

This produces concrete formal artifacts without requiring neural proving.

#### 6.3 Reproducibility Framework

**What**: Automatic `reproducibility.md` generation from experiment history and evidence bundle.

Every workspace gets:
- Exact software versions
- Exact commands to reproduce
- Artifact checksums
- Environment requirements

### Evidence Gate

At least one formal Lean 4 artifact verifying a non-trivial statement, with full evidence chain.

---

## Cross-Phase Recommendations

### Modeling Recommendations

1. **Start with DeepSeek-Prover-V2-7B**: workstation-friendly, open-weight, 32K context.
   Hub: `huggingface.co/deepseek-ai/DeepSeek-Prover-V2-7B`.

2. **LeanCopilot as integration surface**: v4.28.0, MIT license, ExternalGenerator API.
   Do not build a custom Lean-LLM bridge.

3. **Semantic Scholar API for literature**: free, structured JSON, 100 req/sec, citation graph.

4. **FrontierMath as calibration, not target**: <2% SOTA solve rate. Use for honest assessment.

5. **Post-quantum crypto as applied wedge**: FIPS 203/204/205 create funded, long-duration demand.

6. **First result should be computational**: extending bounds is more realistic than formal proof
   as a first output.

7. **Process Advantage Verifiers for candidate ranking**: PAV-style step scoring
   (arXiv:2410.08146) gives +8% accuracy over random selection.

### Anti-Goals

1. **Do not expand the registry** until the pipeline closure loop works on 3 problems.
2. **Do not build a custom Lean-LLM bridge** when LeanCopilot provides one.
3. **Do not claim FrontierMath-level capability** at any point in this plan.
4. **Do not skip literature checks** before claiming novelty.
5. **Do not treat LLM judging as verification**: formal tools (Lean, Z3) are ground truth.

---

## Success Metrics

| Phase | Minimum Success Signal |
|-------|----------------------|
| Phase 1 | 3 T1 problems produce evidence bundles with replayable commands |
| Phase 2 | 1 neural-generated Lean proof passes compiler verification |
| Phase 3 | 3 novelty packets with real citations from Semantic Scholar |
| Phase 4 | 1 problem passes full pipeline without manual stage transitions |
| Phase 5 | 1 paper draft at evidence class ≥ C2 with reviewer approval |
| Phase 6 | 1 formal Lean 4 artifact verifying a non-trivial statement |

---

## Academic References

This plan is grounded in the following primary sources:

1. DeepSeek-AI. *DeepSeek-Prover-V2.* 2025. [GitHub](https://github.com/deepseek-ai/DeepSeek-Prover-V2)
2. Wang, H. et al. *Kimina-Prover Preview.* arXiv:2504.11354, 2025.
3. Song, P. et al. *Lean Copilot.* arXiv:2404.12534, NeuS 2025.
4. Lu, S. et al. *Process Advantage Verifiers.* arXiv:2410.08146, 2024.
5. Glazer, E. et al. *FrontierMath.* arXiv:2411.04872, 2024.
6. Feng, T. et al. *Semi-Autonomous Mathematics Discovery with Gemini.* arXiv:2601.22401, 2026.
7. Verbeken, B. et al. *VUB Vibe-Proving.* arXiv:2602.18918, 2026.
8. NIST. *FIPS 203/204/205 (PQC Standards).* 2024.
9. Yang, K. et al. *LeanDojo.* arXiv:2306.15626, NeurIPS 2023.
10. Feng, T. et al. *Towards Autonomous Mathematics Research.* arXiv:2602.10177, 2026.

---

*This plan is a living document. Update when external landscape changes or phases complete.*
