---
name: omega-reproducibility-closure
description: Use when closing an OMEGA experiment or documentation pass by updating results, referee, citation evidence, and reproducibility surfaces with explicit evidence.
argument-hint: problem id + changed surfaces
---

# OMEGA Reproducibility Closure

## When to Use

Use this skill after:

- a new experiment run
- a claim-bearing documentation update
- a benchmark fact-check pass
- an edit to prompts, agents, or skills that changes how flagship math work is routed

## Closure Checklist

1. Update the problem-local `results.md` with what was actually run.
2. Update `referee.md` with blockers, warnings, and claim limits.
3. Update `citation_evidence.md` if benchmark or literature facts changed.
4. Update `proof_obligations.md` if the verification burden changed.
5. Confirm the referenced artifact files really exist.
6. If code changed, run the narrowest relevant Python tests.
7. If docs or control-plane files changed, run the docs closure path for the workspace.

## Repo Rules

- Do not leave a run only in terminal output if it matters to future work.
- Reproduction claims need parameters and artifacts.
- Novelty claims need artifacts, literature check, and referee review.
- Keep per-problem docs aligned with the current executable phase surface.

## Good Closure Standard

Work is closed only when a future researcher can answer:

1. what was run
2. against which benchmark or theorem
3. what the result means
4. what remains unproven or unfinished

## Anti-Patterns

- updating the artifact but not `results.md`
- updating `results.md` but not `referee.md`
- leaving citation drift unresolved after a benchmark fact-check