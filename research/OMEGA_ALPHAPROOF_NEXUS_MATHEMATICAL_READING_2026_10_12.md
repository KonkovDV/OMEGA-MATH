---
title: "Mathematical reading of AlphaProof Nexus"
status: active
version: "1.0.0"
last_updated: "2026-10-12"
date: "2026-10-12"
role: evidence
audience: internal+academic
tags: [omega, erdos, lean, formal-proof, sota]
evidence_class: E1
confidence: C2
---

# Mathematical reading of AlphaProof Nexus

This note is the statement-level reading of Tsoukalas et al. for OMEGA. The
policy consequences are in PROTOCOL.md §1.9. The nine formal targets are in
`research/external/alphaproof_nexus_erdos_2026.yaml`. Press language of the
form "nine Erdős problems were solved" is not used here.

## 1. What was checked, and what was not

Primary technical text: arXiv:2605.22763v2 (8 June 2026), HTML, including
Appendices A and B.

Publication: *Science*, 8 October 2026. Avigad and Ballard's Perspective in
the same issue, DOI 10.1126/science.ael6628, cites the research article as
appearing on page 234. A secondary summary assigns the article the DOI
10.1126/science.aej2213. That DOI was not on a Science page fetched for this
note, so it is not a citation key. Emily Riehl's accompanying essay is
10.1126/science.ael8339.

Lean targets: `google-deepmind/alphaproof-nexus-results` at commit
`0647711a71183c1ea492ad60860776617ce1ea88`, directory
`APNOutputs/ErdosProblems/`, read on 12 October 2026 through the GitHub API.
The same commit prefix was used in a third-party `lake build` report
(Constellate, 10 June 2026, toolchain `leanprover/lean4:v4.27.0`). OMEGA did
not rebuild the project and does not adopt that report as its own
verification. The report also says statement faithfulness was not
independently attested.

Catalog cross-check, each with its own limit:

- Terence Tao's wiki of AI contributions, frozen 30 June 2026. The wiki's own
  disclaimer says it is not a benchmark and not a verdict.
- Bloom's problem pages for #12, #741, and #846.
- Adamczewski and Bloom, FrontierMath Erdős, arXiv:2609.25050. Their footnote
  on the nine statements is the cleanest external count.
- Firsching et al., Formal Conjectures, arXiv:2605.13171.

The deformalized proofs in Appendix B.4 were read for the shape of the
arguments. They are not copied here.

## 2. The count

The screen was every Erdős formalization present in Formal Conjectures in
early February 2026: 353 statements, not a sample chosen for interest. The
authors say this biases the set toward problems that formalize in Lean.
Search stopped at 3000 episodes. Nine files came back without `sorry`.

Those nine files are seven catalog numbers, and only some of those numbers
are closed.

| Catalog | What the Lean target decides | Catalog entry |
|---------|------------------------------|---------------|
| 12 (i), 12 (ii) | Existence of a divisibility-good set with liminf density of order `N^{-1/2}`, and failure of a uniform power-saving upper bound | Open. The reciprocal-series question is untouched. |
| 125 | The base-3 / base-4 sumset has lower density 0 | Disproved, on the corrected reading |
| 138 | `W(k+1) - W(k) → ∞` | Open. This is a variant. `W(k)^{1/k} → ∞` is still on the FrontierMath Erdős list |
| 152 | The isolation function on Sidon sets tends to infinity | Proved |
| 26 | A Tenenbaum question on thick sequences and weak Behrend translates is false | Not an Erdős question. The file name is `variants.tenenbaum` |
| 741 (i) | The positive-density split statement is false; witness `SandorA` | Does not close the problem. Upper density is a different claim, and lower density of part (i) remains open on Bloom's reading as reported by FrontierMath Erdős |
| 741 (ii) | An order-2 basis whose splits are never both syndetic; witness `cassels_set` | Part (ii) only |
| 846 | The non-trilinear plane question is false | Disproved |

