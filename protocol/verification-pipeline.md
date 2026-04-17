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
- explicit `statement_spec.md` defining the target statement and assumptions
- explicit `proof_obligations.md` covering load-bearing claims, branch/sign/endpoint checks, and deferred risks
- prover result artifact under `artifacts/prover-results/<run-id>.yaml` when the run reaches a verifier-visible outcome
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
   Ensure the result is not already known, using `literature.md`, `literature_graph.md`, and `citation_evidence.md` when novelty claims depend on related work.
5. Review challenge
   Force the Reviewer to identify the strongest objection.
6. Publication gate
   Allow publication only if the claim language matches the evidence class.

## LLM-Assisted Proof Rules

When proof work uses LLMs:

1. Treat every model-generated step as a candidate, not as an accepted lemma.
2. Convert critique into explicit obligations in `proof_obligations.md`.
3. Use fresh-session or independent referee passes as bounded diagnostics, not as endless loops.
4. Keep versioned drafts or equivalent dependency-visible notes whenever patching a load-bearing step.
5. Offload algebraic expansions, inequality-domain checks, and similar bottlenecks to formal or symbolic tools whenever available.
6. LLM-judge approval alone never upgrades a candidate argument into a proof claim.
7. Proof-result progression should follow `draft -> verifier-checked -> formally-checked` before any theorem-level language.

## Literature-Positioning Requirements

When a result claims novelty, contrast, or survey completeness, preserve:

- a local literature packet in `literature.md`
- a graph-aware view of related work in `literature_graph.md`
- a citation packet in `citation_evidence.md` with supporting and contrasting sources separated when available

External discovery services can assist retrieval, but the final claim-bearing record must stay local.

## Failure Conditions

Do not publish if any of the following hold:
- theorem language is used for numerical evidence only
- a proof depends on an unstated lemma
- a computational search cannot be reproduced
- literature search is shallow or obviously incomplete
- a novelty claim depends on literature positioning but no local citation evidence packet exists
- an LLM judge or press summary is being treated as the primary proof verifier
- the result is only interesting because the problem is famous
- a presentation artifact overstates the stored paper or results claim

## Minimal Reproducibility Record

Every completed run should preserve:
- problem id
- date
- agent roles used
- method summary
- parameters
- runtime or cost summary
- literature graph snapshot or update note
- citation evidence packet
- proof obligations path when proof-first work was involved
- prover result path when proof-first work produced a verifier outcome
- experiment ledger path when computation was involved
- result class: proof, counterexample, bound, heuristic, null result
- next-step recommendation

## Review Questions

The Reviewer should always answer:

1. What exactly was proved, if anything?
2. What was only observed experimentally?
3. What assumptions are still doing hidden work?
4. What is the strongest alternative explanation for the result?
5. Would another researcher be able to reproduce this with the stored artifacts?
6. Are supporting and contrasting citations both represented when the novelty claim depends on the literature?
7. Does the presentation layer say anything stronger than the stored paper or result evidence?
