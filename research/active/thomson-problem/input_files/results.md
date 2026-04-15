---
title: "Thomson Problem — Results"
status: active
version: "1.3.1"
last_updated: "2026-04-08"
tags: [thomson-problem, results, reproduction, benchmark]
mode: evidence
---

# Thomson Problem — Results

## Executed Steps

The currently documented executable work now includes:

- **Phase 1 multi-start optimization**
- **Phase 2 bounded basin-hopping global search**
- **Phase 3 bounded numerical certification scaffold**

Executed artifact families:

- `artifacts/phase1_smoke.json` -> smoke verification for `N=2..4`, `restarts=3`, `seed=1729`
- `artifacts/phase1_cpu_probe_7_12.json` -> bounded CPU probe for `N=7..12`, `restarts=10`, `seed=42`
- `artifacts/phase1_cpu_probe_13_20.json` -> bounded CPU probe for `N=13..20`, `restarts=10`, `seed=42`
- `artifacts/phase2_cpu_probe_7_10.json` -> bounded Phase 2 probe for `N=7..10`, `restarts=3`, `niter=8`, `local_maxiter=150`, `top_k=3`, `seed=1729`
- `artifacts/phase2_cpu_probe_11_13.json` -> bounded Phase 2 probe for `N=11..13`, `restarts=3`, `niter=8`, `local_maxiter=150`, `top_k=3`, `seed=1729`
- `artifacts/phase2_cpu_probe_14_20.json` -> bounded Phase 2 probe for `N=14..20`, `restarts=3`, `niter=8`, `local_maxiter=150`, `top_k=3`, `seed=1729`
- `artifacts/phase2_cpu_probe_16_20_deeper.json` -> deeper Phase 2 probe for `N=16..20`, `restarts=5`, `niter=20`, `local_maxiter=250`, `top_k=5`, `seed=2718`
- `artifacts/phase2_cpu_probe_19_20_deeper.json` -> focused deeper Phase 2 probe for `N=19..20`, `restarts=7`, `niter=30`, `local_maxiter=300`, `top_k=7`, `seed=31415`
- `artifacts/phase3_certify_7_10.json` -> bounded Phase 3 certification scaffold for `N=7..10`, `mp.dps=80`, tangent-force residuals plus tangent-space finite-difference Hessian
- `artifacts/phase3_certify_11_12.json` -> bounded Phase 3 certification scaffold for `N=11..12`, `mp.dps=80`, tangent-force residuals plus tangent-space finite-difference Hessian

## Findings

### 1. Phase 1 remains a strong reproduction baseline on 1 CPU

Across all executed artifacts, the script reproduces accepted Thomson benchmark
energies to within floating-point noise.

| Run family | Range | Budget | Result |
|---|---:|---:|---|
| smoke | `N=2..4` | 3 restarts | exact small-case reproduction within `~4e-10` |
| CPU probe A | `N=7..12` | 10 restarts | all cases reproduce the accepted baseline |
| CPU probe B | `N=13..20` | 10 restarts | all cases reproduce the accepted baseline |

### 2. Phase 2 is now shipped and reproduces the benchmark across bounded coverage from `N=7..20`

The shipped bounded Phase 2 artifacts now cover `N=7..20` and classify every run as
`reproduction`.

| Run family | Range | Budget | Result |
|---|---:|---:|---|
| Phase 2 CPU probe A | `N=7..10` | 3 restarts, 8 basin steps | all cases reproduce the accepted baseline |
| Phase 2 CPU probe B | `N=11..13` | 3 restarts, 8 basin steps | all cases reproduce the accepted baseline |
| Phase 2 CPU probe C | `N=14..20` | 3 restarts, 8 basin steps | all cases reproduce the accepted baseline |
| Phase 2 deeper probe | `N=16..20` | 5 restarts, 20 basin steps | all cases reproduce the accepted baseline |

Additional evidence carried by the Phase 2 artifact:

