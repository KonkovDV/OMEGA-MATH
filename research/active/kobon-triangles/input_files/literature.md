# Literature Packet — Kobon Triangles

## Seed Papers

1. Fujimura K. Kobon original problem statement (1903–1983).
2. Clément G, Bader J (2007). Tighter Upper Bound for the Number of Kobon Triangles.
3. Bartholdi N, Blanc J, Loisel S (2008). On simple arrangements of lines and pseudo-lines. arXiv:0706.0723
4. Savchuk P (2025). Constructing Optimal Kobon Triangle Arrangements via Table Encoding, SAT Solving, and Heuristic Straightening. arXiv:2507.07951
5. Zarzuelo Urdiales A (2026). Lower bound construction for Kobon triangles. Archivara.
6. Forge D, Ramírez Alfonsín JL (1998). Straight line arrangements in the real projective plane. DCG 20(2):155–161.

## Known Results

- Tamura's bound: N(k) ≤ floor(k(k-2)/3).
- Clément–Bader: bound unachievable for k ≡ 0,2 (mod 6).
- Optimal known for k = 3–13, 15–17, 19, 21, 23, 25, 27, 29, 31, 33.
- Savchuk 2025: SAT solver proved K(11) = 32 (previously gap).
- Even k improved bound: floor(k(k-7/3)/3).

## Best Current Bounds

| k | Lower (best) | Upper | Status |
|---|-------------|-------|--------|
| 18 | 93 | 94 | GAP |
| 20 | 116 | 117 | GAP |
| 22 | 143 | 144 | GAP |
| 26 | 203 | 205 | GAP |

## Key Mathematical Tools

- Oriented matroids / chirotopes
- SAT/SMT solving for combinatorial search
- Pseudoline arrangement theory
- Heuristic straightening (gradient descent)
- Existential theory of the reals (stretchability is ETR-complete)

## Contrasting Evidence

## Collision Check

## Risks
