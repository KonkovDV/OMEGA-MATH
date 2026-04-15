---
description: Run or analyze the executable Thomson-problem optimization lane from the OMEGA math workspace.
agent: omega-math
argument-hint: "phase1 N=2..20 restarts=20" or "phase2 N=7..20 niter=30 restarts=4"
model: GPT-5.4 (copilot)
---

Work inside the standalone `math` repository on `thomson-problem`.

Required sequence:

1. Read [problem brief](../../research/active/thomson-problem/input_files/data_description.md), [literature packet](../../research/active/thomson-problem/input_files/literature.md), and [attack plan](../../research/active/thomson-problem/planning/attack_plan.md).
2. Treat the currently shipped experiment lanes as:
	- `phase1_multistart.py`
	- `phase2_basin_hopping.py`
3. Use explicit seeds and bounded restart / basin-hopping counts first.
4. Compare every energy value against the Cambridge known energies embedded in the scripts and brief.
5. Do not claim a new minimum unless the energy is strictly lower than the known value by a credible margin, the best configuration is persisted, and the run is reproducible.

Return:

- parameters used
- energies found and deltas vs known values
- whether the result is a reproduction, a gap, or a plausible improvement
- the next best bounded run