- every run stores `best_config`
- every run stores `top_minima`
- every run recomputes the saved best configuration energy, with `recompute_delta` at numerical zero
- the bounded probe already sees multiple distinct minima: `4` for `N=7`, `2` for `N=8`, `2` for `N=9`, `2` for `N=10`
- the second bounded probe extends the same geometry-level evidence to the previously suspicious `N=11` case and still records `reproduction`
- the third bounded probe extends the same evidence lane through `N=20`
- the deeper probe confirms that the multi-basin behavior is stable under larger Phase 2 budgets: `4` distinct minima for `N=16`, `3` for `N=17`, `1` for `N=18`, `5` for `N=19`, and `3` for `N=20`

This materially improves OMEGA's evidence quality compared with the earlier scalar-only Phase 1 summaries.

### 3. There is still no credible new minimum in the current artifact set

The most superficially suspicious case remains `N=11`, where both shipped phases produce a tiny negative delta against the in-code `KNOWN_ENERGIES` constant:

- Phase 1 local best: `40.59645050821393`
- Phase 2 bounded best: `40.596450508214375`
- in-code benchmark constant: `40.596450510`
- artifact delta scale versus that constant: about `-1.79e-9`
- public CCD display value: `40.5964505`

This must **not** be interpreted as a scientific improvement. The benchmark values in
the script are rounded benchmark constants, while the CCD table shown to operators is an
even shorter rounded display surface. On either surface, `N=11` is still a reproduction,
now checked by both the local and global-search lanes.

The expanded Phase 2 artifacts do not challenge any accepted benchmark value. The delta
list below is computed against the in-code `KNOWN_ENERGIES` constants used by the scripts;
the shorter public CCD display values only strengthen the conservative interpretation that
these are reproductions rather than escalation candidates.

- `N=7`: `Δ ≈ +2.23e-10`
- `N=8`: `Δ ≈ +2.33e-10`
- `N=9`: `Δ ≈ +2.72e-10`
- `N=10`: `Δ ≈ +1.69e-10`
- `N=11`: `Δ ≈ -1.79e-9`
- `N=12`: `Δ ≈ -3.70e-10`
- `N=13`: `Δ ≈ -2.87e-10`
- `N=14`: `Δ ≈ -3.57e-10`
- `N=15`: `Δ ≈ +3.15e-10`
- `N=16`: `Δ ≈ +5.50e-10`
- `N=17`: `Δ ≈ -3.65e-10`
- `N=18`: `Δ ≈ +5.07e-10`
- `N=19`: `Δ ≈ -2.90e-10`
- `N=20`: `Δ ≈ -2.21e-10`

All fourteen are clean reproductions, not escalation candidates.

### 4. The landscape already shows nontrivial multiplicity in accepted minima for some `N`

Two cases stand out even at only 10 restarts:

- `N=16` -> `distinct_minima = 2`, `energy_std ≈ 3.48e-3`
- `N=19` -> `distinct_minima = 3`, `energy_std ≈ 1.25e-3`

Interpretation: the current multi-start + local descent setup is already encountering
multiple numerically distinct accepted minima. This is useful evidence that Phase 2 should focus on better
global exploration rather than pretending that more documentation alone will solve the
search problem.

The Phase 2 probes reinforce the same conclusion on a wider range by exposing multiple
distinct accepted minima even while reproducing the accepted best energy. On the deeper
`N=16..20` probe, the multiplicity persists rather than disappearing under larger budgets:
`4` for `N=16`, `3` for `N=17`, `1` for `N=18`, `8` for `N=19`, and `2` for `N=20`.
In this context, `distinct_minima` should be read as an energy-level multiplicity signal
under the script's acceptance and rounding rules, not as a formally verified basin count.

The focused deeper `N=19..20` follow-up sharpens the same conclusion rather than overturning it:

- `N=19` increases to `13` distinct accepted minima under the larger `restarts=7`, `niter=30` budget
- `N=20` remains comparatively stable at `2` distinct accepted minima under the same focused probe

This is good evidence that `N=19`, not `N=20`, is currently the more rugged bounded target for further global-search work.

### 5. Runtime is excellent for bounded local and global sweeps

