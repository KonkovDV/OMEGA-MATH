# OpenAI release functions

Read at `openai/math` commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`.
OMEGA did not build the project and did not copy manuscripts. The counts
and the seams are in `research/external/openai_math_catalog_2026.yaml`.
The adversarial pass remains `research/OMEGA_OCTOBER_2026_MURDER_BOARD.md`.

## What the release is

The release is a catalog of drafts, not a list of theorems. An unreleased
internal model was given about 4,000 problems. Results that passed an
unpublished significance filter were grouped into 372 families and 719
manuscripts. A family may hold a principal result, a companion, a
consequence, or another proof of the same idea. The average reported cost
is three hours of ChatGPT Pro thinking compute. Two jobs are named as
exceptions to that fixed procedure: a zero-free region for the zeta
function, and the Hodge conjecture for CM abelian varieties. The writeup
of the region `Re(s) > 11/12` was edited by a person. Ten families also
have an abridged reasoning summary. The search itself cannot be replayed,
because the model is unreleased.

## Citation function

Each manuscript directory carries a short README. The author field is the
organization. The BibTeX key is `OAI:` plus the directory slug. A version
note, when present, points at a sibling directory with an earlier date,
not at a git tag. The `howpublished` URL points at `blob/main`. That URL
moves. OMEGA cites the commit and the slug. A citation of `main` is not a
version.

`CONTENTS.md` at this commit does not contain the three titles withdrawn
on 7 October. `history.md` is the index of those withdrawals. Near-duplicate
titles that remain are different manuscripts:

- The rational Hodge conjecture for CM abelian varieties, 6 October 2026
- Weil classes and Hodge classes on abelian powers, 6 October 2026
- Algebraic Kuga–Satake correspondences and Hodge conjectures on a K3
  quadratic locus, 30 September 2026

None of those three is one of the withdrawn titles. A shared word is not
a shared theorem.

## Comparator function

`lean/ComparatorChallenges/` holds 416 JSON challenges and 416 Lean
modules. A challenge module states the selected theorems and proves them
with `sorry`. The solution module is supposed to prove the same
statements. The upstream Comparator contract, `leanprover/comparator`,
says a successful run means the named theorems in the solution have the
same statement as in the challenge, use only the permitted axioms, and
are accepted by the kernel.

The trust assumptions of that contract are the seam. The challenge file,
its imports, and the lakefile have to be controlled by the checker. In
this repository the challenge and the solution are written by the same
party. A pass shows that the solution matches the challenge that party
wrote. It does not show that the challenge is the theorem a reader thinks
the paper proved.

In a sample of 29 challenge files, 27 leave `definition_names` empty. The
permitted axioms in that sample are `propext`, `Quot.sound`, and
`Classical.choice`. `enable_nanoda` is not constant: nanoda is an optional
second kernel, and a false flag means that kernel was not required. The
Hadwiger challenge restates `hadwigerNumber` in the challenge file and
does not list that definition among `definition_names`. The statement
that is checked is the statement in the challenge, including that local
definition.

Five challenges are labeled by the repository as checks of supporting
results, not of the papers' main theorems: `CharacterVarietiesAllSeamsSupport`,
`CartierChartCompactnessSupport`, `SurfaceConeCandidateSupport`,
`TraceIdealTransportSupport`, and `HoneycombBridgeMassSupport`.

## Scope-note function

`lean/docs/` holds 242 notes, numbered like the families. Each note says
which selected statement was formalized and which claim of the paper is
outside that selection. The pattern is stable across the notes that were
opened. Family 007 formalizes ordinary two-point correlations and leaves
logarithmic averages out. Family 017 formalizes that the irrationality
exponent of π is 2 and leaves the Flint–Hills consequence out. Family 087
formalizes the symmetric Mahler conjecture and the general volume-product
bound, and leaves the nonsymmetric functional inequality out. Family 376
formalizes computation by smooth incompressible flows on the flat
three-torus under a divergence-free force, at positive computable
viscosity, including particles that detect halting. That is not Clay
(A) or (B), and it is not the forced blowup claimed on 8 September.
`history.md` records a repair to the box-transport manuscript in that
family. A formalized Navier–Stokes file is not yet a regularity theorem.

`lean/formalization.yaml` v0.4 lists 173 sources and 200 main-result
declarations and calls its own scope partial. The history file's 300/719
is a separate self-report. The 416 challenges are a third count: several
challenges can belong to one paper, and some of them are support checks.

## Trusted base

The toolchain is `leanprover/lean4:v4.34.1`. Mathlib is pinned at
`d13f23b723b8a846827a245b89c10fc7d3f11612`. The lakefile also pins other
git dependencies and applies compatibility patches named
`*-lean4341.patch` before dependency resolution, including to the
`lana-agents` packages that the lakefile requires. A Comparator pass is
a pass against that patched base. It is not a pass against the upstream
tags alone. OMEGA does not claim that any particular theorem uses those
packages. The seam is the base, not an extra theorem.

## What the commits show

`main` has three commits. No other public branch carries a fourth.

| Commit | Date | Subject | What it contains |
|---|---|---|---|
| `adc7f1241b42` | 6 October 2026, 21:58 UTC | Initial commit | README and CONTENTS say 722 manuscripts. `history.md` does not exist. The three later-withdrawn directories hold full PDFs, from about 639 KB to 812 KB, and a `build/` directory |
| `301488868bee` | 8 October 2026, 05:03 UTC | Update manuscripts and Lean formalizations | README and CONTENTS say 719. `history.md` appears. The subject line does not say that anything was withdrawn |
| `fd4aeeb2ee4f` | 8 October 2026, 05:20 UTC | Merge pull request #1 from `codex/update-10-7` | The update branch merged to `main` |

The preprint directory count goes from 722 to 749. Zero directories are deleted. Twenty-seven new dated directories are added, which is how a revision is published: a new folder, while the old folder stays. The three withdrawn directories stay too, under the same names. In each one the PDF is replaced by a notice of about 3.6 KB, and the `build/` directory is removed. The notice dates the withdrawal 6 October. `history.md` titles the section 7 October. The commit that introduces the notice is 8 October.

Each notice states the gap: a sign error in the stabilization-trace cancellation, so the cited cancellation hypothesis is not met. Each notice says the withdrawal concerns the proof and does not declare the statement false. Each notice links the pre-withdrawal PDF at `adc7f1241b42`. The dependent notices point their ordinary prose link at `blob/main`, which is now the stub, and point the archive link at that initial commit.

`CONTENTS.md` is the map the README tells a reader to use. At the initial commit it names the three manuscripts. At the update it does not. The count in its first line changes from 722 to 719. A reader of HEAD who follows the map does not meet the withdrawn titles. They remain in the git tree and in `history.md`.

The commit page lists 300 files and then stops. In that slice the modified files are `CONTENTS.md`, `README.md`, `lean/ComparatorChallenges/README.md`, and `lean/OAI.lean`. The PDF replacements are not in that slice. The Comparator README gains, in this same commit, the warning that five challenges check supporting results rather than the papers' main theorems. `OAI.lean` gains the import of the Hadwiger counterexample module in this same commit.

The retraction is in the repository. It is not in the commit subject, not in the manuscript map, and not in the first 300 files of the commit page.

## What OMEGA does with this

A Comparator success is stored as `verifier-checked` with
`claim_scope: comparator-selection` and `challenge_party: same-party`.
It becomes `formally-checked` only when the scope is the registry
statement, the fidelity note says the challenge matches that statement,
and `challenge_party` is explicit. `unchecked` cannot be promoted.
Citation uses the commit and the `OAI:` slug. A scope note's "outside"
sentence stays outside. A near-duplicate title is not the withdrawn
manuscript. Family 376 does not close `navier-stokes`.
