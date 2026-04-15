---
description: Run or analyze the executable Erdős–Straus experiment lanes from the OMEGA math workspace.
agent: omega-math
argument-hint: "phase1 verify_count=50" or "phase2 max_n=5000 max_denom=100000"
model: GPT-5.4 (copilot)
---

Work inside the standalone `math` repository on `erdos-straus`.

Required sequence:

1. Read [problem brief](../../research/active/erdos-straus/input_files/data_description.md), [literature packet](../../research/active/erdos-straus/input_files/literature.md), and [attack plan](../../research/active/erdos-straus/planning/attack_plan.md).
2. Run only the currently shipped experiment lanes:
   - `phase1_covering.py`
   - `phase2_parametric.py`
3. Keep the first run bounded unless the user explicitly asks for a larger budget.
4. Write or read artifacts under `research/active/erdos-straus/artifacts/` when useful.
5. Compare outputs against the known modular coverage and decomposition status from the brief.

Return:

- parameters used
- key outputs
- whether the run extended coverage, only reproduced known behavior, or exposed a gap
- the next best bounded command