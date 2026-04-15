---
title: "Thomson Problem — Citation Evidence"
status: active
version: "1.3.1"
last_updated: "2026-04-08"
tags: [thomson-problem, citation-evidence, fact-check]
mode: evidence
---

# Thomson Problem — Citation Evidence

## Externally Rechecked in This Review

| Claim or surface | Source rechecked now | How it is used locally |
|---|---|---|
| accepted benchmark energies and point groups for many `N` | Cambridge Cluster Database Thomson table (Wales and Ulker, 2006) | supports the conservative interpretation of `KNOWN_ENERGIES` and shows that the public operator-facing benchmark surface is itself rounded |
| Thomson objective and problem complexity | TRACER Thomson problem page | supports the high-level problem framing and why local minima proliferate |
| current local optimizer choice | official SciPy `minimize(method='L-BFGS-B')` docs | supports Phase 1 as a smooth local optimization baseline |
| next global-search upgrade path | official SciPy `basinhopping` docs | supports Phase 2 direction as the smallest sound extension of the current code |

## Present in the Literature Packet but Not Re-Fetched in This Edit

These references remain important, but were not independently re-fetched during this
specific documentation pass:

- J. J. Thomson (1904) for the historical formulation
- Smale (1998) for the broader algorithmic framing via Smale's 7th problem
- Schwartz (2013) for the rigorous `N=5` case
- Cohn and Kumar (2007) and related sphere-packing / universal-optimality context
- Wales and Ulker (2006) as the primary paper-level companion to the CCD table

If this workspace is used to produce an outward-facing note or paper draft, these should
be re-fetched or BibTeX-verified at publication time rather than trusted from memory.

## Novelty Risk

The current novelty risk is **low in the sense of overclaiming, high in the sense of
false-positive excitement**.

Why:

- the current artifact set mostly reproduces accepted benchmark values to high precision
- benchmark tables are rounded, so tiny negative deltas can look more exciting than they
	are
- the workflow now persists geometry for bounded and deeper Phase 2 probes covering `N=7..20`, but the evidence is still range-limited and reconnaissance-scale rather than publication-scale
- the bounded Phase 3 scaffold now covers `N=7..12`, but it still establishes numerical local-minimum candidacy rather than rigorous optimality
- the previously suspicious `N=11` case has now been rechecked by the global-search lane and remains a rounding-sensitive reproduction

The official CCD surface makes this conservative stance mandatory: the public table lists
rounded energies such as `40.5964505`, `49.1652530`, and `58.8532306` for `N=11..13`, so
local deltas at the `1e-9` level cannot be treated as evidence of a new minimum.

Operational rule:

- `reproduce benchmark` -> safe claim
- `appears slightly lower than rounded table` -> treat as rounding-sensitive reproduction
- `materially lower and reproducible` -> only then escalate to literature collision and
	publication review

## Follow-Up Reads

Highest-value next reads for this track:

1. Wales and Ulker (2006) for the spherical-crystal and point-group context behind the CCD table
2. additional basin-hopping and global-minima literature cited from the SciPy docs
3. interval-arithmetic or computer-assisted proof references before attempting rigorous follow-on work beyond the shipped Phase 3 numerical scaffold