Observed elapsed times remain small on 1 CPU:

- `N=7..12`: about `0.07s` to `0.16s` per value
- `N=13..20`: about `0.34s` to `1.03s` per value
- Phase 2 `N=7..10`: about `0.15s` to `0.23s` per value on the bounded probe
- Phase 2 `N=14..20`: about `0.59s` to `1.68s` per value on the bounded probe
- Phase 2 `N=16..20` deeper: about `2.1s` to `5.6s` per value on the deeper probe

This makes Thomson the strongest current flagship track for rapid iteration in the
standalone OMEGA workspace.

### 6. Phase 3 now upgrades `N=7..13` from plain reproduction to numerical local-minimum candidacy checks

The current bounded Phase 3 artifacts consume persisted Phase 2 minima instead of rerunning the search.

Key outcomes from `artifacts/phase3_certify_7_10.json`, `artifacts/phase3_certify_11_12.json`, and `artifacts/phase3_certify_13.json`:

- all seven executed cases (`N=7..13`) keep their benchmark-level reproduction energies under `mpmath` re-evaluation
- all seven show tangent-force residuals in the `1e-6` to `1e-5` range, which is consistent with double-precision upstream optimization followed by higher-precision rechecking
- all seven show zero negative eigenvalues after excluding the expected three rotational symmetry modes
- all seven are therefore classified as `numerical-local-minimum-candidate`

Additional Phase 3 detail for the extended range:

- `N=11`: `delta_to_known ≈ -1.79e-9`, `max_tangent_force_norm ≈ 2.84e-6`, `post_symmetry_min_eigenvalue ≈ 9.07e-2`
- `N=12`: `delta_to_known ≈ -3.70e-10`, `max_tangent_force_norm ≈ 1.00e-6`, `post_symmetry_min_eigenvalue ≈ 9.07e-1`
- `N=13`: `delta_to_known ≈ -2.87e-10`, `max_tangent_force_norm ≈ 4.57e-6`, `post_symmetry_min_eigenvalue ≈ 3.85e-2`

This still does **not** prove optimality, but it is a material step beyond “the optimizer converged and the energy looks right.”

### 7. Thomson now has a live provenance surface, not just loose artifacts

The `phase3_certify_11_12` extension is also the first Thomson run recorded through the local OMEGA workflow substrate:

- `experiments/ledger.yaml` contains the completed tracked run `thomson-problem-20260408-001`
- `artifacts/evidence-bundle.yaml` now resolves the tracked dataset artifact plus core workspace documents
- `control/workflow-state.yaml` and `research/active/experiment-index.yaml` now reflect Thomson as an active experiment-first workspace in the `results` stage

This is a meaningful quality improvement because operator-facing claims and on-disk provenance now move together.

## Negative Results

- No rigorous interval certification has been attempted.
- No new low-energy configuration has been established.
- No symmetry, defect, or structure summary has yet been emitted from the saved configurations.

## Limitations

1. The benchmark table values stored in code are rounded.
2. Phase 1 and Phase 2 are reproduction surfaces, and the current Phase 3 lane is still a numerical scaffold rather than a proof surface.
3. Restart counts and basin-hopping budgets here are reconnaissance budgets, not exhaustive search budgets.
4. Geometry is now persisted for bounded and deeper Phase 2 probes through `N=20`, and the Phase 3 scaffold now covers `N=7..12`, but the total range and supporting analyses are still too small for publication-grade discovery claims.

## Bottom Line

The present Thomson workflow is already good enough to serve as OMEGA's most credible
1-CPU flagship reproduction track. With the shipped Phase 2 probes, it now has a real
global-search lane plus geometry-level artifact capture across `N=7..20`, including a deeper
multi-basin check on `N=16..20` and a focused deeper probe on `N=19..20`. With the shipped
Phase 3 scaffold, it also has a bounded numerical local-minimum-candidate surface for
`N=7..12` plus a tracked provenance bundle for the latest certification run. It is **still not** good enough to support claims of new minima, rigorous optimality,
or publication-ready structural insight.
