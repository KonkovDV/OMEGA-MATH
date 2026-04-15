# Attack Plan — Thomson Problem

Execution status: **Phase 1, Phase 2, and a bounded Phase 3 numerical certification scaffold are implemented and runnable now. Phase 4 remains planned work, and a fully rigorous interval-based certification layer is still unshipped.**

## Phase 1: Multi-Start Optimization (Python + scipy, ~2h)

**Goal**: Reproduce known best energies for N ≤ 200 and search for improvements.

**Method**:
1. Random initial points on S² (Fibonacci lattice for seeding)
2. L-BFGS-B with spherical projection
3. 1000 restarts per N value
4. Compare with Cambridge Cluster Database values

**Script**: `experiments/phase1_multistart.py`

## Phase 2: Basin-Hopping (Python + scipy, ~4h)

**Goal**: For N where Phase 1 doesn't match known best, use advanced methods.

**Method**:
1. Basin-hopping with perturbation = random rotation of random subset
2. Simulated annealing with Lundy-Mees cooling
3. Genetic algorithm with spherical crossover
4. Log all distinct local minima

**Script**: `experiments/phase2_basin_hopping.py`

## Phase 3: Numerical Certification Scaffold (Python + mpmath, ~1h)

**Goal**: For bounded small-`N` Thomson cases, build numerical evidence for local-minimum candidacy without pretending to have a rigorous proof.

**Method**:
1. Read `best_config` from the persisted Phase 2 artifact
2. Recompute the energy at higher precision with `mpmath`
3. Measure tangent-force residuals instead of trusting the optimizer termination flag alone
4. Build a tangent-space finite-difference Hessian and treat three near-zero modes as expected rotational symmetry directions
5. Classify the result as a numerical local-minimum candidate or review-needed, never as a proof

**Script**: `experiments/phase3_certify.py`

## Phase 4: Structural Analysis (Python + matplotlib, ~1h)

**Goal**: Analyze defect patterns and generate publication-quality visualizations.

**Method**:
1. Voronoi tessellation on sphere for each optimal config
2. Count 5-fold and 7-fold defects
3. Correlate with N=12 icosahedral template
4. Generate 3D plots of optimal configurations

**Script**: `experiments/phase4_structure.py`

## Agent Workflow

```
Planner → [Phase 1 sweep N=2..200] → compare with Cambridge DB
       → [Phase 2 for N with energy gap] → advanced optimization
       → [Phase 3 for N=7..13, next N=14..20] → numerical certification scaffold
       → [Phase 4 for all optima] → structural analysis
       → Writer drafts results note
```
