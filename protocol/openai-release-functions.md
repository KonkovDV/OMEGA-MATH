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

## What OMEGA does with this

A Comparator success is stored as `verifier-checked` with
`claim_scope: comparator-selection` and `challenge_party: same-party`.
It becomes `formally-checked` only when the scope is the registry
statement, the fidelity note says the challenge matches that statement,
and `challenge_party` is explicit. `unchecked` cannot be promoted.
Citation uses the commit and the `OAI:` slug. A scope note's "outside"
sentence stays outside. A near-duplicate title is not the withdrawn
manuscript. Family 376 does not close `navier-stokes`.
