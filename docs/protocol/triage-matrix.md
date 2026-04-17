# OMEGA Triage Matrix

The master queue lives in math/registry/triage-matrix.yaml. This file defines how problems are scored and how the queue should be used.

## Goal

Rank open mathematical problems by current AI usefulness, not by fame.

A problem can be mathematically legendary and still be a poor AI target. OMEGA optimizes for research throughput:

- direct computability
- counterexample accessibility
- measurable partial progress
- reproducible outputs
- publishable intermediate results

## Scoring Axes

Each problem gets an amenability score from 0 to 10.

1. Searchability
   Can brute-force, SAT, SMT, or heuristic search explore meaningful instances?
2. Experimental signal
   Can computation produce nontrivial evidence, bounds, or candidate structure?
3. Formalizability
   Can the problem or partial results be encoded in Lean 4, Coq, or symbolic systems?
4. Feedback speed
   Does an attempted approach fail quickly enough to support iteration?
5. Publication yield
   Are partial improvements likely to be independently valuable?

## Tier Definitions

### T1 computational

Score: 7 to 10

Use when:
- bounded search is meaningful
- exact instances can be solved
- counterexamples may be found by computation

Expected outputs:
- new bounds
- counterexamples
- verified exhaustive results
- optimized constructions

### T2 experimental

Score: 4 to 6

Use when:
- large-scale computation yields evidence
- data can refine conjectures
- patterns can be measured before they are proved

Expected outputs:
- empirical laws
- conjecture refinements
- verification to larger bounds
- numerical datasets and plots

### T3 pattern

Score: 2 to 4

Use when:
- analogy, structural comparison, or cross-domain synthesis may help
- direct proof is unlikely but reframing is plausible
- a target theorem can already be stated precisely and a classical scaffold or reduction template exists

Expected outputs:
- proof sketches
- proof-obligation lists
- equivalence proposals
- simplified reformulations
- literature syntheses

### T4 structural

Score: 1 to 2

Use when:
- deep theory is required
- AI is mainly a formalization and support layer, or a human-verified vibe-proving assistant on strongly scaffolded subclaims

Expected outputs:
- Lean formalizations of lemmas
- dependency maps of known proofs
- proof-obligation packets for correctness-critical steps
- strategy memos for experts

### T5 foundational

Score: 0 to 1

Use when:
- the problem is likely outside current AI proving capability
- work is mostly literature and formal context building

Expected outputs:
- annotated surveys
- theorem dependency maps
- formalized known results

## Queue Policy

Default order of work:

1. Highest-score T1 items with moderate compute cost
2. T2 items where a new bound is realistically achievable
3. T1/T2 items with active public benchmarks or distributed-computing analogs
4. T3 items that connect multiple already-active domains
5. T4/T5 only when they support downstream work or formalization goals

## Stop Rules

A problem should be deprioritized when:

- the search space grows faster than verification value
- repeated runs produce no new structural information
- literature already saturates the same computational angle
- the required compute exceeds the current research budget

## Promotion Rules

A problem can move upward in priority when:

- a new reduction makes it searchable
- a formal encoding becomes available
- a fresh empirical pattern suggests a tractable subclass
- external results narrow the open core to a computational target
