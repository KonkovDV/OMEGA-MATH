---
title: "Reading of the OpenAI mathematics catalog"
status: active
version: "1.0.0"
last_updated: "2026-10-12"
date: "2026-10-12"
role: evidence
audience: internal+academic
tags: [omega, openai, lean, navier-stokes, hodge, riemann, evidence-governance]
evidence_class: E1
confidence: C2
---

# Reading of the OpenAI mathematics catalog

This note is the statement-level reading behind PROTOCOL.md §1.10. Counts
live in `research/external/openai_math_catalog_2026.yaml`. The Le Monde
article of 10 October 2026 is the occasion. Its body did not load: the
page returned a client challenge. The title in the URL is journalism. The
mathematical distinctions below come from the catalog, from the Clay
split as OpenAI's own note identifies it, and from a fidelity paper. They
do not come from the newspaper.

## 1. What was read

Primary catalog, retrieved 12 October 2026 at commit
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` (8 October 2026):

- `README.md`. 719 manuscripts in 372 families. A family may hold a
  principal result, a companion, a consequence, or an alternative proof.
  About 42 percent of top-line results have a Lean formalization. The
  unreleased internal model was posed about 4,000 problems. A typical
  result used three hours of ChatGPT Pro thinking compute. Unformalized
  results may have issues. Citation is the BibTeX block of the manuscript,
  and earlier versions stay available.
- `history.md`, dated 7 October 2026. Three withdrawals from one sign
  error. Fourteen other manuscripts revised. Thirteen further manuscripts
  updated only so that they cite the revised companions. Six new
  formalizations and five supporting additions bring the formalized count
  to 300/719, which the history file writes as about 42 percent.
- `lean/formalization.yaml`, version v0.4. Its scope line says "Partial
  progress." It lists 173 source titles and 200 main-result declarations.
  That file does not independently confirm the figure 300.

OMEGA did not run Comparator, did not build the Lean library, and did not
copy PDFs. The adversarial pass is
`research/OMEGA_OCTOBER_2026_MURDER_BOARD.md`.

The release note of 6 October 2026,
`https://openai.com/index/sharing-ai-progress-in-mathematics/`, matches
the compute sentence and says the Institute for Advanced Study advisory
group was consulted. It is a company note, class E2, and it is not a
stronger count than the README.

A fork and some secondary pages repeat 722. That number is the
repository's own initial commit, `adc7f1241b42` (6 October 2026), in both
`README.md` and the first line of `CONTENTS.md`. The next commit,
`301488868bee` (8 October 2026), changes both lines to 719. The current
ledger uses 719 for the pinned HEAD and keeps 722 as the opening count.

## 2. A family is not a theorem

The catalog is a batch of drafts. The history file says 300 of the 719
top-line results have some Lean. The machine-readable catalog at the same
commit is shorter and labels itself partial, so the manuscripts without a
matched declaration stay `draft`. A result reaches `formally-checked` only
when a named file, a frozen statement, and a checker exist,
`statement_fidelity` is `faithful` or `amended`, and `claim_scope` is
`registry-statement`.

The history file is the operational lesson. The sign error is in
"Algebraicity of Weil classes on split abelian eightfolds". It breaks a
stabilization-trace cancellation and a construction used by two other
manuscripts, which were withdrawn with it:

- Algebraicity of Kuga–Satake Correspondences for K3 Surfaces
- The rational Hodge conjecture for products of K3 surfaces

The third title is a special case of a rational Hodge statement for
products of K3 surfaces. It is not the Hodge conjecture, and it is
withdrawn. A later reader who cites the 6 October version without the
7 October withdrawal is citing a retracted argument.

The fourteen repairs are also part of the claim surface, not a footnote.
They include four manuscripts on Lipschitz heights and Ashkin–Teller
currents, six on Kähler minimal model programs and abundance, two on
taming and hypersymplectic deformation, one on incompressible box
transport, and one on an exact Birch–Swinnerton-Dyer formula at low
Selmer corank, the last of these being a removed citation. "Abundance"
in that list is not the abundance conjecture in `registry/domains/`.
Nothing in this note closes `abundance-conjecture` or
`birch-swinnerton-dyer`.

## 3. A special case is not the registry problem

The README names two exceptions to the fixed generation procedure.

The zero-free region `Re(s) > 11/12` for the Riemann zeta function is a
region, not the critical line. The writeup of that region was edited by a
person for readability. A different file at the same commit,
`lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean`, states that
`riemannZeta` is nonzero when the real part exceeds `7/8`. That binder
does not exclude `s = 1`, while the Dirichlet theorem beside it does
exclude the principal pole. `7/8` is a stronger half-plane than `11/12`,
and neither is the line `Re(s) = 1/2`. `riemann-hypothesis` stays `open`.

