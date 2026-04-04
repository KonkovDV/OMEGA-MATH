# OMEGA Research Protocol
# Version: 0.1.0 | Date: 2026-04-04

## 1. Overview

OMEGA (Open Mathematics Exploration by Generative Agents) is a systematic protocol for applying AI agents to the full landscape of unsolved mathematical problems. Unlike ad-hoc attempts where an LLM is pointed at a single famous conjecture, OMEGA takes a **catalog-first, triage-driven** approach:

1. **Catalog** every known open problem in machine-readable format
2. **Triage** each problem by AI-amenability (not difficulty alone)
3. **Research** systematically, starting from the most tractable tier
4. **Publish** all results — including negative results and refined conjectures

## 2. Problem Taxonomy

### 2.1 Domains (12 primary, from Wikipedia's master list)

| # | Domain | Subdomain count | Est. open problems |
|---|--------|----------------|-------------------|
| 1 | Algebra | 3 (general, group theory, representation theory) | ~40 |
| 2 | Analysis | 1 | ~15 |
| 3 | Combinatorics | 1 | ~15 |
| 4 | Dynamical Systems | 1 | ~15 |
| 5 | Games & Puzzles | 2 (combinatorial, imperfect info) | ~10 |
| 6 | Geometry | 6 (algebraic, covering/packing, differential, discrete, Euclidean, non-Euclidean) | ~80 |
| 7 | Graph Theory | 8 (algebraic, games, coloring, drawing, restriction, subgraphs, word-rep, misc) | ~60 |
| 8 | Model Theory & Formal Languages | 1 | ~5 |
| 9 | Number Theory | 8 (general, additive, algebraic, analytic, arithmetic geo, computational, Diophantine approx, Diophantine eq, primes) | ~120 |
| 10 | Probability Theory | 1 | ~5 |
| 11 | Set Theory | 1 | ~10 |
| 12 | Topology | 1 | ~20 |
| **Total** | | **~35** | **~395+** |

### 2.2 Named Collections

| Collection | Count | Unsolved | Year | Source |
|-----------|-------|----------|------|--------|
| Hilbert's problems | 23 | 13 | 1900 | David Hilbert |
| Landau's problems | 4 | 4 | 1912 | Edmund Landau |
| Taniyama's problems | 36 | — | 1955 | Yutaka Taniyama |
| Thurston's 24 questions | 24 | 2 | 1982 | William Thurston |
| Smale's problems | 18 | 14 | 1998 | Stephen Smale |
| Millennium Prize Problems | 7 | 6 | 2000 | Clay Mathematics Institute |
| Simon problems | 15 | <12 | 2000 | Barry Simon |
| DARPA math challenges | 23 | — | 2007 | DARPA |
| Erdős's problems | >1183 | 692 | 1930s–1990s | Paul Erdős |
| Kourovka Notebook | ~100+ | ~100+ | 1965+ | Group theory |
| Sverdlovsk Notebook | ~100+ | ~100+ | 1965+ | Semigroup theory |
| Dniester Notebook | 100+ | 100+ | — | Ring/module theory |
| Erlagol Notebook | — | — | — | Algebra/model theory |

## 3. AI Approach Tiers

The key insight: mathematical problems vary enormously in how amenable they are to current AI/computational approaches. We classify into 5 tiers:

### T1 — Computational (amenability: 8–10)
**Profile:** Direct computation, exhaustive or heuristic search, SAT/SMT solving.
**Examples:** Specific Ramsey numbers, Van der Waerden numbers, Dedekind numbers, busy beaver values, specific counterexample searches.
**Tools:** SAT solvers (Kissat, CaDiCaL), SMT solvers (Z3), distributed computing, SageMath.
**Agent role:** Set up computation, manage search space, verify results.

### T2 — Experimental (amenability: 5–7)
**Profile:** Numerical experiments can provide strong evidence, discover patterns, verify special cases. Full proof may be out of reach but partial results are publishable.
**Examples:** Goldbach conjecture verification to large bounds, Collatz conjecture statistics, distribution of primes in various sequences, numerical checks of Riemann hypothesis zeros.
**Tools:** Python/SageMath for computation, matplotlib for visualization, statistical analysis.
**Agent role:** Design experiments, run large-scale verification, analyze patterns, formulate refined conjectures.

