---
title: "OMEGA Academic Architecture Audit"
status: active
version: "1.0.0"
date: "2026-04-09"
role: audit-report
audience: internal+academic
evidence_class: R0+E1
confidence: C3
tags: [omega, audit, architecture, gaps, recommendations, SOTA]
---

# OMEGA Academic Architecture Audit Report

**Date**: 2026-04-09
**Scope**: Full codebase review + SOTA comparison
**Method**: Static analysis, protocol review, external evidence cross-reference

---

## 1. Executive Summary

OMEGA v0.4.0 is an unusually well-structured AI-for-math research platform for its maturity stage. The registry (60+ problems across 15 domains), triage matrix (5-tier amenability scoring), 7-agent team architecture, evidence governance protocol, and verification pipeline are all internally consistent and grounded in externally verified donor patterns (Denario, CMBAgent, LSST DESC).

The protocol layer is stronger than the runtime layer. The major gap is that the Python runtime (`scripts/`) is a collection of CLI adapters with no execution orchestration connecting the agents. The protocol *describes* how agents should interact; the runtime cannot *enforce* it yet.

### Verdict

| Dimension | Grade | Notes |
|-----------|-------|-------|
| Problem catalog & registry | A | 60+ problems, JSON Schema validated, 15 domains |
| Triage methodology | A | 5-axis scoring, 5-tier routing, externally grounded |
| Protocol design | A- | Verification pipeline, evidence governance, LLM-proof rules are SOTA-aware |
| Agent architecture | B+ | Good role separation; no runtime orchestration |
| Python runtime | B- | CLI adapters work; no inter-adapter pipeline; no state machine |
| Lean/formal integration | C+ | Adapter spec exists; no live Lean toolchain wired |
| Solver integration | B | SAT (python-sat), SMT (z3), CAS (sympy) adapters present but minimal |
| Experiment tracking | B+ | Ledger YAML spec + evidence-bundle spec; no automated checksumming |
| Test coverage | B | 23 test files, schema validation, workflow logic; integration gaps |
| Research output artifacts | B+ | Literature, citation, prover-result contracts; not yet exercised end-to-end |

---

## 2. Codebase Inventory

### 2.1 Scale

| Component | Count |
|-----------|-------|
| Registry domain YAML files | 15 |
| Registered problems | ~60 |
| Protocol documents | 17 |
| Agent definitions (YAML) | 8 (7 roles + 1 team) |
| Python scripts (`scripts/`) | 12 CLI entry points |
| Test files (`tests/`) | 23 |
| Research reports | 6 |
| Active problem workspaces | 3 (erdos-straus, kobon-triangles, thomson-problem) |

### 2.2 Dependency Profile

Core: `PyYAML 6.0.1`, `jsonschema 4.23.0`.
Optional extras: `z3-solver ≥4.12`, `python-sat ≥1.8`, `sympy ≥1.13`, `numpy ≥1.26`, `scipy ≥1.13`, `mpmath ≥1.3`, `matplotlib ≥3.8`.

The dependency surface is deliberately minimal, which is correct per OMEGA's standalone mandate.

---

## 3. Architecture Analysis

### 3.1 Registry Design (Grade: A)

The schema (`registry/schema.json`) is JSON Schema 2020-12 compliant with 15 mathematical domains, 6 status values, a formal-statement block, references with DOI and MathSciNet support, and an AI-amenability block with the 5-axis scoring system.

**Strengths**:
- Amenability axes (searchability, signal, formalizability, speed, yield) are the right decomposition — they separate what AI can do from what is mathematically hard.
- Schema validation is wired into both the runner and a dedicated `validate_registry.py` CLI.
- Domain files are separate YAMLs under `registry/domains/`, enabling git-conflict-free parallel editing.