FrontierMath Erdős, whose second author curates erdosproblems.com, compresses
the same fact: four problems unambiguously resolved in their sense (#152,
#846, #125, and the Tenenbaum form of #26), #741 dependent on which density
is meant, #12 and #138 still open. OMEGA adopts that compression.

Four of the nine targets are `answer(False)`. A negative theorem is a
result. It is not "the conjecture was proved."

## 3. The statements, from the files

Formal Conjectures writes a yes/no question as `answer(sorry) ↔ P`. The
agent may replace `sorry` by `True` or `False` inside an `EVOLVE-VALUE`
marker. The biconditional stays outside the marker. That is the right split:
the truth value is a searched parameter, the mathematical claim is frozen.

**#12 (i).** `IsGood` means an infinite set of positive integers with no
distinct `a, b, c` such that `a` divides `b + c` and `a` is smaller than both.
The target is existence of a good set with

```text
liminf |A ∩ [1, N]| / sqrt(N) > 0.
```

The witness is named `MyGoodSet`. The supplement builds it as a union of
blocks. Inside a block the offsets are a 3-AP-free image, so `2a = b + c`
cannot happen. Across blocks a Chinese-Remainder residue forbids the
divisibility. The spacing is chosen so the liminf is at least `1/sqrt(2)`.
Part (ii) replaces the 3-AP-free piece by a Behrend sphere in an odd base, so
the same block idea beats every exponent `1 - ε`. Neither file mentions the
series `∑_{n ∈ A} 1/n`.

**#125.** `A` is the integers whose base-3 digits lie in `{0,1}`, and `B` is
the same in base 4. The target is whether `A + B` has positive lower density.
The proof shows the lower density is 0, by a scale on which the counting
function contracts by a factor `11/12`. The first public attempt (Tao's wiki,
21 February 2026) was only a variant, because "density" had been read as
natural density. The file in the repository is the later lower-density
question (wiki: full solution, 30 March 2026).

**#138.** The target is only `W(k+1) - W(k) → ∞` for the two-color van der
Waerden function. The file defines `W` as the usual minimal `N`. It does not
mention `W(k)^{1/k}`. That stronger question is Erdős problem 138 on the
FrontierMath Erdős list and was open as of August 2026. The $500 prize is
attached to the open problem, not to this variant.

**#152.** `f(n)` is the minimum, over Sidon sets of size `n`, of the number of
sumset points with neither neighbor in the sumset. The target is `f(n) → ∞`.
The wiki records a similar argument in Erdős, Sárközy, and Sós (1994). The
Lean proof can be new as a formal text and still be close to a known idea.

**#26.** The target is the negation of: every strictly increasing thick
sequence (divergent reciprocal series) is weakly Behrend at every `ε > 0`,
meaning some translate has its set of multiples of lower density at least
`1 - ε`. The witness `seqA` satisfies, for every integer shift `k`, that the
lower density of those multiples is `< 1/2`. The counting lemma gives the
explicit bound `37/90`. Table 1 of the paper describes a different sentence,
about upper density of `A + k` below `1 - 1/4`. That sentence is not the
target theorem of `erdos_26.variants.tenenbaum.lean`. OMEGA follows the file.

**#741 (i).** The target is the negation of: whenever `A + A` has positive
density, `A` splits into two sets whose sumsets also have positive density.
The counterexample is a set named `SandorA`. There is no second target
theorem in this file for upper density. The paper's Table 1 and Bloom's page
both describe a positive theorem under upper density. Those are separate
attestations. They are not what this Lean file's target says. FrontierMath
Erdős adds that the lower-density reading of part (i) was still open.

**#741 (ii).** The target is existence of a set `A` such that `A ∪ {0}` is an
additive basis of order 2, and every partition of `A` leaves at least one of
`A₁ + A₁`, `A₂ + A₂` non-syndetic. The witness is `cassels_set`. Syndeticity
is the formal shape of "bounded gaps."

**#846.** The target is the negation of: an infinite plane set in which every
finite subset keeps a positive fraction of points with no three collinear
must be a finite union of collinear-free sets. The counterexample is the
image of a map on pairs. Bloom's page also says a counterexample follows from
Reiher, Rödl, and Sales (2024), Theorem 1.7, after a projection. Tao's wiki
marks the AI write-up as not similar to that paper. Correctness of the
disproof and priority over RRS24 are different questions. OMEGA records both
and decides neither.

## 4. What the agent comparison does and does not show

Agent A is a Ralph loop: Gemini 3.1 Pro edits the sketch, Lean answers, a
leftover `sorry` is annotated with a lesson, the next episode continues.
SafeVerify checks the finished proof against the specification and rejects
injected axioms, including `sorryAx`. If that check fails, the episode
reverts. Agent D adds a population, Elo ratings from Gemini 3.0 Flash on
7-tuples (Plackett–Luce, Gibbs, P-UCB on the top 64, exploration constant
`0.2`), and at most five AlphaProof calls and 90 edits per episode. AlphaProof
ran in tree search, not in its test-time reinforcement-learning mode, with
about 400 simulations per goal. The compiler sandbox was Lean v4.27 in Docker,
through Pantograph.

On these nine files, after they were already known to be solvable, agent A
also found proofs. Flash, Flash-Lite, and AlphaProof alone (about 64 TPU-hours
each) found none. Agent D was cheaper on the hard files, in particular #125
and the #138 variant, by about 2× to 5×, and more expensive on the easier
ones. AlphaProof's own ~$60 was omitted from the plotted B and D costs.
Variance is large; #12 (ii) and #152 are the examples the supplement names.
One generator that samples an evolutionary database, without a pool of
asynchronous agents, did worse than the basic loop. The database pays for
itself as a way to coordinate several agents, not as a memory for one.

The screen that discovered which of the 353 statements would fall was run
with agent D. The sentence "the simple loop solves the same problems" is a
statement about nine known targets, not a statement about a fresh catalog.

## 5. Misformalization is a mathematical error, not a software error

Firsching et al. classify a wrong formal statement in three layers:

1. Translation. The informal sentence is clear, and the Lean is wrong.
2. Underspecified. The informal sentence is the accepted one, but it omits a
   choice a formal text cannot omit. "Density" on #125 and #741 (i) is this
   layer: natural density, lower density, and upper density are three
   theorems.
3. Source. The informal sentence itself was not the intended question.

They report 291 repaired misformalizations in the benchmark, mostly
misrepresentation and semantic errors. AI proofs are part of the audit: a
proof of a statement nobody meant is how the statement gets caught. Test
lemmas for definitions are the other half. At the `bench-v1` snapshot, 467
test statements and 155 API statements were 23.8% of the repository.

OMEGA's repair loop now rejects a new `sorry`. It does not implement
SafeVerify, and it does not classify translation against underspecification
against source error. The prover-result field `statement_fidelity` is where
that classification has to be written by a person.

## 6. The controlled comparison that came after

Adamczewski and Bloom fixed, in advance, 68 Erdős problems still open in
August 2026, chosen so that a human solution would merit a strong journal
paper. Fifty of the Lean statements come from Formal Conjectures; the curator
picked the statement that matches the problem when several variants existed.
Each model had one attempt, $300, and 72 hours, and had to prove the
statement or its negation. Comparator checked the proof in a separate
container.

On that protocol, a pre-release GPT-6 Astra resolved 2 of 68 (#74, a
disproof, $218; #126, a proof, $247). GPT-5.6 Sol, GPT-5.5, Claude Fable 5.1,
and Claude Fable 5 resolved none. Further, non-protocol attempts by the same
pre-release model also resolved #1, #548, and #571, at costs from $363 to
$1,384, after more than $220,000 of total spend. Those extra attempts are not
a score. Erdős–Straus is problem 242 on this list. It was not among the
resolutions.

Two lessons for OMEGA:

- A formalization-biased screen overstates how often an important problem
  falls. Nexus's 9/353 and FrontierMath Erdős's 2/68 are different
  denominators. Neither is "AI now does research mathematics."
- OEIS Open, discussed in the same paper, found that a heavier agent harness
  did not beat a basic ReAct loop on those conjectures. That agrees with the
  Nexus post-hoc result and still leaves the hard-instance cost gap intact.

Riehl's essay in the same Science issue draws the line OMEGA should keep:
finding a proof is not the same as knowing which statement was worth proving,
or what the proof teaches. Avigad's lecture of 9 October 2026 says the same
thing from the other side. Litt, quoted by Adamczewski and Bloom, says that
discovering the lemma is often harder than proving it. OMEGA's registry and
triage exist for that half of the work. A prover loop does not replace them.

## 7. What this changes in the active workspaces

Erdős–Straus (`research/active/erdos-straus`) is not one of the nine files.
It is on the FrontierMath Erdős list as open in August 2026. The covering
congruence program is unchanged. The block-and-CRT construction for #12 does
not produce Egyptian-fraction identities.

No registry score moves. Section 1.5 still refuses to add these catalog
numbers as if OMEGA had closed them.

## 8. Sources

1. Tsoukalas et al., arXiv:2605.22763v2. Science, 8 October 2026.
2. Avigad and Ballard, Science 394, 166–167 (2026), DOI 10.1126/science.ael6628.
3. Riehl, DOI 10.1126/science.ael8339.
4. AAAS EurekAlert 1146436, 8 October 2026.
5. `google-deepmind/alphaproof-nexus-results` @ `0647711a7118`.
6. Tao, wiki "AI contributions to Erdős problems", frozen 30 June 2026.
7. Bloom, erdosproblems.com, pages 12, 741, 846, as fetched 12 October 2026.
8. Firsching et al., arXiv:2605.13171. Repository `google-deepmind/formal-conjectures`.
9. Adamczewski and Bloom, arXiv:2609.25050. Repository `epoch-research/LeanOpenProblems`.
10. GasStationManager, SafeVerify, cited by Tsoukalas et al. as the final axiom check.
11. Aniva et al., Pantograph, arXiv:2410.16429, the Lean interaction layer in the sandbox.
