---
title: "OMEGA SOTA Landscape Update — October 12, 2026"
status: active
version: "1.0.0"
last_updated: "2026-10-12"
date: "2026-10-12"
role: evidence
audience: internal
tags: [omega, sota, formal-proving, lean, erdos, evidence-governance]
evidence_class: E1
confidence: C2
supersedes: "operational open-problem recommendation in PROTOCOL.md §1.4 and in OMEGA_SOTA_LANDSCAPE_UPDATE_2026_04_13.md §1.4 item 1"
---

# OMEGA SOTA Landscape Update — October 12, 2026

## Purpose

Record what Tsoukalas et al. change in OMEGA's proof-search policy. This note
does not replace the April landscape reports. Those reports remain the record
of competition-benchmark provers (MiniF2F, PutnamBench, DeepSeek-Prover-V2,
Kimina). This note is the record for open statements.

## Source

| Item | Record |
|------|--------|
| Paper | George Tsoukalas et al., "Advancing Mathematics Research with AI-Driven Formal Proof Search", *Science*, 8 October 2026 |
| Preprint read for the technical claims | arXiv:2605.22763v2 (8 June 2026), HTML |
| Publication record | AAAS EurekAlert release 1146436, 8 October 2026, Science Press Package |
| Proofs | https://github.com/google-deepmind/alphaproof-nexus-results |
| Formal statements that were attempted | Formal Conjectures (Erdős); OEIS autoformalizations described in the paper |

The Science PDF was not copied into this repository. Numbers below are taken
from the arXiv HTML and checked against the AAAS release for the headline
counts (9 of 353 Erdős problems, 44 of 492 OEIS conjectures).

A secondary write-up gives doi `10.1126/science.aej2213`. That DOI was not
on the AAAS release page fetched for this note, so it is not used as a
citation key here.

## What was solved

Read the targets before this summary. The statement-level note is
`research/OMEGA_ALPHAPROOF_NEXUS_MATHEMATICAL_READING_2026_10_12.md`. The
headline "9 Erdős problems" is nine Lean files. #12 and #138 remain open,
#26 is a Tenenbaum variant, and the published #741 (i) file is a disproof of
the positive-density reading.

The full agent (agent D: evolutionary sketch ranking plus AlphaProof as a
tool) was run on 353 Lean formalizations, with a stop at 3000 episodes. It
produced 9 files with no `sorry`. After each one, people on the team checked
that the Lean statement matched the informal problem they had chosen. That
check does not make a variant into the catalog problem.

| ID | Informal claim, compressed | Device used in the proof |
|----|----------------------------|--------------------------|
| 12 (i) | 1970. An infinite set where no element divides the sum of two larger ones, with lower density of order `1/sqrt(N)` along a subsequence | Blocks, Chinese Remainder Theorem, 3-AP-free sets |
| 12 (ii) | 1970. The same divisibility constraint, with `|A ∩ [1,N]| ≫ N^(1-ε)` | Same block construction |
| 125 | 1996. Base-3 and base-4 sum-free digit sets; the sumset has lower density zero | Inductive thinning from `3^m ≈ 4^k` |
| 138* | 1981. `W(k+1) - W(k) → ∞` for van der Waerden numbers | Greedy coloring |
| 152 | 1994. Large Sidon sets have many isolated points in `A+A` | Counting argument |
| 741 (i) | 1994. If `A+A` has upper density, `A` splits into two sets whose sumsets also have positive upper density | Case split on upper density |
| 741 (ii) | 1994. A basis of order 2 that keeps bounded gaps after every split | Explicit fast-growing sequence |
| 846 | 1992. An infinite set whose finite subsets are not finite unions of collinear sets, but still contain many non-collinear points | Vertex labels on `K_∞`, quadratic edge map |
| 26* | 1995. A set whose every translate `A+k` has upper density `< 1 - 1/4`. Not posed by Erdős; a broader variant | Blocks, primes, CRT |

The asterisk marks a variant. Problem 26 was not posed by Erdős.

The same agent proved 44 of 492 OEIS conjectures that a manual review judged
correctly formalized and previously unproved. Before the conjecture, the agent
had to prove test lemmas for the first terms of the sequence.

Other research uses reported in the paper, each still tied to a human
formalization of the statement:

- an exact `O(1/t)` rate for anchored gradient descent-ascent, with the step
  schedule left as a value the agent could change
- one bipartite variant of graph reconstruction, plus a leaf-count conjecture
  from Graffiti (1996)
- log-concavity of pure O-sequences in codimension 3 and type 2, open about
  fifteen years
