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

## Formal Proof Search (October 2026)

These rules apply when a model writes Lean against an open statement. They
come from Tsoukalas et al., *Science*, 8 October 2026 (arXiv:2605.22763).
The evidence note is `research/OMEGA_SOTA_LANDSCAPE_UPDATE_2026_10_12.md`.

1. Freeze the statement. The search may change a marked proof region or a
   marked parameter. It may not edit the theorem type, the hypotheses, or
   the imports that give the claim its meaning. `proof_repair_loop.py`
   enforces the narrower case: text before the first `sorry` is unchanged,
   and a candidate that reintroduces `sorry` or `admit` is discarded before
   Lean is asked to score it.
2. A helper lemma closed by `sorry`, including one the model describes as a
   published theorem, is an open obligation. It is not progress. Name it in
   `proof_obligations.md`.
3. Statement fidelity is a separate gate from compilation. `formally-checked`
   requires a written note that the Lean statement matches the informal
   claim, including which notion of density, order, or finiteness was used.
   Classify a mismatch the way Formal Conjectures does (arXiv:2605.13171):
   translation (the informal sentence was clear), underspecified (the
   informal sentence omitted a choice, as with natural versus lower versus
   upper density), or source (the informal sentence itself was not the
   intended question). If the formalization was wrong, record
   `misformalized` or `amended` and do not describe the run as a solution of
   the original problem.
4. A yes/no question is stored as a frozen biconditional. The searched
   value is only `True` or `False`. Closing one part, or a named variant,
   does not close the catalog entry. Say which file and which answer.
5. For a claim about a concrete sequence or enumeration, prove a test lemma
   for the first terms before searching for the conjecture.
6. A compiler message that a subgoal is false is an outcome. Persist it.
   Do not drop it in favor of another attempt at the same proof. A negative
   answer, `answer(False)`, is a result when the biconditional is the
   question that was asked.
7. Keep the best sorry-bearing sketch when the budget ends, together with
   the compiler transcript. The open goals are the handoff to a human.

## Mass Releases (October 2026)

A catalog of many informal manuscripts is one draft per family, not a closed
domain. The October 2026 OpenAI catalog is the example: 719 manuscripts,
372 families, 300 of 719 top-line results formalized, three manuscripts
withdrawn the next day for a shared sign error. Rules:

1. Cite the manuscript version and its BibTeX. A withdrawn version stays in
   the history and drops out of the claim.
2. A Lean file counts only for the statement it contains. If the prose and
   the Lean file diverge, fidelity is `unchecked` until a person records
   which one is the claim.
3. Dependent papers fall with the paper they cite.
4. Registry status does not move because a newspaper, a blog, or the catalog
   overview says a famous problem has fallen. `navier-stokes`,
   `riemann-hypothesis`, `hodge-conjecture`, and `hadwiger-conjecture` stay
   `open`. A file whose sentence is a special case, a forced variant, a
   catalog title, or a Comparator selection is stored with that
   `claim_scope` and is not promoted to `formally-checked`. A Comparator
   challenge written by the solution's author is `challenge_party:
   same-party`. The pass matches that challenge. It does not choose the
   challenge.

The note is `research/OMEGA_OPENAI_MATH_CATALOG_2026_10_12.md`.

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
- the Lean file checks only because a helper lemma still contains `sorry`
- the formal statement was not compared with the informal claim
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