**Gaps**:
- No `last_updated` timestamp per problem entry (only per domain file).
- No backward link from workspace to registry entry (the workspace knows its problem ID, but the registry doesn't know which workspaces exist).

### 3.2 Triage Matrix (Grade: A)

The 5-tier system (T1-computational through T5-foundational) correctly prioritizes by AI-amenability rather than mathematical fame. The routing table in `agents/team.yaml` maps tiers to agent roles, and the workflow controller reads this mapping at runtime.

**Strengths**:
- The scoring rubric is explicit and numeric (0-10 with axis breakdown).
- The matrix is a single YAML file that serves as the master work queue.
- Active routing: `omega_workflow.py triage <id>` reads the matrix and assigns execution role + route.

**Gaps**:
- No temporal decay: a problem triaged 6 months ago has the same score as one triaged today, even if external progress changed the landscape.
- No automated re-triage trigger when new SOTA results arrive.

### 3.3 Agent Team Architecture (Grade: B+)

Seven agent roles (Planner, Librarian, Analyst, Experimentalist, Prover, Writer, Reviewer) with a defined execution order and quality gates.

**Strengths**:
- The Denario-inspired artifact chain (data-description → literature-memo → idea-note → method-plan → result-summary → draft → referee-report) enforces sequential evidence building.
- Quality gates include explicit evidence class, reproducibility record, literature collision check, and reviewer signoff.
- The team YAML is readable by both humans and the workflow controller.

**Critical gap**: The agents are *defined* but not *instantiated*. There is no LLM-backed agent runtime — the YAML files describe roles and expected I/O, but no code creates agent sessions, passes context between roles, or enforces the artifact chain. This is the single largest gap in the system.

### 3.4 Python Runtime (Grade: B-)

12 CLI entry points registered in `pyproject.toml`:

| CLI | Function |
|-----|----------|
| `omega-runner` | Scaffold + validate + run problems |
| `omega-workflow` | Triage + status + advance state machine |
| `omega-validate-registry` | Schema validation |
| `omega-scaffold-problem` | Create workspace from registry |
| `omega-query` | Query experiment ledgers |
| `omega-literature` | Literature adapter |
| `omega-lean` | Lean 4 adapter |
| `omega-solve` | SAT/SMT solver adapter |
| `omega-cas` | CAS adapter |
| `omega-generate-index` | Registry index generation |
| `omega-generate-experiment-index` | Experiment index |

**Strengths**:
- `omega_workflow.py` implements a real state machine with stages (triage → research → experiment/prove/survey → write → review → close), transitions, and blocking conditions.
- `omega_runner.py` validates schemas, creates workspace scaffolds, and manages the experiment ledger.
- All adapters have a consistent CLI interface pattern.

**Gaps**:
- Adapters are shims that validate inputs and write placeholder files — none actually invoke external tools (no `lean` binary call, no `z3` invocation, no `pysat` solve).
- No inter-adapter pipeline: there is no code that runs Librarian → Analyst → Experimentalist in sequence with context passing.
- The workflow state machine is correctly designed but untested at the integration level.

### 3.5 Verification Pipeline (Grade: A-)

The 3-level evidence system (computational claim, structural claim, proof claim) with 6 verification stages (artifact check → internal consistency → reproducibility → literature collision → review challenge → publication gate) is rigorous.

**Strengths**:
- LLM-assisted proof rules are carefully bounded (LLM output is "candidate, not lemma"; no LLM-judge-only upgrades).
- The evidence governance document correctly separates R0/R1/E1/E2/H classes with confidence labels C1-C3.
- Anti-overclaiming rules with specific downgrade patterns ("proved" → "draft proof candidate").
- Literature-positioning requirements demand local citation evidence packets.

**Gap**: The verification pipeline is entirely manual — no automated checks run. The evidence-bundle YAML spec exists, but no code checksums artifacts or validates bundles.

### 3.6 Formal Math Integration (Grade: C+)

The `lean-execution-adapter.md` protocol document describes how Lean 4 should be invoked, the `lean_adapter.py` script provides the CLI surface, and the `lean-bootstrap.md` document specifies the Lean 4 + Mathlib4 setup.

**Gap analysis against SOTA**:

| SOTA Tool | Status in OMEGA |
|-----------|----------------|
| DeepSeek-Prover-V2 (671B/7B) | Referenced in landscape report; no integration code |
| Kimina-Prover (72B/7B/1.5B) | Referenced; no integration |
| LeanCopilot (v4.28.0) | Identified as primary integration surface; no code |
| LeanDojo/ReProver | Identified as foundation layer; no code |
| Lean 4 compiler | `lean_adapter.py` exists but doesn't invoke `lean` binary |

This is the weakest area of the system. The protocol is correctly designed around the SOTA landscape, but zero runtime integration exists.

---

## 4. SOTA Comparison (April 2026)

### 4.1 Neural Theorem Proving

| System | MiniF2F-test | PutnamBench | Architecture | Availability |
|--------|-------------|-------------|--------------|-------------|
| DeepSeek-Prover-V2-671B | 88.9% | 49/658 | Recursive subgoal decomposition + RL | Open-weight (HuggingFace) |
| Kimina-Prover-72B | ~80.7% (pass@8192) | — | Whole-proof generation + RL, Formal Reasoning Pattern | Open-weight distilled 1.5B/7B |
| LeanCopilot | 74.2% automation | — | LLM copilot for tactic suggestion + proof search | MIT, Lean 4 v4.28.0 |

OMEGA's protocol correctly identifies DeepSeek-Prover-V2 as the dominant paradigm and LeanCopilot as the primary integration surface. The two-level architecture (large model decomposes, small model proves) is the right design choice.

### 4.2 Optimization Landscape (Thomson Problem)

The Thomson problem workspace in OMEGA targets configurations of N point charges on a sphere. Current SOTA:

- Known exact solutions: N = 1-6, 12.
- Best numerical solutions tabulated to N = 470+ (Cambridge Cluster Database, Wales group).
- Algorithms used: steepest descent, genetic algorithms, constrained global optimization, random walks.
- **AI opportunity**: RL-based optimization + differentiable physics can produce new configurations for N values where current best-known energies have nonzero dipole moments (those are suspect non-optimal).

OMEGA's approach tag ("optimization + monte-carlo + RL") is correct but underspecified — no specific algorithm choice or benchmark comparison.

### 4.3 Computational Number Theory (Erdős–Straus)

Current SOTA: verified for n ≤ 10^14 by parametric families + covering congruences.

**AI-amenable attack surfaces**:
1. Covering congruence completion: finite check that remaining residue classes have representations.
2. Parametric family discovery: search for new 4/n decomposition families in unexplored modular arithmetic ranges.
3. SAT/SMT encoding of the covering system completeness.

OMEGA's triage score of 8 and approach "parametric-search + covering-congruences" is accurate.

### 4.4 Combinatorial Geometry (Kobon Triangles)

Current SOTA: known optimal values for small n, with gaps at specific n values. The problem is SAT-encodable for small instances.

OMEGA's approach "search + SAT" is correct; the python-sat dependency is the right tool.

---

## 5. Gap Analysis: Ranked by Impact

### Gap 1: No Agent Runtime (Impact: CRITICAL)

**What exists**: 7 agent role definitions in YAML, a team configuration, and a state machine in `omega_workflow.py`.

**What's missing**: No code instantiates LLM-backed agents, passes context between roles, or enforces the artifact pipeline. The entire right side of the "agents → artifacts → verification" chain is unimplemented.

**Recommendation**: Implement a minimal orchestrator that:
1. Takes a problem ID and stage from the workflow state machine.
2. Constructs a prompt for the appropriate agent role using the YAML definition.
3. Invokes an LLM API (Claude, GPT-5, DeepSeek, or local model via litellm/openrouter).
4. Parses the output into the expected artifact format.
5. Advances the state machine.

This does not require a complex agent framework. A ~200-line Python module that reads agent YAML, constructs prompts, calls an API, and writes artifact files would close 80% of the gap.

### Gap 2: No Lean 4 Toolchain Integration (Impact: HIGH)

**What exists**: `lean_adapter.py` CLI, `lean-bootstrap.md` spec, `lean-execution-adapter.md` protocol, `prover-result-contract.md` artifact schema.

**What's missing**: No actual Lean 4 invocation. No connection to LeanCopilot, LeanDojo, or DeepSeek-Prover.

**Recommendation**: Wire `lean_adapter.py` to invoke Lean 4 via subprocess (for proof checking) and LeanCopilot's ExternalGenerator API (for LLM-assisted proving). This is the highest-leverage integration because it converts the Prover agent from a specification into a functioning component.

### Gap 3: No Solver Execution (Impact: MEDIUM)

`solver_adapter.py` and `cas_adapter.py` exist as CLI entry points but don't invoke z3, pysat, or sympy.

**Recommendation**: For T1-computational problems (highest amenability), implement:
- A z3 wrapper in `solver_adapter.py` that takes a problem's SMT-LIB encoding and returns sat/unsat + model.
- A pysat wrapper for SAT encodings.
- A sympy wrapper in `cas_adapter.py` for symbolic computation.

These are ~50–100 lines each and directly enable the Experimentalist agent for the 8+ T1 problems.

### Gap 4: No Automated Evidence Checksumming (Impact: MEDIUM)

The `evidence-bundle.yaml` spec requires SHA-256 checksums for artifacts, but no code computes or verifies them.

**Recommendation**: Add a `verify_evidence_bundle()` function that walks artifacts and checks SHA-256 hashes. This is ~30 lines and makes the verification pipeline executable.

### Gap 5: No Inter-Workspace Dependency Tracking (Impact: LOW)

Problems can depend on each other (e.g., results on covering congruences may apply to multiple number-theory problems), but no dependency graph exists.

**Recommendation**: Add an optional `depends_on` field to the registry schema pointing to other problem IDs. This enables cascading re-triage when a dependent problem's landscape changes.

---

## 6. Strengths That Should Not Be Changed

1. **Standalone mandate**: OMEGA correctly avoids depending on MicroPhoenix runtime. The separation is clean and should be preserved.
2. **Evidence governance**: The R0/R1/E1/E2/H evidence class system with anti-overclaiming rules is more rigorous than any comparable open-source AI-for-science project.
3. **Catalog-first approach**: Starting from a comprehensive problem registry rather than ad-hoc attacks on famous problems is the correct research strategy.
4. **5-axis triage**: Separating AI-amenability from mathematical difficulty is a genuine methodological contribution.
5. **Verification pipeline**: The 3-level, 6-stage pipeline with LLM-proof-specific rules is well-designed.
6. **Minimal dependencies**: PyYAML + jsonschema core, with optional solver/math extras, is the right dependency strategy.
7. **Research intelligence layer**: The donor extraction from Denario, CMBAgent, LSST DESC, and the vibe-proving evidence from Verbeken et al. is properly attributed and architecturally separated.

---

## 7. Prioritized Roadmap Recommendations

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| P0 | Minimal agent orchestrator (LLM API + prompt construction from agent YAML + artifact writer) | 2-3 days | Unlocks entire agent pipeline |
| P1 | Wire `lean_adapter.py` to Lean 4 binary + LeanCopilot ExternalGenerator | 1-2 days | Enables Prover agent |
| P1 | Wire `solver_adapter.py` to z3/pysat | 1 day | Enables T1 Experimentalist |
| P2 | Evidence bundle checksumming | 0.5 day | Verification pipeline becomes executable |
| P2 | End-to-end integration test: scaffold → triage → research → experiment → write → review for one T1 problem | 1-2 days | Proves full pipeline |
| P3 | Temporal decay / auto-re-triage | 1 day | Keeps triage matrix current |
| P3 | Cross-workspace dependency graph | 0.5 day | Enables cascading research |

---

## 8. Academic Positioning

OMEGA's closest comparators:

| System | Focus | OMEGA's advantage |
|--------|-------|-------------------|
| Denario (arXiv:2510.26887) | General science paper generation | OMEGA has math-specific triage, formal verification, solver integration |
| CMBAgent (arXiv:2507.07257) | Domain-specific (cosmology) agent | OMEGA is domain-general across all mathematics |
| AlphaProof (Google DeepMind) | Competition math proving | OMEGA is open, registry-based, handles non-proof problems |
| FunSearch (Google DeepMind) | Evolutionary program search | OMEGA handles proof, survey, and experiment workflows, not just search |
| LEGO-Prover (arXiv:2310.00656) | Growing Lean library via proved lemmas | OMEGA incorporates proving as one lane among many |

OMEGA's unique contribution is the **catalog-first, triage-driven** approach that treats the entire landscape of open problems as a prioritized work queue rather than attacking individual famous conjectures. This is a genuine methodological innovation with no direct open-source counterpart.

---

## 9. Conclusion

OMEGA is a well-designed research platform with a strong protocol layer and a weaker runtime layer. The path from current state to a functioning end-to-end system is short (the orchestrator + lean adapter + solver adapter fill the critical gaps). The evidence governance and triage methodology are publication-quality and could stand as independent contributions.

The single most impactful next step is a minimal agent orchestrator that connects the existing state machine to LLM API calls, enabling the 7-agent pipeline to execute for the first time.