- Green's problem 57: the agent proved a real-valued variant, then proved that
  a floating-point candidate on `Z/3Z` is a counterexample to the complex-valued
  statement
- several quantum-optics existence claims for monochromatic graphs with
  `N = d ∈ {4, 6, 10}`

## The result that changes the agent policy

The full agent was chosen because, when the screen was planned, simple loops
were weak on competition benchmarks. After the nine Lean files existed, the
authors compared four agents on those nine targets only:

| Agent | What it is |
|-------|------------|
| A | Independent "Ralph" loops. Each episode is a Gemini 3.1 Pro conversation that edits the sketch. Lean checks the sketch after each turn. A leftover `sorry` is followed by a written lesson, and that sketch is the next episode's input. |
| B | A, plus AlphaProof as a tool that can return a proof, a disproof, or a failure |
| C | A, plus a shared population of sketches ranked by Elo from cheaper rater models |
| D | B and C together |

Agent A closed all nine targets. It cost more than D on the harder instances. On #125
and the #138 difference variant, D was about 2× to 5× cheaper. On the other plotted problems, D was
about half as cost-efficient. AlphaProof's own cost, about 27.5 TPU-hours and
$60 per problem on v6e, was not included in the B and D points; adding that
$60 did not change the ranking beyond the reported error. Flash and Flash-Lite
variants of A, and AlphaProof alone in tree search, solved none of the nine.

This comparison is post-hoc. It does not say that A would have found the same
nine if it had been the only agent pointed at all 353 statements. The screen
that found which statements were tractable was itself a large cost, paid with
agent D.

## Failure modes OMEGA now treats as gates

1. **Sorry laundering.** The strongest failed sketches often pushed the real
   difficulty into one helper lemma whose statement was the goal again, closed
   by `sorry`. Telling the model not to do this did not stop it.
2. **Invented citations.** Other sketches depended on `sorry` lemmas the model
   described as published theorems. Inspection showed those lemmas were not
   in the literature.
3. **Misformalization.** On #125 and #741 (i) the agent proved a reading
   ("natural density") that was not the intended reading ("lower density",
   "upper density"). The statements were corrected. The corrected statements
   were still proved. A compiling file is not evidence about the informal
   problem until a person has signed the reading.
4. **Library boundary.** Successes clustered where mathlib is mature and the
   goal splits into known steps: combinatorics, convex optimization, number
   theory. Most of the 353 statements stayed open. Problems that need a new
   theory stayed open.

A failed sketch was still useful to the mathematicians when the closed steps
were formal and the open goals were explicit. They read the open goals. They
did not re-check the closed steps.

## What OMEGA changes because of this

1. The default `prove` pass on an open statement is one capable model plus
   Lean feedback. PROTOCOL.md §1.9. The April recommendation "large model
   decomposes, small model proves" stays in force for competition-style
   benchmarks and for an already-isolated obligation. It is no longer the
   first pass on a fresh open statement. Small models solved none of the nine.
2. Evolutionary search and an external prover are an escalation, used after
   the basic loop stops, and only on a statement whose fidelity note exists.
   They are justified on hard instances by the cost gap on #125 and #138, not
   by a claim that the basic loop cannot succeed.
3. `scripts/proof_repair_loop.py` rejects a candidate that contains `sorry`,
   `admit`, or `sorryAx`, that opens a new declaration, or that changes the
   text before the first `sorry`. The count of those rejections is returned
   as `unsafe_candidates_rejected`.
4. `omega-runner proof-result` writes `statement_fidelity`, `claim_scope`,
   `agent_profile`, and `unsafe_candidates_rejected`. Status
   `formally-checked` or `verified` is refused while fidelity is
   `unchecked` or `misformalized`, and while `claim_scope` is anything
   other than `registry-statement`.
5. The amenability rubric's October 2026 note tells a rater how to read axes
   3 and 4. No registry score was changed in this pass. §1.5 still forbids
   adding these nine Erdős items to the registry before three local T1
   workspaces finish the lifecycle.

## What this note does not claim

- OMEGA did not reproduce the nine proofs.
- OMEGA does not have AlphaProof, Gemini 3.1 Pro, or a 3000-episode budget
  wired in.
- A local 7B prover remains a workstation tool for a short obligation. It is
  not, on this evidence, a solver of open Erdős statements.
- Informal proofs from other 2026 systems still need a human or a formal
  checker. The paper's own discussion says formal verification is the filter
  for which arguments deserve that human reading.
- The OpenAI manuscript catalog of 6 October 2026 is a separate surface.
  Its reading is `research/OMEGA_OPENAI_MATH_CATALOG_2026_10_12.md`. A family
  in that catalog is not a closed registry entry.
