# OMEGA Amenability Scoring Rubric v0.1

## Purpose

This rubric defines the 0–10 amenability score assigned to each open problem
in the OMEGA registry. The score estimates how feasible current AI systems
are for making progress on the problem.

## Calibration Notice

All scores in the registry are **v0.1 editorial estimates** produced by a
single rater (the OMEGA seed author) in April 2026. No inter-rater reliability
study has been conducted. Scores should be treated as informed starting points
for prioritization, not authoritative assessments.

## Five-Axis Framework

Each problem is scored on five axes (0–2 each, summed to 0–10):

### Axis 1: Searchability (0–2)

Can the problem be meaningfully explored via computational search?

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | No finite search space; purely structural or existential | Riemann hypothesis |
| 1 | Partial search possible but space is exponential or ill-defined | Goldbach conjecture (verifiable per n but unbounded) |
| 2 | Well-defined finite search space amenable to SAT/brute-force | Hadamard matrix order 668, Kobon triangles |

### Axis 2: Experimental Signal (0–2)

Does computation produce useful signal (patterns, data, counterexample candidates)?

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | Computation gives no useful feedback; purely abstract | Hodge conjecture |
| 1 | Computation can generate data, but signal-to-noise ratio is low | Collatz (lots of data, but pattern extraction hard) |
| 2 | Computation yields clear patterns, bounds, or candidates | Erdős–Straus (Egyptian fractions for specific n) |

### Axis 3: Formalizability (0–2)

Can the problem be encoded in a formal proof assistant (Lean 4, Coq)?

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | No known formalization; requires new foundations | Yang–Mills mass gap |
| 1 | Partial formalization exists or is feasible with effort | Four-color theorem (formalized), Goldbach (statement easy, proof hard) |
| 2 | Statement and key lemmas already in Mathlib or similar | Many Ramsey-type bounds, graph theory lemmas |

### Axis 4: Feedback Speed (0–2)

How quickly can a proposed approach be validated or rejected?

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | Verification requires months/years of human review | Novel proof strategies for RH |
| 1 | Verification takes hours to days (run computation, check proof) | Large-scale numerical verification |
| 2 | Verification is instant or near-instant (SAT result, counterexample) | SAT-based proofs, explicit constructions |

### Axis 5: Publication Yield (0–2)

Is incremental progress publishable?

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | Only a full resolution would be publishable | Some foundational conjectures |
| 1 | New bounds or partial results are publishable | Extending Goldbach verification range |
| 2 | Multiple publication opportunities (survey, computation, partial proof, connection) | Erdős problems with rich partial-result landscape |

## Score Interpretation

| Total Score | Tier | Meaning |
|-------------|------|---------|
| 0–2 | T5-foundational | Essentially inaccessible to current AI |
| 3–4 | T4-structural / T3-pattern | Possible pattern discovery; unlikely direct progress |
| 5–6 | T2-experimental | Meaningful computational experiments possible |
| 7–8 | T1-computational | Strong AI amenability; realistic research target |
| 9–10 | T1-computational (top) | Ideal AI target; well-defined search + fast feedback |

## Calibration Examples

### Score 8 — Erdős–Straus conjecture
- Searchability: 2 (check each n for Egyptian fraction representation)
- Experimental Signal: 2 (covering congruences yield clear patterns)
- Formalizability: 1 (statement easy; proof strategies complex)
- Feedback Speed: 2 (verification per n is instant)
- Publication Yield: 1 (new verification bound publishable, but incremental)

### Score 7 — Hadamard matrix conjecture
- Searchability: 2 (construct matrices of order 668)
- Experimental Signal: 1 (construction search; failure gives no signal)
- Formalizability: 1 (matrix algebra well-formalized)
- Feedback Speed: 2 (found = done)
- Publication Yield: 1 (construction of 668 would be notable)

### Score 5 — Collatz conjecture
- Searchability: 1 (can verify individual trajectories, but space is infinite)
- Experimental Signal: 1 (rich data, weak signal for proof)
- Formalizability: 1 (statement trivial to formalize; proofs not)
- Feedback Speed: 1 (verification fast per n, but doesn't advance proof)
- Publication Yield: 1 (new verification record publishable)

### Score 0 — P vs NP
- Searchability: 0 (no finite search)
- Experimental Signal: 0 (no computation gives structural insight)
- Formalizability: 0 (resolution may require new complexity theory)
- Feedback Speed: 0 (no incremental feedback)
- Publication Yield: 0 (only full resolution counts)

## Recalibration Schedule

- Scores should be reviewed quarterly as AI capabilities evolve
- AlphaProof-class systems may shift formalizability scores upward for entire classes
- FunSearch-class systems may shift searchability scores for combinatorial problems
- Each version bump should note which scores changed and why

## Known Limitations

1. Single-rater editorial judgment — no inter-rater reliability
2. Axes are not truly independent (searchability and feedback speed correlate)
3. Equal weighting across axes may not reflect actual research utility
4. Score does not account for problem prestige or impact
5. Does not capture whether partial results exist vs. fresh territory
