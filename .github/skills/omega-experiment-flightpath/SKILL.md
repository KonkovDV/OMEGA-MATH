---
name: omega-experiment-flightpath
description: Use when running, extending, or analyzing a bounded OMEGA flagship experiment in erdos-straus, kobon-triangles, or thomson-problem from VS Code.
argument-hint: problem id + phase + compute budget
---

# OMEGA Experiment Flightpath

## When to Use

Use this skill when the task is to:

- run a flagship experiment from `research/active/`
- extend an experiment script without pretending planned phases already exist
- analyze a fresh artifact against known values or bounds
- choose a bounded 1-CPU run instead of an open-ended compute sink

## Required Order

1. Read `README.md` and `research/active/README.md`.
2. Read the target problem's `input_files/data_description.md`, `input_files/literature.md`, and `planning/attack_plan.md`.
3. Distinguish **shipped** experiment surfaces from **planned** phases.
4. Use an explicit seed and an explicit output artifact path.
5. Compare the result against the right benchmark or bound.
6. Update the problem's `results.md` and `referee.md` if the run materially changes the local evidence.

## Repo Rules

- Treat numerical output as evidence, not proof.
- On one CPU, start bounded and only scale up after a useful baseline exists.
- Store artifacts under the problem-local `artifacts/` directory.
- Never call a result novel until the literature-collision check has been done.
- If the phase is only listed in `planning/attack_plan.md`, say so explicitly instead of implying it is already implemented.

## Good Output Contract

Return:

1. what was run or changed
2. parameterization and seed
3. comparison against known values, bounds, or benchmark tables
4. whether the result is a reproduction, a gap, or a plausible escalation candidate
5. the next best bounded run

## Anti-Patterns

- treating a planned phase as shipped code
- running huge budgets before a smoke baseline exists
- saving only terminal text and forgetting the artifact
- calling a tiny rounded benchmark delta a discovery