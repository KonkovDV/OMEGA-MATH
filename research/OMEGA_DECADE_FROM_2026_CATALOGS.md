---
title: "What to keep from the 2026 proof catalogs"
status: active
version: "1.0.0"
last_updated: "2026-10-12"
date: "2026-10-12"
role: evidence
audience: internal+academic
tags: [omega, sota, horizon, openai, alphaproof, formal-proof]
evidence_class: "E1 for cited runs; H for cost projections"
confidence: C2
---

# What to keep from the 2026 proof catalogs

This note extracts the mechanisms that are worth building, and the ones
that age badly, from AlphaProof Nexus (Tsoukalas et al., *Science*,
8 October 2026) and from `openai/math` at `fd4aeeb2ee4f`. It does not
adopt their theorems. No registry score moves. Counts and agent results
below are class E1, taken from those sources and from the ledgers in
`research/external/`. Sentences about costs falling, or about success
rates rising, are class H. The note does not forecast which conjectures
fall.

## The split

Two jobs are already separable, and the next decade pulls them further
apart.

**Search inside a frozen statement.** A file states a theorem and leaves
`sorry`. A model proposes a proof, the compiler answers, the loop
repeats. On the nine Erdős files, after they were already known to be
solvable, the basic loop (Gemini 3.1 Pro, with Lean feedback) also found
proofs. Gemini 3.0 Flash, Gemini 3.1 Flash-Lite, and AlphaProof used
alone found none. AlphaProof's miss is not a size result: it was run as
a tree search, about 64 TPU-hours on each target. The heavier agent was
cheaper on the hardest of those nine, notably #125 and the #138 variant.
That comparison is post-hoc. It is not a screen of unsolved statements.
FrontierMath Erdős, one attempt at $300, resolved 2 of 68 for one model
and 0 of 68 for four others. Search of this kind has a denominator:
episodes, dollars, or hours. If models and compilers get cheaper, that
denominator can fall. That sentence is class H. A higher rate of success
on a frozen, faithful statement would still not be a new account of what
the statement means, and no such higher rate is a result in hand.

**Choosing the sentence.** The OpenAI catalog shows the other job. A
Comparator pass matches a challenge written by the same party. In a
sample of 29 challenges, 27 leave `definition_names` empty, so those
definitions are not separate comparison targets. Scope notes leave the
paper's own consequences outside the formalized sentence. A zero-free
half-plane is not the critical line. A forced blowup is not unforced
regularity. Prose and Lean diverge even when both might be repairable
(arXiv:2610.08144). Three manuscripts were withdrawn for one sign error,
the commit subject did not say so, and the manuscript map dropped the
titles. Bastounis, Circelli, and Hansen argue that semantically faithful
translation into Lean is not a finite check. Nothing in the search loop
above makes this job cheap. A faster prover makes a wrong sentence fail
faster, or certifies it faster. It does not decide whether the sentence
was the problem.

OMEGA's scarce work for the next ten years is the second job. The first
job runs only after a statement is frozen, the definitions are named,
and a person has recorded `statement_fidelity` as `faithful` or
`amended`.

## Mechanisms to keep

1. **The challenge file is the interface.** A sorry-bearing statement,
   a solution module, a list of permitted axioms, and a kernel. That
   shape is right. The missing piece is who writes the challenge.
   `frozen-before-search` is the OMEGA default. `same-party` is a weaker
   provenance: it proves the solution matches a challenge from the same
   author. The runner can still promote it to `formally-checked` when
   the scope is the registry statement, fidelity is `faithful` or
   `amended`, and the party is written down. The party field is the
   warning. It is not a permanent ban, and it is not statement trust by
   itself.

2. **Name the definitions.** `hadwigerNumber`, a density, a force, a
   pole at `s = 1`. An empty `definition_names` list does not mean the
   checker ignored a symbol that appears in the theorem's type: the
   solution still has to match that type. It means the checker was not
   given a second definition to compare. The author of the challenge
   chose the type, including any local copy. Over ten years the
   definitions should live in a community library, and the challenge
   should point at those names. A local copy that is not on the
   comparison list is a warning, not a detected mismatch.

3. **Write the outside list.** Every formalization gets a scope note:
   the selected sentence, and the sentences of the paper that were not
   selected. Support checks are labeled and stay out of any success
   rate. A family (372), a manuscript (719 at HEAD, 722 at the initial
   commit), a formalization-catalog source (173), a main-result
   declaration (200), a self-reported top-line count (300), and a
   challenge file (416) are six counts. None of them is the number of
   theorems.

4. **Search variants as different problems.** Clay (A)/(B) and (C)/(D)
   were already different theorems before any agent ran. The useful
   pattern is to freeze each variant first and forbid a result on one
   from closing another. The useless pattern is to discover the
   difference after the press note.