### T3 — Pattern Recognition (amenability: 3–5)
**Profile:** Finding patterns, analogies, or structural similarities across known results could yield new approaches. Requires mathematical intuition that LLMs may partially possess.
**Examples:** Connections between different conjectures, suggesting proof strategies by analogy, identifying when known techniques might apply.
**Tools:** LLM reasoning, literature search, analogy engines, knowledge graphs.
**Agent role:** Literature survey, cross-domain insight generation, conjecture refinement.

### T4 — Structural (amenability: 1–3)
**Profile:** Deep algebraic, geometric, or topological reasoning required. Current AI can scaffold but not autonomously solve.
**Examples:** Most algebraic geometry conjectures, Hodge conjecture, Yang–Mills existence.
**Tools:** Lean 4 / Coq for proof verification, Mathematica for symbolic computation.
**Agent role:** Formalize known partial results, explore proof strategies, verify proposed proofs.

### T5 — Foundational (amenability: 0–1)
**Profile:** Metamathematical, logical, or foundational issues. May be independent of standard axioms.
**Examples:** Large cardinal consistency, continuum hypothesis variants, P vs NP.
**Tools:** Proof assistants for independence proofs, forcing constructions.
**Agent role:** Literature survey, formalization of known results, exploration of axiom alternatives.

## 4. Agent Architecture

### 4.1 Agent Roles (Denario-inspired)

Following the Denario framework (arXiv:2510.26887), each research task employs a team of specialized agents:

| Agent | Role | Denario Mapping |
|-------|------|-----------------|
| **Librarian** | Literature search, bibliography, related work | Background Agent |
| **Analyst** | Problem analysis, approach evaluation, triage | Methodology Agent |
| **Experimentalist** | Numerical experiments, computation, verification | Results Agent |
| **Prover** | Formal proofs, Lean 4 / Coq, proof strategies | (new role) |
| **Writer** | Paper generation, LaTeX, scientific writing | Paper Writing Agent |
| **Reviewer** | Quality control, peer review simulation | Peer Review Agent |

### 4.2 Workflow (CMBAgent-inspired)

Following CMBAgent's Planning & Control pattern (arXiv:2507.07257):

```
┌──────────────────────────────────────────────────┐
│                   PLANNER                         │
│  Receives problem → Creates research plan         │
│  Allocates agents → Monitors progress             │
└──────────────┬───────────────────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Librarian│ │Analyst │ │Experi- │
│         │ │        │ │mentalist│
└────┬───┘ └───┬────┘ └───┬────┘
     │         │           │
     └─────────┼───────────┘
               ▼
          ┌────────┐
          │ Prover │
          └───┬────┘
              ▼
         ┌────────┐
         │ Writer │
         └───┬────┘
              ▼
         ┌────────┐
         │Reviewer│
         └────────┘
```

### 4.3 Research Phases

Each problem investigation follows these phases:

1. **RECON** — Librarian surveys existing literature, known partial results, failed approaches
2. **TRIAGE** — Analyst assigns AI tier, selects approach strategy, estimates feasibility
3. **EXPERIMENT** — Experimentalist runs computations, searches for patterns/counterexamples
4. **PROVE** — Prover attempts formalization, explores proof strategies (if T1–T3)
5. **WRITE** — Writer generates paper draft covering methodology and all results
6. **REVIEW** — Reviewer checks correctness, identifies gaps, requests revisions
7. **PUBLISH** — Final paper formatted for arXiv submission

## 5. Publication Standards

### 5.1 What Counts as a Result

OMEGA publishes **all** non-trivial outcomes:

