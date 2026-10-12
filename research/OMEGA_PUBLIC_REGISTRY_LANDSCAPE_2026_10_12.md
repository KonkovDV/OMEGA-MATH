---
title: "What to take from the public math registries"
status: active
version: "1.0.0"
last_updated: "2026-10-12"
date: "2026-10-12"
role: evidence
audience: internal+academic
tags: [omega, sota, palomar, qed, formal-conjectures, mathdb]
evidence_class: "E1 for pages fetched on 2026-10-12; E2 for second-hand descriptions"
confidence: C2
---

# What to take from the public math registries

Fetched on 12 October 2026: Palomar, qed.bot, the Formal Conjectures
stats pages, MathDB, and whataifound.org. erdosproblems.com is named
because qed.bot's method page cites it. VibeMathed and ProofAtlas appear
only as that comparison page describes them. Open Problem Garden and
Cairn Commons were not re-read, so this note takes no rule from them.
This note extracts operating
rules. It does not adopt their theorems. No registry score moves. No
problem is added to `registry/`. §1.5 still holds. The runner's
`formally-checked` gate is unchanged.

The locked snapshots are `research/external/public_registry_landscape_2026.yaml`.

## The counts are different objects

| Snapshot | What the page said | Class |
|---|---|---|
| Formal Conjectures, arXiv:2605.13171v1 | 2615 statements, 1029 open, 836 solved and kept for autoformalization | E1 |
| Formal Conjectures stats page, official | 6329 indexed statements | E1 |
| firsching.ch stats page, same date | 5172 indexed statements | E1 |
| qed.bot source list, Formal Conjectures records in its graph | 1417 records | E1 |
| qed.bot homepage | 1858 statements, 19 collections, 77 record targets, 650 AI claims, 37 machine-checked | E1 |
| qed.bot Erdős dataset | 1221 records. The erdosproblems.com proof-claim feed was unavailable | E1 |
| MathDB about page | 87,328 catalogued, 225 with a recorded AI attempt, 195 claimed solved with AI | E2, their self-report |
| whataifound.org on MathDB | 66,736 | E2, a second site, not reconciled with MathDB's own page |

The official stats page and firsching.ch were both live on this date and
disagreed: 6329 and 5172. Neither is corrected into the other. The paper's
2615 is the count in arXiv:2605.13171v1. qed.bot's 1417 is how many
Formal Conjectures records its own graph held, not a census of the
repository. Subject rows on either stats page are multi-tagged, so they
are not added into the index total. None of these numbers is a theorem
count, and none of them is the size of `registry/`.

## What each project actually keeps

**Formal Conjectures** (`google-deepmind/formal-conjectures`) is a
library of Lean statements. The paper presents open conjectures as a
bench on the ground that a solution is not already in the training
corpus. That is the project's claim about its own design. Solved
problems stay in the library, marked solved, for autoformalization, and
they sit outside that claim. A definition
that mathlib does not yet have can live beside the statement, so a
conjecture is not blocked on a library release. The paper's own audit
loop is that a proof or a disproof can expose a bad formalization.
OMEGA already uses that classification in the verification pipeline:
translation, underspecified, source.

**Palomar** (palomar-registry.org) is a registry of pinned Lean
snapshots. Comparator compiles the statement and the proof in separate
sandboxes and checks that the declarations the statement depends on
agree. The exported proof is replayed by Lean's kernel and by the
independent kernels named on the entry. Palomar requires nanoda.
`leanchecker` replays into a fresh environment and still uses Lean's
kernel, so it is not the independent check. A language model looks for
a blocking mismatch between the formal statement and the informal
account, and for a minimum of research interest. Palomar says that
filter does not accept, endorse, or peer-review a result, and that it
does not certify novelty, importance, or alignment. Scores behind the
filter are withheld: the same commit scored 5 and then 4 on one axis
with the same registerability. An entry is not re-run when Lean or
mathlib moves. A later commit is a new version of the same identifier;
the old version URL stays. Moderators can retract one exact version.
The history is not erased. The statement file may import Lean core,
mathlib, and Tau Ceti. A Tau Ceti import is recorded as a qualified
statement dependency. Proof dependencies may be wider. mathlib's build
cache is a mutable store, so a reproduction that needs identical
artifacts builds mathlib from source.

**qed.bot** is a graph assembled by a job from public sources. Nothing
on the method page is entered by hand. A source that cannot be read is
shown as unavailable, and the affected records are left as they were.
On this date, 12 of 13 sources were read, and the erdosproblems.com
proof-claim feed was the one left unread.

