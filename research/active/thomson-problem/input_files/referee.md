---
title: "Thomson Problem — Referee Report"
status: active
version: "1.3.1"
last_updated: "2026-04-08"
tags: [thomson-problem, referee, review]
mode: evidence
---

# Thomson Problem — Referee Report

## Blocking Issues

1. The current artifact family now persists geometry for bounded Phase 2 probes, but it
	does not yet cover a broad enough range or depth to support strong scientific claims.
2. No rigorous certification layer exists. The new Phase 3 scaffold strengthens the `N=7..12`
	evidence materially, but any language stronger than “numerical local-minimum candidate under a bounded scaffold” would still overstate the current evidence.
3. No structural-analysis layer exists yet, so saved configurations cannot yet support
	defect-topology or symmetry claims in a disciplined way.

## Warnings

1. The formerly suspicious `N=11` case has now been checked by the shipped Phase 2
	global-search lane and remains a rounding-sensitive reproduction, not a discovery.
2. `distinct_minima > 1` for some `N` values is an informative signal that the energy
	landscape is already nontrivial at modest sizes; it also implies that restart budgets
	must be interpreted carefully. In the current implementation this should be read as
	multiple numerically distinct accepted minima, not as a formally verified basin count.
	The deeper `N=16..20` artifact confirms this multiplicity persists under larger Phase 2 budgets.
3. The newly shipped Phase 3 scaffold produces a useful signal for `N=7..12`: all six executed cases are now numerical local-minimum candidates under explicit finite-precision tolerances, with positive post-symmetry Hessian spectra and three near-zero modes treated as expected rotations.
4. Even after these upgrades, the current probe budget is still reconnaissance-scale rather than competitive-scale.

## Publication Recommendation

Current recommendation: **do not publish a novelty claim from the present artifact set**.

Safe uses of the current material:

- internal methods baseline
- reproducibility appendix for the standalone OMEGA workspace
- benchmark note that documents 1-CPU reproduction quality
- bounded artifact example showing basin-hopping, geometry persistence, and first-stage numerical certification scaffolding

Unsafe uses of the current material:

- claim of a new global minimum
- claim of rigorous optimality
- claim of structural discovery without follow-up analysis of the saved configurations

## Safe Next Step

Extend the **Phase 3 certification scaffold** from `N=7..12` to `N=13`, then add a narrow
symmetry or defect-summary helper only for candidates that already pass the current numerical gate.
That is now the smallest next move that meaningfully upgrades the scientific quality of this track without inflating claims.
