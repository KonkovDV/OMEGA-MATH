# Problem Brief — Kobon Triangles

- Registry ID: kobon-triangles
- Title: Kobon triangles
- Tier: T1-computational
- Amenability Score: 8/10
- Route: experiment-first (SAT + geometric heuristic)

## Problem Statement

Find the largest number N(k) of non-overlapping triangles whose sides lie on
an arrangement of k straight lines in the Euclidean plane.

Tamura's upper bound: N(k) ≤ floor(k(k-2)/3).
Clément–Bader (2007): cannot be achieved when k ≡ 0,2 (mod 6).

## Current Status (April 2026)

Optimal known for k = 3–13, 15–17, 19, 21, 23, 25, 27, 29, 31, 33.
Key open gaps: k=18 (best=93, bound=94), k=20 (best=116, bound=117).
Savchuk (2025): SAT-based proof that K(11)=32.
Zarzuelo Urdiales (2026): iterative lower bound construction.

## Attack Vectors

### V1: SAT Encoding of Pseudoline Arrangements
Encode chirotope (oriented matroid) as Boolean variables.
Triangle counting as 3-clique detection on arrangement graph.
Maximize triangle count subject to arrangement constraints.

### V2: Target k=18 and k=20 Gaps
Either find constructions reaching the bound, or prove unachievability.

### V3: Geometric Realization (Straightening)
Given maximal pseudoline arrangement, "straighten" into actual lines
using gradient descent on slopes/intercepts while maintaining combinatorial type.

## Success Condition

1. New optimal construction for any open k → OEIS update + paper
2. SAT-based unachievability proof → publishable
3. Improved general bounds → publishable

## Stop Conditions

- SAT instances exceed compute for k ≥ 18
- All constructions match known best without improvement
- Straightening fails on all maximal pseudoline arrangements
