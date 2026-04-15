---
title: "Thomson Problem — Proof Obligations"
status: active
version: "1.3.1"
last_updated: "2026-04-08"
tags: [thomson-problem, proof-obligations, verification]
mode: reference
---

# Thomson Problem — Proof Obligations

## Load-Bearing Claims

The current load-bearing claims are deliberately narrow.

1. `phase1_multistart.py` numerically reproduces accepted benchmark energies for the
	 bounded ranges already executed.
2. `phase2_basin_hopping.py` now reproduces accepted benchmark energies for the bounded
	 `N=7..20` range while persisting `best_config` and `top_minima`.
3. `phase3_certify.py` now upgrades `N=7..12` to a bounded numerical local-minimum-candidate check using higher-precision energy re-evaluation, tangent-force residuals, and a tangent-space finite-difference Hessian.
4. Current runs are reproductions, not new minima.
5. The present 1-CPU workflow is suitable for baseline establishment and for selecting the next algorithmic upgrade.

## Branch / Sign / Endpoint Checks

Before any stronger claim is made, check all of the following explicitly:

- sphere projection is applied after optimization steps and before final energy reporting
- any persisted `best_config` is re-evaluated so the stored geometry and reported energy agree
- any negative delta against the in-code benchmark constants is interpreted in the context
	of the shorter public CCD display surface and the benchmark's rounding precision
- `distinct_minima > 1` is treated as multiplicity evidence under the script's acceptance
	and rounding rules, not as a correctness defect and not as a formally verified basin count
- the Phase 3 force-residual tolerance is treated as a numerical calibration surface, not as a theorem threshold
- the first three near-zero Hessian modes are treated as expected rotational symmetry directions, not as instability by default
- no run is called globally optimal just because repeated local solves returned the same
	value on a small restart budget

## Mechanizable Substeps

These checks can and should be mechanized:

1. rerun the same `N` with multiple seeds
2. persist the final configuration for the best minimum and the top minima set
3. recompute the saved configuration energy in a separate pass
4. compare against the external benchmark table again
5. compute tangent-force residuals at higher precision
6. estimate the tangent-space Hessian and separate the expected rotational near-zero modes from the post-symmetry spectrum
7. detect whether symmetry or local-minimum multiplicity changed with budget
8. compare Phase 1, Phase 2, and Phase 3 on the same bounded range before escalating budgets

## Independent Patch Search

The next useful independent verification patches are:

1. extend the Phase 3 certification scaffold from `N=7..12` to `N=13`
2. benchmark-sync or table-verification helper for CCD values used in code
3. optional symmetry or defect-analysis helper now that coordinates are persisted
4. interval-arithmetic scaffolding for one or two small cases

## Deferred Risks

- no rigorous optimality proof
- no interval arithmetic
- the Hessian check is finite-difference and numerical, not rigorous
- benchmark values in code are rounded public references, not a full exact oracle
- current artifact summaries are stronger than before but still weaker than publication-grade provenance packets
