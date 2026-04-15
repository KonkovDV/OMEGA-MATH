---
title: "Thomson Problem — Methods"
status: active
version: "1.3.1"
last_updated: "2026-04-08"
tags: [thomson-problem, methods, optimization, scipy, reproducibility]
mode: explanation
---

# Thomson Problem — Methods

## Scope of This Packet

This methods note documents the **currently shipped** experiment surface in:

- `experiments/phase1_multistart.py`
- `experiments/phase2_basin_hopping.py`
- `experiments/phase3_certify.py`

Implemented now:

- Phase 1 multi-start local optimization with analytic gradients
- Phase 2 basin-hopping global search with persisted geometry-level evidence
- Phase 3 numerical certification scaffold for bounded high-precision rechecks of persisted Phase 2 minima

Still planned, not yet shipped:

- Phase 4 structural analysis
- fully rigorous interval certification

Any statement in this packet about rigorous proof or about Phase 4 is a roadmap statement taken from
`planning/attack_plan.md`, not a claim that those phases already exist in code.

## Research Objective

The current executable goal is modest and explicit:

1. reproduce benchmark energies for bounded `N`
2. measure restart stability on 1 CPU
3. persist geometry for the best minima instead of reporting scalar energies alone
4. identify where simple multi-start L-BFGS-B stops being an adequate search surface

This is a **reproduction, baseline-establishment, and bounded numerical-certification workflow**, not a proof workflow.

## Implemented Numerical Stack

### Representation

- A configuration is stored as `N` points in `R^3`.
- Every evaluation re-projects those points back to the unit sphere `S^2` by
	normalizing each point.
- This avoids a more complex intrinsic parameterization while preserving the sphere
	constraint numerically.

### Objective Function

The code minimizes the Coulomb energy

$$
U(N) = \sum_{i < j} \frac{1}{\|r_i - r_j\|}
$$

with a vectorized pairwise-distance implementation for the forward pass and an
analytic gradient projected onto each point's tangent plane.

### Local Optimizer

The local solver is `scipy.optimize.minimize(..., method="L-BFGS-B")`.

This choice is justified operationally:

- the official SciPy documentation states that `minimize(method='L-BFGS-B')`
	minimizes a scalar function of one or more variables using the limited-memory
	BFGS algorithm
- it is efficient for smooth objectives where gradients are available
- in this repository it acts as a robust local descent engine inside a larger
	multi-start strategy

The current implementation does **not** use explicit box constraints. The sphere
constraint is enforced by repeated projection, so L-BFGS-B is being used here as a
stable quasi-Newton optimizer rather than as a bound-heavy constrained solver.

### Multi-Start Policy

Each run uses:

- one Fibonacci-lattice seed for a structured low-discrepancy initialization
- the remaining starts from random Gaussian points projected to the sphere
- an explicit random seed to keep the run reproducible

This follows a simple but defensible rule for rugged energy landscapes: do not trust a
single local solve, even when one start looks good.

### Global Optimizer Layer

Phase 2 wraps the same objective and gradient in SciPy's `basinhopping` driver.

The current shipped design is intentionally narrow and reproducible:

- one run family uses a Fibonacci-lattice start and the remaining starts use seeded random initial configurations
- each basin-hopping step rotates a random subset of points and optionally injects a small jitter
- every accepted minimum is re-projected to the sphere and filtered by a minimum pair-distance check
- callback capture records distinct minima, top minima, and the full `best_config`
- each saved `best_config` is re-evaluated after the run to confirm that the persisted geometry matches the reported energy

This means Phase 2 upgrades the evidence surface in two important ways:

1. it is a real global-search layer rather than repeated independent local solves
2. it produces geometry-level artifacts that can be rechecked later

### Numerical Certification Layer

Phase 3 now consumes a persisted Phase 2 artifact rather than rerunning optimization from scratch.

The current shipped scaffold does three things:

- re-evaluates `best_config` with `mpmath` at higher precision
- measures tangent-force residuals directly on the sphere
- builds a tangent-space finite-difference Hessian and checks whether the spectrum remains positive after the expected three rotational symmetry modes

This is intentionally narrower than rigorous certification. It is a **numerical local-minimum candidacy check** with explicit claim limits, not an interval proof.

## External Benchmark Surface

The benchmark source used by the current code is the **Cambridge Cluster Database**
table for the Thomson problem (Wales and Ulker, 2006), which lists putative global
minima energies and point groups for many `N` values.

For the bounded ranges used in this workspace, the rechecked CCD table explicitly lists
rounded display values such as `40.5964505` for `N=11`, `49.1652530` for `N=12`, and
`58.8532306` for `N=13`, alongside the corresponding point groups. This matters because
the local scripts compare against their own rounded `KNOWN_ENERGIES` constants, which are
close to but not identical with the shorter CCD display surface, and neither should be
treated as a hidden full-precision oracle.

For the current local packet, the most important benchmark consequence is practical:

