# Attack Plan — Kobon Triangles

Execution status: **Phase 1 is implemented and runnable now. Phase 2 and Phase 3 remain planned work and should not be treated as shipped code.**

## Phase 1: Pseudoline Arrangement Generator (Python, ~1h)

**Goal**: Enumerate all pseudoline arrangements for small k and count triangles.

**Method**:
1. Represent arrangement as chirotope (sign vector of all 3-tuples)
2. Enumerate valid chirotopes satisfying axioms
3. Count triangles = bounded faces with exactly 3 sides
4. For k ≤ 12: exhaustive. For k > 12: heuristic with simulated annealing.

**Script**: `experiments/phase1_pseudoline_enum.py`

## Phase 2: SAT Encoding (Python + PySAT, ~4h)

**Goal**: For k=18 and k=20, use SAT to determine if upper bound is achievable.

**Method** (following Savchuk 2025):
1. Encode crossing sequence of k lines as Boolean variables
2. Add clauses ensuring valid arrangement (no triple crossings etc.)
3. Encode triangle count ≥ target
4. Run CaDiCaL/Kissat SAT solver

**Script**: `experiments/phase2_sat_kobon.py`

## Phase 3: Heuristic Straightening (Python + scipy, ~2h)

**Goal**: Given a maximal pseudoline arrangement, realize it with straight lines.

**Method**:
1. Start from pseudoline arrangement with known good triangle count
2. Parameterize each line as (slope, intercept)
3. Loss function: crossing order violations + arrangement degeneracy penalty
4. Optimize with L-BFGS-B

**Script**: `experiments/phase3_straighten.py`

## Agent Workflow

```
Planner → [Phase 1 for small k] → verify known results
       → [Phase 2 for k=18,20] → SAT solver
       → [Phase 3 for any SAT solutions] → straightening
       → Analyst checks if result is new → Writer drafts
```