5. **Keep every version, and cascade a retraction.** A revision is a
   new directory. The old blob stays. A sign error downgrades every
   manuscript that cites it, on the same day, in the map a reader
   actually opens. Their `history.md` did the first half. Their
   `CONTENTS.md` undid the second. The ten-year version is a
   dependency edge, not a prose section whose date disagrees with the
   notice and with the commit.

6. **Put a denominator on every attempt.** Episodes, dollars, or hours,
   including the failures. Three hours of compute, $300, or 3000
   episodes are already enough to stop a catalog from being read as a
   rate. An unpublished significance filter is not a denominator.
   OMEGA's filter is the registry statement.

7. **Hash the base.** Toolchain, mathlib commit, and every patch.
   A second kernel, such as nanoda, checks the same proof again. It
   does not check that the statement is the right one. A patched
   library is part of the claim. Upstream tags alone are not.

8. **Render exposition from the checked term, and still audit the
   term.** The Hansen mismatch exists because the prose and the Lean
   file are two arguments that share a title. Generating the exposition
   from the kernel-checked term can force the prose to follow the term.
   That is deformalization. It does not show that the term is the
   sentence a mathematician asked, and it does not answer the claim that
   translation into Lean is not a finite check. The outside list remains
   a person's job. This is a design aim. It is not a pipeline OMEGA has.

## Mechanisms to drop

- An unreleased model as a benchmark. The artifacts can be read. The
  search cannot be rerun, so it cannot be a baseline.
- A family count, a challenge count, or a self-reported formalization
  rate as a measure of theorems. The six counts in item 3 are the
  example.
- A headline that a field has been finished, as a change of tier.
- A `blob/main` URL as a citation. The initial commit said 722. HEAD
  says 719. The URL is the same shape either way.
- Copying the manuscripts into the registry. §1.5 still holds.

## How the five axes age

Scores in `registry/` stay at the April 2026 estimates until a quarterly
pass names a specific problem and a specific reason.

- Axis 4, feedback speed, rises for a problem only after a faithful
  frozen statement exists and one compile is the feedback. A screen of
  hundreds of open problems does not inherit that score from a handful
  of closed files.
- Axis 3, formalizability, rises when the definitions are in a library
  the challenge names. A catalog of prose, or a Lean file with a local
  redefinition, does not raise it.
- Axes 1 and 2 do not move because more manuscripts exist. A finite
  search space is a property of the problem.
- Tier 5 stays tier 5. The Riemann hypothesis, the Hodge conjecture,
  and unforced Navier–Stokes do not become search problems because
  search inside other statements got cheaper. A special case can be
  recorded beside them. It does not become them.

## Where this sits in the roadmap

Horizon 2 (2027–2030) already asks for proof-repair loops. The October
evidence says the basic loop is the default, and a heavier agent is an
escalation after that loop stops. The new required outcome is the
denominator and the fidelity note, not a larger swarm.

Horizon 3 (2030–2040) asks for natural language at scale to become
formal. The evidence says that translation is the part that does not
automatically follow from a better prover. The pipeline to build is
the outside list, the named definitions, and the retraction edge.
Autonomous generation of new conjectures stays behind that gate.
A conjecture without a frozen statement is a draft, however fluent
the prose.

## Triage

| Mechanism | Disposition | Score |
|---|---|---|
| Sorry-challenge plus kernel | Adopt as the proof interface | None |
| Same-party challenge as statement trust | Reject. Keep it as disclosed provenance | None |
| Named definitions in a community library | Adopt as a requirement before a score moves | None |
| Outside list, support checks excluded from rates | Adopt | None |
| Variants frozen before search | Adopt | None |
| New version is a new directory; retraction hits the map | Adopt | None |
| Denominator on failures as well as successes | Adopt | None |
| Hash of toolchain, library, and patches | Adopt | None |
| Prose generated from the checked term | Hold. It does not settle alignment | None |
| Unreleased model as a baseline | Reject | None |
| Any of the six catalog counts as a theorem count | Reject | None |
| Amenability change from a headline or from cheaper search elsewhere | Reject | None |

## What this audit removed

The draft of this note did not survive review on four points.

- The whole note was labeled E1. The cost sentences are H. The header now says so.
- AlphaProof's failure on the nine files was eligible to be read as a small-model result. The run was a tree search of about 64 TPU-hours. Flash and Flash-Lite are the small-model failures. The basic-loop successes are post-hoc.
- An empty `definition_names` list was described as if a local definition
  would pass unnoticed even when its symbol sits in the theorem's type.
  The checker matches the type. It does not compare an unnamed definition
  with an independent one.
- Rendering prose from the Lean term was described as the fix for the Hansen gap. It is deformalization. The hardness claim is about translation into Lean.