- matching the CCD table means the run reproduced the accepted numerical baseline
- failing to match the table means the present search budget or method is insufficient
- going below the table by a tiny rounded margin is **not** automatically a discovery,
	because the public table is rounded and the local result is floating-point

The secondary external support surface used in this review is the TRACER Thomson
problem page, which confirms both the classical problem statement and the rapid growth
of local minima with `N`.

## One-CPU Operating Regime

The current repository is optimized for a **single-CPU, bounded-budget** workflow.

Recommended budgets:

- Phase 1 reconnaissance: `restarts=10`, `N <= 20`
- Phase 2 reconnaissance: `restarts=3..5`, `niter=8..20`, starting with `N <= 10` and now validated through `N <= 20`
- Phase 1 serious local reproduction: `restarts=50..100`, `N <= 60`
- Phase 2 claim-bearing search: only after multi-seed reruns persist the best
	configurations and reproduce the same energy class over a wider range

The present code is good enough to establish a strong reproduction baseline on one CPU,
and Phase 2 now gives OMEGA a real bounded global-search lane. It is still not a
publication-grade discovery system.

## Validation Strategy

### Primary Numerical Check

For each `N`, compare `best_energy` against the accepted benchmark energy.

Operational interpretation:

- `|delta| <= 1e-6` -> treat as reproduction
- `delta < 0` with magnitude at the level of table rounding -> still treat as reproduction
- novelty requires a materially lower energy **and** reruns that reproduce the result

### Stability Signals

The current script records:

- `energy_std`
- `distinct_minima`
- elapsed time per `N`

These do not prove correctness, but they do indicate whether the local landscape is
simple under the current budget or whether multiple numerically distinct minima are already visible.

Phase 2 adds additional stability signals:

- `top_minima`
- `accepted_minima`
- `best_config`
- `recomputed_best_energy`
- `recompute_delta`

These are still empirical rather than proof-bearing, but they materially strengthen the
reproducibility surface.

`distinct_minima` should be read as an energy-level descriptor, not as a defect counter
and not as a formally verified basin count. In the current implementation it reflects the
number of accepted minima that remain distinct after the script's energy-rounding key is
applied. When the best energy still matches the benchmark surface, this multiplicity means
that the basin-hopping lane is sampling several numerically distinct accepted minima
without overturning the accepted benchmark. The deeper `N=16..20` probe shows exactly
this pattern.

### Novelty Discipline

A lower energy must **not** be called an improvement unless all of the following hold:

1. the benchmark source has been rechecked externally
2. the improvement is larger than the apparent rounding noise of the benchmark table
3. the configuration is persisted, not just the scalar energy
4. the result survives reruns with new seeds and comparable budgets

### What This Phase Cannot Validate

- global optimality
- rigorous certification
- symmetry classification
- topology of defect structures
- publication-ready claims about new minima

### Current Phase 3 Outcome on `N=7..13`

The currently tracked bounded certification artifacts are now:

- `artifacts/phase3_certify_7_10.json`
- `artifacts/phase3_certify_11_12.json`
- `artifacts/phase3_certify_13.json`

Using the persisted Phase 2 minima from `artifacts/phase2_cpu_probe_7_10.json` and `artifacts/phase2_cpu_probe_11_13.json`, the scaffold now reports:

- `N=7`: `max_tangent_force_norm ≈ 1.34e-6`, post-symmetry minimum eigenvalue `≈ 9.20e-3`
- `N=8`: `max_tangent_force_norm ≈ 9.08e-7`, post-symmetry minimum eigenvalue `≈ 1.97e-1`
- `N=9`: `max_tangent_force_norm ≈ 9.66e-7`, post-symmetry minimum eigenvalue `≈ 1.44e-1`
- `N=10`: `max_tangent_force_norm ≈ 5.87e-6`, post-symmetry minimum eigenvalue `≈ 9.63e-2`
- `N=11`: `max_tangent_force_norm ≈ 2.84e-6`, post-symmetry minimum eigenvalue `≈ 9.07e-2`
- `N=12`: `max_tangent_force_norm ≈ 1.00e-6`, post-symmetry minimum eigenvalue `≈ 9.07e-1`
- `N=13`: `max_tangent_force_norm ≈ 4.57e-6`, post-symmetry minimum eigenvalue `≈ 3.85e-2`

All seven executed Phase 3 cases are currently classified as `numerical-local-minimum-candidate` under the scaffold's explicit finite-precision tolerances. This is stronger evidence than raw optimizer termination, but still weaker than rigorous optimality.

## Next Methodological Upgrade

The next sound improvement is **Phase 3 range extension plus selective structural analysis**:

- keep multi-seed reruns and configuration persistence mandatory on the current `N=16..20` multi-basin range
- extend the numerical certification scaffold from `N=7..12` to `N=13` before pretending the phase is stable across a wider small-`N` regime
- add symmetry or defect-summary capture only for configurations that already pass the current numerical local-minimum-candidate gate
- defer interval arithmetic until the numerical scaffold stops drifting under repeated reruns

That is the smallest academically defensible progression from the current shipped Phase 1-3 lane.
