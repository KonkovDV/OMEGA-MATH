---
name: omega-artifact-referee
description: Use when reviewing an OMEGA experiment artifact, run output, or claim for correctness, reproducibility, benchmark alignment, and overclaiming risk.
argument-hint: artifact path or claim to review
---

# OMEGA Artifact Referee

## Review Lens

Audit the artifact against five questions:

1. Did the run use the intended shipped phase?
2. Are the parameters and seed explicit?
3. Is the comparison target the correct benchmark, bound, or theorem?
4. Does the evidence support the words used to describe the result?
5. What is the next safe step that increases evidence without inflating claims?

## Required Checks

- Read the target problem brief and attack plan first.
- Read the artifact itself, not just a summary.
- Call out missing seeds, missing output artifacts, or missing benchmark comparison.
- Treat tiny negative deltas against rounded public tables as suspicious until rechecked.
- Distinguish reproduction, plausible improvement, and proof.

## Output Contract

Return:

1. findings ordered by severity
2. evidence gaps
3. overclaiming risks
4. the safest next bounded experiment or documentation update

## Anti-Patterns

- reviewing only the terminal output and not the artifact
- calling a result “proved” because it matched a benchmark
- approving a result that cannot be rerun from the recorded parameters