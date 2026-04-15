# Problem Brief — Thomson Problem

- Registry ID: thomson-problem
- Title: Thomson problem (Smale's 7th problem)
- Tier: T1-computational
- Amenability Score: 8/10
- Route: experiment-first (optimization + numerical certification)

## Problem Statement

Find the configuration of N point charges on the unit sphere S² that minimizes
the total Coulomb energy: U(N) = sum_{i<j} 1/|r_i - r_j|
where r_i ∈ S² for all i.

## Current Status (April 2026)

Rigorously proved optimal only for N = 1,2,3,4,5,6,12.
Numerically known putative minima for N ≤ 470+ (Cambridge Cluster Database).
Key structures: N=4 tetrahedron, N=6 octahedron, N=8 square antiprism (NOT cube),
N=12 icosahedron, N=24 snub cube, N=48/60 geodesic polyhedra.
Asymptotic: U(N) ~ N²/2 − 0.5526...N^{3/2}.
Related: Smale's 7th problem — algorithm within c·log(N) of minimum.

## Attack Vectors

### V1: Multi-Start Gradient Optimization
For each target N: 1000+ random starts, L-BFGS-B with spherical projection,
catalogue all local minima, compare with Cambridge database.

### V2: Basin-Hopping + Simulated Annealing
For N where V1 doesn't match known best: basin-hopping (Wales & Doye),
SA with adaptive cooling, genetic algorithm.

### V3: Rigorous Certification
For small N (7–20): interval arithmetic, Hessian positive definite check,
computer-assisted proof attempt for N=7,8.

### V4: Structure Discovery
Defect distribution, symmetry breaking, shell-filling correlation with periodic table.

## Success Condition

1. Improved energy for any N > 65 → update to Cambridge DB
2. New rigorous proof for N ∈ {7,8,9,10,11} → significant paper
3. Novel algorithm outperforming basin-hopping → publishable
4. Structural insight on defect topology → publishable note

## Stop Conditions

- All configurations match Cambridge DB to 12+ digits for N ≤ 200
- No rigorous certification achievable without interval arithmetic
- Compute budget exhausted without finding lower energy