**MathDB** (mathdb.com) is a prose catalog from a Caltech collaboration.
Its about page states a verdict, the evidence, and whether anyone has
checked. It does not run a kernel. The same page advertises 2026 claims,
including a bound touching the Riemann hypothesis and a Jacobian
counterexample. OMEGA does not adopt those claims. A wrong statement of
a conjecture is worse than a missing entry, which is why an adopted
sentence still needs a fidelity note.

**Named from a page this pass did fetch.** erdosproblems.com is the
collection qed.bot uses for identities such as `erdos:707`. The
proof-claim feed on that site was unavailable to qed.bot at the refresh
recorded on its method page, so those claims are absent there rather
than filled in. VibeMathed, as whataifound.org describes it, is a
community list. Its verification label is that site's label.
ProofAtlas, on the same comparison page, can mark a Lean build checked
while the record is still not accepted, and a retained audit can be a
summary rather than the transcript. OMEGA has not read ProofAtlas's own
contract. That sentence stays E2.

## Rules adopted

1. **Identity is source-anchored.** The canonical id names the collection
   that owns the statement (`erdos:707`, `kourovka:12.34`). A Lean path
   or a problem page is an alias. Two records merge only when a locator
   says they are the same. They do not merge because the titles look
   alike. Two faithful formalizations of one problem can differ, and two
   different problems can read almost identically.

2. **A proposition and a record are different nodes.** A statement is
   open or settled. A target is a quantity: a direction, a history of
   values, and a standing (`below`, `matched`, `record`, `superseded`,
   `unstated`). A better packing or a moved constant is not stored as
   "the conjecture is solved." If a source gives the standing and not
   the value, the value stays empty.

3. **Edges come from a source.** `derives-from`, `part-of`,
   `references`, and `variant-of` are recorded when a citation or a
   locator supplies them. Nothing is inferred from similarity.

4. **Autonomy, evidence, and fidelity are independent.** qed.bot's
   scales, copied here as an external vocabulary:

   | Grade | Meaning |
   |---|---|
   | A3 / A2 / A1 / A0 / A? | Autonomous, directed, collaborative, human, or not established from the record |
   | V3 | A proof rebuilt at a pinned commit by someone other than the authors, and resting on the standard axioms; or an object measured against the problem's own constraints |
   | V2 | An artifact is published, and nobody independent of the authors has rebuilt it |
   | V1 / V0 | Informal public write-up, or a claim with no public artifact |
   | F3 | The proof was checked for exact statement identity against a statement written independently of it |
   | F2 | The authors declared the correspondence, or a statement corpus cites the proof against its own statement |
   | F1 / F0 | A formal artifact exists and nothing records the correspondence, or no formal statement is attached |
   | D3–D1 / withheld | The announcement identifies every result and attaches a checkable artifact, or it identifies them in prose, or it only names them, or it claims results it does not identify |

   The grades describe the evidence attached to a claim. They are not a
   verdict that the mathematics is correct. A result that has not been
   identified is counted under disclosure. It is not given an autonomy,
   evidence, or fidelity grade.

5. **Map the grades onto OMEGA without collapsing them.**

   | External grade | OMEGA reading |
   |---|---|
   | F3 | The comparison target was a statement from a separate corpus. `frozen-before-search` alone is not F3: a statement frozen by the same party is not an independent corpus |
   | F2, authors declared the alignment | A human fidelity note. `same-party` stays disclosed |
   | F1 | A compiling file with `statement_fidelity: unchecked` |
   | F0 | A draft manuscript |
   | V3 | An independent rebuild. A local run by the same party does not receive this label |
   | V2 | The proof artifact exists |
   | Palomar's language-model filter | A published review that found no blocking problem. It is not `statement_fidelity: faithful` |

   `formally-checked` with `challenge_party: same-party` is at most V2
   plus a human fidelity note. It is not V3 and it is not F3. The runner
   may still promote that case when the scope is the registry statement
   and the fidelity note is `faithful` or `amended`. This note does not
   add an independent-rebuild requirement to that gate.