`not_hadwiger_conjecture` in
`lean/OAI/Combinatorics/HadwigerCounterexample/Main.lean` is the negation
of `chromaticNumber ≤ hadwigerNumber` for every finite simple graph. That
sentence is the registry entry. The file was read. The imported
construction was not, and the library was not built. `hadwiger-conjecture`
stays `open`.

"Proof of the Hodge Conjecture for CM abelian varieties" is a restriction
on the variety. The registry statement is the Hodge conjecture for a
projective nonsingular variety over the complex numbers. `hodge-conjecture`
stays `open`. The withdrawn manuscript on products of K3 surfaces is a
third, different sentence, and it is not available as a theorem.

## 4. Navier–Stokes: forced blowup is not unforced regularity

On 8 September 2026 OpenAI published a separate note,
`https://openai.com/index/navier-stokes-solution/`. The result it states
is a finite-time singularity for a 3D incompressible fluid that starts at
rest, under a smooth compactly supported force, with energy remaining
finite. The note says this is Clay statement (C), and also (D). It says
the company does not intend to claim the Millennium Prize.

The same note separates an unforced Euler blowup, produced by a smaller
group of agents, from the forced Navier–Stokes claim. It also says a
concurrent forced-Euler result of Alpöge and Buckmaster has priority on
that forced Euler question. Those are three different theorems.

Clay (A) and (B) are the unforced regularity questions, on Euclidean space
and on the torus. The 8 September note does not claim them. The sentence
previously stored for `navier-stokes` asked whether solutions "always"
exist and stay smooth, and it did not say whether a force was allowed.
That wording mixed (A)/(B) with (C)/(D). The registry statement now names
(A) and (B). Status remains `open`.

Two further limits sit on top of that split, and neither is a verdict
that the forced argument is false:

- Bastounis, Circelli, and Hansen, arXiv:2610.08144, show that the Lean
  development is not a semantic translation of the prose. One concrete
  divergence is Lemma 8.6: the Lean estimate spends one more derivative
  than the prose (`m+5` rather than the prose bound). Their disclaimer
  says they do not claim the prose is wrong and do not claim it is right.
  A compiling file therefore does not certify the manuscript. This is the
  same fidelity gate as PROTOCOL.md §1.9, reached from the other
  direction: here the prose is the thing that has not been checked.
- Scientific American reports Luis Silvestre distinguishing the Clay
  option that allows a force from the unforced problem, and reports a
  further argument that this forced construction does not extend to the
  unforced equations. That report is class E2. OMEGA does not adopt the
  non-extension argument as a theorem.

## 5. What the newspaper and the seminar change

Le Monde, 10 October 2026, is class E2. The URL's title reports Hugo
Duminil-Copin saying that the release annihilated his research domain.
The Société Mathématique de France page confirms a talk in the seminar
MIAM on 8 October 2026, titled "Un grave défaut d'alignement de l'IA en
math", and says the page was updated on 9 October. The video was not
transcribed for this note.

Secondary accounts add page counts, a list of sixteen personal questions,
percolation, the six-vertex height function, and a description of the
model choosing its own problems. Those details are not in the README and
were not checked against `CONTENTS.md` manuscript by manuscript. They are
listed in the ledger under `not_adopted`. They do not move
`self-avoiding-walk-connective`. The hexagonal connective constant is
already the Duminil-Copin–Smirnov theorem. The open remainder in the
registry is the square lattice and the other lattices in that statement.
A manuscript about self-avoiding walks, even a long one, is not a value
of that constant until the statement is matched and checked.

The judgment that a domain has been annihilated is evidence about the
shock to a community and about how problems were selected. It is not a
status. The declaration those remarks belong to is "A Severe Misalignment
of AI in Mathematics", 11 September 2026, DOI 10.5281/zenodo.22737750.
Terence Tao's post of that day says there were 25 initial Fields Medal
signatories. The declaration page retrieved on 12 October 2026 lists 28,
including Duminil-Copin. The sentence OMEGA takes from it is the one that
matches the protocol: solving a problem is a proxy for understanding, and
a mass of true-or-false announcements is not yet a transmitted proof.
The human remainder is to understand the argument, digest the
dependencies, and write a statement a student can check. That is the
referee lane. It is not a second generation pass over the PDFs.

## 6. The release functions

The production rule, the citation block, the Comparator contract, the
scope notes, and the patched Lean base are written out in
`protocol/openai-release-functions.md`. The operational point is that a
Comparator success matches a challenge written by the same party, a scope
note can leave the paper's main consequence outside the formalized
sentence, and the BibTeX URL tracks `main` rather than a commit. Family
376 is a forced computation result, not the regularity problem.

## 7. What this note does not do

- It does not copy the catalog, the Le Monde article, or the declaration.
- It does not mark `navier-stokes`, `riemann-hypothesis`,
  `hodge-conjecture`, `self-avoiding-walk-connective`,
  `abundance-conjecture`, or `birch-swinnerton-dyer` solved.
- It does not change an amenability score.
- It does not treat 300/719 as an independent audit. That fraction is the
  repository's own figure on 7 October 2026.
