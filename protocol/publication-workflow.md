# OMEGA Publication Workflow

## Objective

Convert a verified research artifact into a publishable note without overstating what was achieved.

## Publication Classes

### Short note

Use for:
- a new counterexample
- a verified special case
- a new computational bound

Base template:

- `templates/short-note.tex` — minimal compile-ready LaTeX note with OMEGA disclosure and reproducibility sections

### Survey memo

Use for:
- state-of-the-problem reports
- literature synthesis plus AI triage
- formalization roadmaps

Base template:

- `templates/survey-memo.tex` — compile-ready LaTeX memo with timeline table, AI amenability assessment, and structured gap analysis

### Full paper

Use for:
- a substantial new theorem
- a major computational campaign
- a broad structural reframing with evidence

## Required Sections

1. Problem statement
2. Prior work
3. Method
4. Results
5. Verification and reproducibility
6. Limitations
7. Next questions

## Claim Language Rules

Allowed:
- verified up to
- computed for all instances below
- found no counterexample below
- conjecture refined to
- proved for the subclass

Disallowed unless fully justified:
- solved
- settled
- complete proof
- definitive classification

## Repository Artifacts Per Publication

Required:
- paper source or markdown draft
- references list
- evidence manifest
- experiment summary if computation was involved
- reviewer report
- citation evidence packet when novelty or comparison claims depend on literature positioning

Recommended:
- abstract-only summary for non-specialists
- one-paragraph novelty statement
- one-paragraph limitations statement
- companion presentation pack under `presentation/` when the result will be presented outside the repository

If the note is LaTeX-first, start from `templates/short-note.tex` and then narrow claims to the actual evidence class of the run.

## Authorship Disclosure

Every paper draft should include an explicit note that AI agents participated in:
- literature synthesis
- experiment design
- computation orchestration
- drafting

Human review remains required before any external submission.

## Presentation Parity

If a draft also produces slides, a seminar deck, or other presentation outputs:

- every headline claim must map to a stored paper section or result artifact
- limitations and negative results must not disappear from the presentation layer
- the deck cannot use stronger language than the paper's evidence class supports
- citation-heavy novelty claims should reference the same `citation_evidence.md` packet as the paper draft

## Exit Criteria

A draft is ready for outside review when:
- the evidence class is explicit
- the Reviewer found no unaddressed blocking issue
- the novelty check is complete enough to be defensible
- the result can be rerun or independently checked from the stored artifacts
- any companion presentation pack stays in claim-parity with the paper draft
