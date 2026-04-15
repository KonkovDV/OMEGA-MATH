# Attack Plan — Erdős–Straus Conjecture

Execution status: **Phase 1 and Phase 2 are implemented and runnable now. Phase 3 is still planned research work, not shipped code.**

## Phase 1: Covering Congruence Machine (Python, ~2h compute)

**Goal**: For each of the 6 uncovered residues mod 840 (r ∈ {1, 121, 169, 289, 361, 529}),
find primes q such that r is NOT a quadratic residue mod q, then construct a polynomial
identity for n ≡ r (mod q).

**Method**:
1. For each uncovered r, enumerate primes q from 7 to 10^6
2. Check Legendre symbol (r/q) = -1
3. When found, try parametric decomposition: search for a,b,c polynomials in n such that
   4/n = 1/a(n) + 1/b(n) + 1/c(n) holds for n ≡ r (mod q)
4. Verify on first 10^4 primes in that residue class

**Script**: `experiments/phase1_covering.py`

## Phase 2: Parametric Family Brute Search (Python, ~4h compute)

**Goal**: For "hard" primes p ≡ 1 (mod 24), find all solutions up to denominator 10^8.

**Method**:
For each prime p: iterate over k ∈ {1, ..., p²} and find (y,z) such that
4/(p) = 1/(pk) + 1/y + 1/z → 4pk - p = pk(1/y + 1/z) → solve Diophantine.

**Script**: `experiments/phase2_parametric.py`

## Phase 3: Verification Frontier (Python + C extension, GPU optional)

**Goal**: Push verification past 10^17 toward 10^18 using identity-based sieve.

**Method**:
1. Implement sieve that skips all n covered by known modular identities
2. For remaining n (only primes ≡ 1 mod 24), run decomposition search
3. Use GMP for arbitrary precision

**Script**: `experiments/phase3_frontier.py`

## Agent Workflow

```
Planner → [Phase 1] → Experimentalist runs covering.py
       → [Phase 2] → Experimentalist runs parametric.py
       → Analyst reviews results → Librarian checks novelty
       → Writer drafts note if new identities found
```