6. **A rebuild has verdicts, and a glance is not a rebuild.** qed.bot
   passes a file when it elaborates at the pinned commit and `#print axioms`
   shows only `propext`, `Classical.choice`, and `Quot.sound`. `sorryAx`
   means an unproved goal survived. Any other axiom is named.
   The method page names `Lean.ofReduceBool` and `Lean.trustCompiler` as
   the typical signature of `native_decide`. Those are extra axioms, not
   a silent pass. A
   file that imports its own project is a fragment, not a standalone
   proof. A dependency that does not resolve, and a file that does not
   elaborate, are separate failures. Reading the source for `sorry`,
   `admit`, and `native_decide` is a static inspection. It does not earn
   V3. A missing file is recorded as missing.

7. **An object is checked by measuring it.** The checker does not read
   the claim first. A disagreement is published as a refutation. This
   is the generator-verifier class that FrontierMath distinguishes from
   a general statement (arXiv:2609.25050): a graph, a cap set, or a
   tensor decomposition can be cheap to check and still not be a proof
   of a conjecture. False positives and false negatives exist inside
   that class too.

8. **`sorry` in a statement library is normal.** Formal Conjectures is
   a repository of statements. Formal status is read from the research
   annotations (`open`, `solved`, and the other category columns on the
   stats page), not from a count of `sorry`. Goal counts are context.

9. **A container speaks for none of its contents.** A `formalization.yaml`,
   a repository, or a directory that joins several results is not an
   identity. Archive, review, and history copies of that file are set
   aside. The newest declaration stands. A registration attached only
   because a project mentions a problem number is shown and is not
   counted: a file titled after a problem may prove only a part of it.
   A move of a directory is recorded with the commit that documents it.

10. **A supporting success is not a primary success.** Formalization,
    literature search, rewriting, and computation have their own
    outcomes. "The formalization succeeded" and "the problem fell" are
    counted in different columns and are never added.

11. **Pin the base, and do not let the entry drift.** Toolchain, library
    commit, patches, axiom policy, and the kernel names are part of the
    claim. An old snapshot is not quietly re-verified on a newer
    mathlib. A new version is a new pinned submission. The previous
    version stays resolvable.

12. **A feed that failed stays failed.** Do not fill an unread
    proof-claim list from memory or from a second site's paraphrase.

## Triage

| Mechanism | Disposition | Score |
|---|---|---|
| Source-anchored id and aliases | Adopt | None |
| Separate proposition and record nodes | Adopt | None |
| Independent autonomy, evidence, fidelity | Adopt as an external vocabulary | None |
| V3 only after an independent rebuild | Adopt as a label. Do not add it to the runner gate | None |
| Named axiom verdicts, including `native_decide` | Adopt when reading an external Lean file | None |
| Object check measured before it is compared | Adopt for constructions | None |
| Research annotation, not a `sorry` count | Adopt | None |
| Container, newest declaration, move commit | Adopt | None |
| Separate supporting and primary outcomes | Adopt | None |
| Pinned snapshot, old version kept | Adopt | None |
| Unread source left unread | Adopt | None |
| Language-model statement filter | Hold. It is a review to read, not a fidelity grade | None |
| Palomar research-interest floor | Reject as an importance score | None |
| Another registry's title as a closed OMEGA entry | Reject | None |
| Any snapshot count as a theorem count | Reject | None |
| MathDB's advertised 2026 claims | Reject | None |
| VibeMathed significance, or a Palomar registration, as an amenability change | Reject | None |

## What this pass refused

- The runner still promotes `same-party` when the scope is the registry
  statement and a person has recorded `faithful` or `amended`. Calling
  that promotion an independent check would be the false step.
- Palomar's decision to register with no human editorial step is their
  policy. OMEGA's fidelity gate stays a person's note.
- ProofAtlas's acceptance rule is used only as whataifound.org stated
  it. It is not copied into the runner.
- The Riemann hypothesis, the Hodge conjecture, unforced Navier–Stokes,
  and the Hadwiger conjecture stay `open`.

## What the audit removed

The first draft of this note invented an order among counts that the
pages do not supply.

- firsching.ch's 5172 was described as an earlier reading of the
  official stats page. Both pages were live on 12 October 2026. One
  said 6329. The other said 5172.
- qed.bot's 1417 was eligible to be read as an earlier census of Formal
  Conjectures. It is the number of records in qed.bot's graph.
- whataifound.org's 66,736 was called an older MathDB total. It is the
  other site's sentence. The two pages were not ordered.
- F3 was identified with `frozen-before-search`. A statement the same
  party froze before searching is not a statement from a separate corpus.
- Open conjectures were described as though absence from the training
  corpus had been shown. The paper claims that about its design.
