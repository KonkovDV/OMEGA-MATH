---
description: Run or analyze the executable Kobon triangles search lane from the OMEGA math workspace.
agent: omega-math
argument-hint: "phase1 k=3..10 restarts=10 iterations=500" or "analyze latest artifact"
model: GPT-5.4 (copilot)
---

Work inside the standalone `math` repository on `kobon-triangles`.

Required sequence:

1. Read [problem brief](../../research/active/kobon-triangles/input_files/data_description.md), [literature packet](../../research/active/kobon-triangles/input_files/literature.md), and [attack plan](../../research/active/kobon-triangles/planning/attack_plan.md).
2. Treat Phase 1 (`phase1_pseudoline_enum.py`) as the only shipped experiment lane today.
3. Use explicit seeds and bounded search parameters for the first pass.
4. Compare found triangle counts against `KNOWN_OPTIMAL`, Tamura bound, and improved bound.
5. If asked about SAT or straightening, state that those are planned later phases unless their scripts have been implemented in the workspace.

Return:

- parameters used
- found counts vs known values
- whether the run only reproduced, matched, or challenged known best values
- the next best bounded experiment