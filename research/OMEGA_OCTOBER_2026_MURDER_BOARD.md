---
title: "October 2026 red team and murder board"
status: active
version: "1.0.0"
last_updated: "2026-10-12"
date: "2026-10-12"
role: evidence
audience: internal+academic
tags: [omega, red-team, triage, openai, alphaproof, navier-stokes, hadwiger]
evidence_class: E1
confidence: C2
---

# October 2026 red team and murder board

This note attacks the two October readings before they are allowed to move
a registry status or an amenability score. The statement ledgers are
`research/external/alphaproof_nexus_erdos_2026.yaml` and
`research/external/openai_math_catalog_2026.yaml`. OMEGA did not build
either Lean project.

## Triage

| Surface | What was opened | Disposition | Score |
|---|---|---|---|
| AlphaProof Nexus, commit `0647711a7118` | Nine Erdős targets, still HEAD on 12 October 2026 | External ledger. Three files close their own formal targets. The catalog entries for #12, #138, #26, and #741 stay open | Unchanged |
| `openai/math` commit `fd4aeeb2ee4f`, 8 October 2026 | README, `history.md`, `lean/formalization.yaml` v0.4, three Lean statements | Draft batch. 719 manuscripts, 372 families | Unchanged |
| Self-reported formalization rate | `history.md`: 300/719 | Kept as a self-report | Unchanged |
| `formalization.yaml` | 173 source titles, 200 main-result declarations, scope "Partial progress." | Machine count. It does not confirm 300 | Unchanged |
| Secondary figure 722 | Fork and a rendered page | Rejected. The pinned README says 719 | Unchanged |
| Three withdrawals, 7 October | One sign error, two dependents | First-class retraction | Unchanged |
| Navier–Stokes, 8 September | Company note claims Clay (C) and (D) | External claim. Registry tracks (A) and (B) and stays open | Unchanged |
| arXiv:2610.08144 | Lemma 8.6 and pressure-flux bound (10.19) | Lean at `f9e8bc5b38b6` is not a semantic copy of the prose. The paper does not call the prose false | Unchanged |
| Zeta, `Re(s) > 11/12` | README exception, human-edited writeup | Special case | Unchanged |
| Zeta, `Re(s) > 7/8` | `Nonvanishing.lean` at the pinned commit | Different theorem. Binder does not exclude `s = 1` | Unchanged |
| Hodge for CM abelian varieties | README exception | Special case. The K3-product manuscript is withdrawn | Unchanged |
| Hadwiger | `not_hadwiger_conjecture` | The formal sentence matches the registry sentence. Build and definitions are unchecked, so the entry stays open | Unchanged |
| Seymour second neighborhood | `exists_goodVertex` | `GoodVertex` was not read. No registry id is added | Unchanged |
| Cubic percolation | A source title only | Declaration not matched. Not added to the registry | Unchanged |
| Le Monde, 10 October, and SMF MIAM, 8 October | Reported judgment that a field was annihilated | Class E2. Not a status | Unchanged |
| Declaration DOI 10.5281/zenodo.22737750 | 11 September 2026 | Process constraint: a solution is not yet a transmitted proof | Unchanged |

## Attacks that failed

The count 719 was checked again at `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`,
not at a floating branch name. The three withdrawn titles match `history.md`
at that commit. AlphaProof Nexus HEAD on this date is still
`0647711a71183c1ea492ad60860776617ce1ea88`. The 8 September note identifies
its Navier–Stokes result as Clay (C) and (D), with a smooth compactly
supported force, and says the prize is not being claimed. The commit
`f9e8bc5b38b6e212696e8a30e3e91517af887bbd` on `openai/NavierStokesAndEuler`
exists; that existence does not make the prose and the Lean file the same
argument.

## Attacks that landed

Four earlier formulations did not survive.

1. Leaving the OpenAI snapshot unpinned. The ledger now stores the commit.
2. Reading 300/719 as if it were the length of `formalization.yaml`. The
   file's own scope line says the catalog is partial. One hundred declarations
   separate 200 from 300, and the units may differ. Both numbers stay, and
   `matches_self_report` is false.
3. Mentioning only the human-edited region `Re(s) > 11/12`. The formalized
   zeta sentence in the pinned tree is the stronger half-plane `Re(s) > 7/8`.
   `11/12` is about `0.9167` and `7/8` is `0.875`, so the second claim
   excludes zeros farther from the line `Re(s) = 1`. The Riemann hypothesis
   is the line `Re(s) = 1/2`. The Dirichlet theorem in the same file excludes
   the principal pole. The zeta theorem's binder does not. A reviewer still
   has to know what `riemannZeta` does at `1` in that toolchain. OMEGA does
   not guess that value.
4. Treating a catalog title as unread. `not_hadwiger_conjecture` says it is
   false that every simple graph on `Fin m` satisfies
   `chromaticNumber ≤ hadwigerNumber`. The registry sentence, "every graph
   of chromatic number `k` has a `K_k` minor," is that claim for finite
   graphs. `exists_counterexamples` adds a quantitative construction:
   independence number at most 2, a touching-matching bound `m/100`, and a
   gap between the Hadwiger number and the chromatic number. The proof
   imports three construction modules and a matching module. Those files
   were not opened, the definitions of the two graph invariants were not
   audited, and the project was not built. A matching sentence with an
   unchecked proof is not a closed entry. `hadwiger-conjecture` stays
   `open`.

`exists_goodVertex` is the same kind of limit in the other direction. The
file shows a finite nonempty oriented relation has a `GoodVertex`. The
definition of that predicate is in an import. Seymour's second-neighborhood
conjecture is not an OMEGA registry id, and §1.5 still blocks adding one
from a title.

## Murder board

**Did the Navier–Stokes wording get narrowed in order to avoid a claimed
proof?** The previous sentence asked whether solutions "always" exist and
stay smooth, and it never said whether a force was allowed. That sentence
cannot be the target of a proof result, because Clay (A)/(B) and Clay
(C)/(D) answer it differently. The entry now names (A) and (B). The forced
claim is unadopted for a second, independent reason: arXiv:2610.08144
separates the Lean development from the prose at Lemma 8.6 and at the
pressure-flux bound (10.19), and it declines to call either text false.

**Can a faithful special case be promoted onto the registry problem?**
Before this review, `formally-checked` required `statement_fidelity` of
`faithful` or `amended` and did not ask whether the faithful sentence was
the registry sentence. `scripts/omega_runner.py` now requires
`claim_scope: registry-statement` for `formally-checked` and `verified`.
A zero-free region, a forced blowup, or a catalog title can be stored at
`verifier-checked` and cannot take the formal status of the open problem.

**Should Hadwiger move because the formal negation matches?** No. Match of
the statement is the first gate. A local build and a definition audit are
the second. The score is not invented in this pass: `hadwiger-conjecture`
has no amenability entry, and a new score taken from an unchecked file
would be a headline rescore.

**Should the field reported as annihilated change tier?** No. The SMF page
confirms the 8 October talk. The newspaper body was not retrieved. Page
counts, a list of sixteen personal questions, and named percolation
theorems stay under `not_adopted`.

## What remains for a human

A later pass may build `OAI.HadwigerCounterexample.not_hadwiger_conjecture`
and audit `chromaticNumber` and `hadwigerNumber`. Until that command is
recorded, the disposition stays `sentence-matches-build-missing`. The same
rule applies to every other declaration in the 200. Opening three files
does not certify the rest.
