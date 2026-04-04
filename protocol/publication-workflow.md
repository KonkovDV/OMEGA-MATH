# OMEGA Publication Workflow

## Objective

Convert a verified research artifact into a publishable note without overstating what was achieved.

## Publication Classes

### Short note

Use for:
- a new counterexample
- a verified special case
- a new computational bound

### Survey memo

Use for:
- state-of-the-problem reports
- literature synthesis plus AI triage
- formalization roadmaps

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

Recommended:
- abstract-only summary for non-specialists
- one-paragraph novelty statement
- one-paragraph limitations statement

## Authorship Disclosure

Every paper draft should include an explicit note that AI agents participated in:
- literature synthesis
- experiment design
- computation orchestration
- drafting

Human review remains required before any external submission.

## Exit Criteria

A draft is ready for outside review when:
- the evidence class is explicit
- the Reviewer found no unaddressed blocking issue
- the novelty check is complete enough to be defensible
- the result can be rerun or independently checked from the stored artifacts