| Outcome | Publication Value |
|---------|------------------|
| Complete proof | Highest — submit to journal |
| Counterexample | High — disproves conjecture |
| New partial result | High — extends known bounds |
| Computational verification to new bound | Medium — extends numerical evidence |
| Refined conjecture | Medium — improves problem statement |
| Novel connection between problems | Medium — cross-domain insight |
| Comprehensive survey with AI analysis | Medium — useful to community |
| Negative result (approach X doesn't work, with proof) | Low-Medium — saves future effort |
| Formalization in Lean 4 / Coq | Medium — advances formal mathematics |

### 5.2 Paper Structure (Denario format)

```latex
\title{OMEGA-[ID]: [Problem Name] — [Result Type]}
\author{OMEGA Collective}

\begin{abstract}
[Concise summary of result]
\end{abstract}

\section{Introduction}
[Problem statement, historical context, known results]

\section{Methodology}
[AI-driven approach, tools used, computational setup]

\section{Results}
[Main results, theorems/computations/counterexamples]

\section{Discussion}
[Implications, limitations, comparison with prior work]

\section{Related Work}
[Literature survey by Librarian agent]

\section{Reproducibility}
[Code, data, computational environment specifications]
```

## 6. Prioritization Strategy

### 6.1 First Wave — Low-Hanging Fruit (T1)

Start with problems where computation directly yields results:
- Extending Ramsey number bounds
- Computing additional Dedekind numbers
- SAT-based approaches to combinatorial problems
- Searching for counterexamples to open conjectures
- Verifying conjectures to larger bounds

### 6.2 Second Wave — Experimental Insights (T2)

Problems where large-scale numerical evidence is valuable:
- Prime distribution conjectures (twin primes, Goldbach, etc.)
- Dynamical systems (Collatz, etc.)
- Number-theoretic constants
- Self-avoiding walk enumeration

### 6.3 Third Wave — Cross-Domain Patterns (T3)

Use LLM's broad knowledge for cross-domain insights:
- Connections between graph theory and algebraic geometry
- Topology-physics bridges (knot invariants, quantum groups)
- Combinatorial interpretations of algebraic objects

### 6.4 Fourth Wave — Formal Mathematics (T4–T5)

Long-term formalization and proof exploration:
- Formalizing known partial results in Lean 4
- Exploring proof strategies via neural theorem proving
- Building formal libraries for specific problem domains

## 7. Tools & Infrastructure

| Tool | Purpose | Integration |
|------|---------|-------------|
| SageMath | Symbolic computation, number theory | Python API |
| Lean 4 | Formal proofs | LSP + elan |
| Z3 / CaDiCaL | SAT/SMT solving | Python bindings |
| arXiv API | Paper search, submission | REST API |
| Semantic Scholar | Citation network | REST API |
| Google Scholar | Literature search | Scraping / SerpAPI |
| OEIS | Integer sequences | REST API |
| Mathematica | Symbolic computation | WolframScript |
| PARI/GP | Number theory | C library / Python |
| GAP | Group theory | Interactive |
| Macaulay2 | Algebraic geometry | Interactive |

## 8. Quality Gates

Before any OMEGA result is published:

- [ ] **Correctness check**: Independent verification of all computations
- [ ] **Reproducibility**: All code and data available, environment documented
- [ ] **Literature check**: No prior publication of the same result
- [ ] **Formatting**: Standard LaTeX, proper citations, clear exposition
- [ ] **Self-assessment**: Honest evaluation of limitations and what was NOT achieved
- [ ] **Peer review simulation**: Reviewer agent with adversarial stance

## 9. Ethical Guidelines

1. **Honest attribution**: OMEGA results are AI-generated. Always state this clearly.
2. **No overclaiming**: Numerical evidence ≠ proof. Partial results ≠ complete solutions.
3. **Reproducibility**: Every result must be independently verifiable.
4. **Community respect**: Don't flood arXiv with trivial extensions. Batch results.
5. **Credit**: Cite all human work that OMEGA builds upon.
6. **Open source**: All tools, code, and data are open under MIT/CC-BY-4.0.

## 10. Success Metrics

| Metric | Target (Year 1) | Target (Year 3) |
|--------|-----------------|-----------------|
| Problems cataloged | 500+ | 2000+ |
| Problems triaged | 500+ | 2000+ |
| Computational results | 20+ | 100+ |
| Published papers | 5+ | 30+ |
| Counterexamples found | 1+ | 5+ |
| Conjectures refined | 5+ | 25+ |
| Lean 4 formalizations | 10+ | 50+ |
| Conference acceptances | 0 | 3+ |
