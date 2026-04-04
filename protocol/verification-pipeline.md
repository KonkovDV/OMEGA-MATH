# OMEGA Verification Pipeline

OMEGA treats verification as a first-class phase, not a final polish pass.

## Evidence Levels

### Level 1: computational claim

Examples:
- verified up to N
- no counterexample found below bound B
- best construction for instance size n improved from x to y

Required evidence:
- exact command or algorithm description
- hardware/runtime note when relevant
- seed and parameter settings for nondeterministic search
- raw result file or reproducible summary

### Level 2: structural claim

Examples:
- reduction from problem A to problem B
- equivalence between two formulations
- proof of a special case

Required evidence:
- explicit theorem statement
- assumptions separated from conclusions
- proof sketch with all nontrivial dependencies listed
- reviewer check for missing steps

### Level 3: proof claim

Examples:
- theorem proved
- conjecture disproved by explicit counterexample

Required evidence:
- machine-checkable or line-by-line proof artifact when possible
- independent verification pass by Reviewer
- explicit novelty check against literature

## Verification Stages

1. Artifact check
   Confirm that the expected files, logs, and outputs exist.
2. Internal consistency check
   Verify that the claim matches the produced evidence.
3. Reproducibility check
   Re-run or independently reconstruct the result on a narrow sample.
4. Literature collision check
   Ensure the result is not already known.
5. Review challenge
   Force the Reviewer to identify the strongest objection.
6. Publication gate
   Allow publication only if the claim language matches the evidence class.

## Failure Conditions

Do not publish if any of the following hold:
- theorem language is used for numerical evidence only
- a proof depends on an unstated lemma
- a computational search cannot be reproduced
- literature search is shallow or obviously incomplete
- the result is only interesting because the problem is famous

## Minimal Reproducibility Record

Every completed run should preserve:
- problem id
- date
- agent roles used
- method summary
- parameters
- runtime or cost summary
- result class: proof, counterexample, bound, heuristic, null result
- next-step recommendation

## Review Questions

The Reviewer should always answer:

1. What exactly was proved, if anything?
2. What was only observed experimentally?
3. What assumptions are still doing hidden work?
4. What is the strongest alternative explanation for the result?
5. Would another researcher be able to reproduce this with the stored artifacts?
