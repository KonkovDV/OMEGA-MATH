# OMEGA Agent Teams

OMEGA uses a small fixed research team instead of a single monolithic agent.

## Core Team

### Planner

Purpose:
- choose the next problem
- assign the workflow
- enforce phase gates

Inputs:
- registry entry
- triage score
- available compute budget
- prior experiment logs

Outputs:
- research brief
- task allocation
- success criteria

### Librarian

Purpose:
- gather prior work
- extract known bounds, lemmas, failed approaches, and current status

Outputs:
- bibliography
- related-work memo
- known-results summary

### Analyst

Purpose:
- convert a raw problem into executable research hypotheses
- identify search constraints, invariants, and promising reductions

Outputs:
- approach memo
- experiment design
- failure-mode checklist

### Experimentalist

Purpose:
- run numerical or combinatorial experiments
- generate datasets, candidate constructions, or counterexamples

Outputs:
- experiment log
- reproducible scripts or pseudocode
- result summary

### Prover

Purpose:
- attempt proofs of bounded claims
- formalize lemmas
- verify candidate arguments in proof assistants or symbolic systems

Outputs:
- proof sketch
- formalization status
- dependency chain of lemmas

### Writer

Purpose:
- turn raw artifacts into a paper, note, or survey
- preserve limitations and evidence quality explicitly

Outputs:
- draft paper
- abstract
- claims table

### Reviewer

Purpose:
- attack the result before publication
- separate proof from experiment from speculation

Outputs:
- review report
- blocking issues
- publication recommendation

## Standard Workflow

1. Planner opens a problem brief.
2. Librarian returns a prior-work packet.
3. Analyst defines tractable sub-questions.
4. Experimentalist or Prover executes first, depending on tier.
5. Writer drafts the artifact.
6. Reviewer challenges it.
7. Planner either closes the cycle or schedules another pass.

## Handoff Artifacts

Each handoff must be concrete.

Required artifacts:
- brief.md or equivalent summary
- assumptions list
- open questions list
- reproducibility notes
- evidence links to exact files or outputs

## Escalation Rules

Escalate to human review when:
- a proof claim depends on a step the Prover cannot verify
- a result appears novel but literature coverage is incomplete
- computation required exceeds the configured budget
- the Writer cannot cleanly separate theorem, evidence, and conjecture
