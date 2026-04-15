# OMEGA Research Protocol
# Version: 0.5.0 | Date: 2026-04-13

## 1. Overview

OMEGA (Open Mathematics Exploration by Generative Agents) is a systematic protocol for applying AI agents to the full landscape of unsolved mathematical problems. Unlike ad-hoc attempts where an LLM is pointed at a single famous conjecture, OMEGA takes a **catalog-first, triage-driven** approach:

1. **Catalog** every known open problem in machine-readable format
2. **Triage** each problem by AI-amenability (not difficulty alone)
3. **Research** systematically, starting from the most tractable tier
4. **Publish** all results — including negative results and refined conjectures

OMEGA is a **standalone repository**. It borrows reusable ideas from external scientific-agent systems, but does not depend on their runtimes at execution time. The protocol is therefore split into two layers:

1. **Donor-extracted patterns** — what is adopted from Denario, CMBAgent, and LSST DESC
2. **Local operating contract** — what OMEGA actually stores, validates, and publishes inside this repository

## 1.1 External Donor Extraction Baseline

The current protocol is grounded in five externally verified sources:

- **Denario (arXiv:2510.26887 + repo)**: modular research pipeline with separate idea, methods, results, paper, and referee modules; project-directory contract based on persisted markdown artifacts and plots
- **OpenReview Agents4Science paper (`LENY7OWxmN`)**: evidence that at least one Denario-generated paper was accepted, while reviews still surfaced methodological weaknesses and reproducibility concerns
- **CMBAgent repo + papers (`arXiv:2507.07257`, precursor `arXiv:2412.00431`)**: planning/control architecture with structured plan recording, explicit execution-control semantics, and a newer `deep_research` workflow with context carryover; use the repo for current operator guidance and `2507.07257` for paper-level citation
- **LSST DESC AI/ML roadmap (arXiv:2601.14235)**: requirements for uncertainty quantification, validation, robustness, reproducibility, and scientific-software infrastructure at scale
- **EinsteinArena-new-SOTA (`togethercomputer/EinsteinArena-new-SOTA`, README snapshot April 2026)**: benchmark donor for reproducible objective functions, baseline-vs-new score tables, and public verification notebook patterns for AI-discovered math constructions

OMEGA uses these sources as **architectural donors**, not as permission to overclaim full autonomy or publication quality.

## 1.2 Research-Intelligence Expansion (April 2026)

Beyond the initial Denario, CMBAgent, and LSST DESC donor set, OMEGA now tracks a
research-intelligence support layer for literature discovery, bounded experiment design,
and presentation packaging.

Open-source workflow donors verified in the April 2026 pass:

- MiroThinker
- open-researcher
- Vane / Perplexica
- autoresearch
- Paper2Slides
- create-llm

External support services classified for optional use:

- research-grade retrieval support: Elicit, Scite, Litmaps, Inciteful, ResearchRabbit, Connected Papers, SciSpace
- presentation helper: WorkPPT
- tutor-only supplemental surfaces: MathGPT Pro / Mathos AI, Examful
- explicitly excluded: detector-bypass and AI-humanizer workflows

These tools do not change OMEGA's standalone execution boundary. They only justify local
receiver surfaces such as `literature_graph.md`, `citation_evidence.md`,
`experiments/ledger.yaml`, `artifacts/prover-results/`, and `presentation/`.

See `protocol/research-intelligence-stack.md` for the donor and service mapping.

## 1.3 Vibe-Proving and Formal-Math Update (April 2026)

The April 2026 pass also added a proof-workflow evidence layer grounded in:

- **Verbeken et al. (arXiv:2602.18918)**: consumer-LLM vibe-proving with auditable transcripts, versioned drafts, and explicit `generate -> referee -> repair` loop
- **Feng et al. (arXiv:2601.22401; 2602.10177)**: semi-autonomous open-problem screening, autonomy/novelty gradation, and literature-collision risk
- **Numina-Lean-Agent (arXiv:2601.14027 + repo)**: open Lean-first formal-math agent stack
- **Omni-MATH-2 (arXiv:2601.19532)**: judge-induced saturation and the need for stronger verification than LLM judging alone

Operational consequences for OMEGA:

1. Proof-first work should treat model outputs as candidates, not verified facts.
2. LLM-assisted proof runs should persist `input_files/proof_obligations.md`.
3. Human or formal-tool correctness closure remains mandatory for theorem-level claims.
4. Press narratives are secondary evidence; the paper and maintained repo are the authority surfaces.
5. OMEGA should grade autonomy and novelty rather than using binary "autonomous / not autonomous" rhetoric.

Companion synthesis:

- `research/OMEGA_LOCAL_WORKSTATION_VIBE_PROVING_STACK_2026_04_04.md` records the verified local-stack findings for Lean 4, mathlib4, vscode-lean4, LLMLean, LeanCopilot, llmstep, LeanTool, UlamAI, Ollama, llama.cpp, vLLM, and the currently promoted open prover-model families.
- OMEGA should treat that companion report as the authority surface for workstation deployability and setup heuristics, rather than relying on retail-price or throughput folklore.
- `protocol/lean-bootstrap.md` provides the step-by-step Lean 4 + proof-assistant + local model runtime bootstrap recipe, grounded in official docs.

## 1.4 Neural Theorem Proving SOTA Update (April 2026)

The April 2026 landscape analysis added frontier neural theorem proving evidence:

- **DeepSeek-Prover-V2** (deepseek-ai/DeepSeek-Prover-V2, 2025): 88.9% MiniF2F-test, 49/658 PutnamBench. Architecture: recursive subgoal decomposition by large model (671B) → independent solving by small model (7B) → RL with Lean 4 compiler as reward. Open-weight 7B and 671B variants. This is the dominant paradigm for formal theorem proving as of April 2026.
- **Kimina-Prover** (arXiv:2504.11354, MoonshotAI/Numina): 80.7% MiniF2F pass@8192. First demonstration that model-size scaling improves neural theorem proving. Whole-proof generation without MCTS or PRM. Formal Reasoning Pattern: think → formalize → verify. Open-weight distilled 1.5B and 7B models.
- **LeanCopilot v4.28.0** (arXiv:2404.12534, lean-dojo/LeanCopilot, MIT): automates 74.2% of proof steps. Provide `suggest_tactics`, `search_proof`, `select_premises` natively in Lean 4. Bring-your-own-model via `ExternalGenerator` Python API server. This is the recommended integration surface for OMEGA's proof lane.
- **Process Advantage Verifiers** (arXiv:2410.08146): step-level reward models give +8% accuracy and 5-6× sample efficiency over outcome reward models. Applicable to ranking candidate tactics in OMEGA's proof-repair loop.
- **FrontierMath** (arXiv:2411.04872, Epoch AI): current SOTA models solve under 2% of research-grade math problems. This quantifies the gap between current AI and research-level mathematical capability and serves as OMEGA's honest calibration surface.

Operational consequences:

1. OMEGA should adopt the two-level architecture: large model decomposes, small model proves subgoals.
2. LeanCopilot's ExternalGenerator API replaces the need for a custom Lean-LLM bridge.
3. DeepSeek-Prover-V2-7B is the recommended workstation model (32K context, GGUF-quantizable).
4. FrontierMath calibration: OMEGA should target Tier 1-2 subproblems, not claim general research-level capability.
5. PAV-style scoring should be used for candidate ranking in proof-repair loops.

Companion reports:

- `research/OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md` — full SOTA landscape report with verified benchmarks, model comparisons, and capability gap analysis
- `research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md` — concrete execution plan grounded in this landscape analysis

## 1.5 Execution Plan and Roadmap Integration (April 2026)

The April 2026 analysis produced four complementary planning documents:

- **6-Phase Execution Plan** (`research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md`): Phase 1 (Pipeline Closure) → Phase 2 (LLM Proof Search) → Phase 3 (Literature Verification) → Phase 4 (Multi-Agent Orchestration) → Phase 5 (Publication) → Phase 6 (Formal Assurance). Phase 1 is the sole blocking prerequisite for all subsequent work.
- **Development Roadmap** (`research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md`): 5-horizon strategy from Execution Bootstrap (2026-2027) through Continuous Discovery Grid (2055-2076).
- **SOTA Landscape Report** (`research/OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md`): evidence surface for external proving capability, benchmarks, integration surfaces, and capability gap analysis.
- **SOTA Bibliography** (`research/OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md`): standalone academic reference with 25+ primary papers, 15+ maintained repositories, and 6 benchmark surfaces.

The strategic bottleneck identified across all four documents is consistent:

> The main bottleneck is not registry breadth. The main bottleneck is the absence of a repeatable execution loop: `triage → workspace → experiments → proof attempt → evidence bundle → writeup → review`.

Operational consequences:

1. Do not expand the registry until at least 3 T1 problems have completed the full lifecycle.
2. Do not build visionary infrastructure until the existing adapters produce real evidence bundles.
3. Prioritize LeanCopilot ExternalGenerator API as the integration surface for proof search.
4. Use Semantic Scholar API (free tier, 100 req/sec) for literature verification.
5. Treat FrontierMath as a calibration surface, not a target.

## 1.6 Orchestrator and Model Router (v0.5.0, April 2026)

The v0.5.0 release closes the primary Phase 1 bottleneck — the absence of a repeatable
execution loop — by adding three new infrastructure components:

1. **Agent Orchestrator** (`scripts/agent_orchestrator.py`, CLI: `omega-orchestrate`):
   8-stage pipeline dispatcher that loads agent definitions, assembles problem context,
     enforces per-stage workspace prerequisites, constructs structured prompts, invokes
     LLM backends, parses YAML output artifacts, and persists both responses and prompt
     packets with SHA-256 checksums.

2. **Model Router** (`scripts/model_router.py`, CLI: `omega-model-router`):
   Declarative routing layer mapping agent roles and problem tiers to specific LLM
   backends (OpenAI, DeepSeek, Anthropic, Ollama, vLLM, LM Studio) with fallback
   chains and health checks. Designed for the two-level architecture where large
   models decompose and small models solve.

3. **Evidence Verification CLI** (`scripts/verify_evidence.py`, CLI: `omega-verify-evidence`):
   Standalone SHA-256 evidence bundle compute/verify/status tool.

4. **Workspace Artifact Schema Validation** (`scripts/validate_registry.py`):
     In addition to registry/domain checks, the validator now enforces separate JSON Schemas for
     `research/active/*/experiments/ledger.yaml` and workspace evidence bundles via
     `registry/schemas/experiment-ledger.schema.json` and
     `registry/schemas/evidence-bundle.schema.json`.

The repeatable execution loop is now:
```
triage → workspace → experiment → evidence-bundle → writeup → review
```

All outputs are classified as evidence class E2 (LLM-assisted, requires verification)
until a formal verification step upgrades them.

Runtime guarantees added in April 2026 hardening:

1. Every non-dry orchestrator dispatch records `model_requested`, `model_resolved`,
     resolved backend, temperature, and token budget in artifact metadata.
2. Every non-dry dispatch persists a prompt packet under `artifacts/prompts/*.prompt.json`
     and records a canonical `prompt_packet_sha256` in artifact frontmatter and manifest.
3. Stages after `brief` require an initialized workspace; missing baseline files are
     auto-materialized (`README.md`, `input_files/data_description.md`) with stage-specific
     additions for novelty/results/paper/referee (`literature.md`, `citation_evidence.md`)
     and prove (`proof_obligations.md`).

See:
- `protocol/orchestrator-contract.md` for the full orchestrator specification
- `protocol/agent-teams.md` §Orchestrator Integration for the stage-to-role mapping

## 1.7 Einstein Arena Integration Hardening (April 2026)

The Einstein Arena extraction and API surfaces are now treated as first-class bounded
runtime contracts.

Operational additions:

1. `scripts/einstein_arena_adapter.py` now exposes bounded retry controls on all API actions:
     - `--timeout`
     - `--max-retries`
     - `--retry-backoff`
     and retries transient classes (`429`, `502`, `503`, `504`, plus retryable network timeouts).
2. `scripts/import_einstein_arena.py` now uses header-driven table parsing, so README tables with reordered or extra columns continue to parse as long as required columns are present.
3. Slug aliasing is externalized to `registry/collections/einstein-arena-aliases.yaml`, eliminating hardcoded registry mapping edits for every upstream rename.
4. The parser now accepts multiple problem-cell formats (Markdown links, HTML anchors, and plain-text fallback slug inference) to reduce silent ingestion failure when upstream formatting drifts.

Verification policy:

- Keep importer and adapter contract tests green in `tests/test_import_einstein_arena.py` and `tests/test_einstein_arena_adapter.py`.
- Do not treat benchmark extraction as canonical truth: canonical OMEGA records remain under `registry/domains/*.yaml`.

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

### 2.2.1 Canonical vs Overlay Records

- `registry/domains/*.yaml` are the canonical, schema-validated problem records.
- `registry/collections/*.yaml` are quick-reference overlays for prize lists, notebooks, and named families; they may carry lighter metadata than domain records.
- When a collection entry corresponds to a canonical problem record, it should link back via `registry_id`.
- The taxonomy table is broader than the currently implemented collection files. A collection becomes operational only when a YAML file exists under `registry/collections/`.

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
**Profile:** Finding patterns, analogies, or structural similarities across known results could yield new approaches. Requires mathematical intuition that LLMs may partially possess. When a target theorem and a classical reduction template already exist, this tier can also include conversation-auditable proof search.
**Examples:** Connections between different conjectures, suggesting proof strategies by analogy, identifying when known techniques might apply.
**Tools:** LLM reasoning, literature search, analogy engines, knowledge graphs.
**Agent role:** Literature survey, cross-domain insight generation, obligation discovery, conjecture refinement.

### T4 — Structural (amenability: 1–3)
**Profile:** Deep algebraic, geometric, or topological reasoning required. Current AI may help co-develop structured arguments on scaffolded subproblems, but correctness-critical closure still belongs to humans or formal tooling.
**Examples:** Most algebraic geometry conjectures, Hodge conjecture, Yang–Mills existence.
**Tools:** Lean 4 / Coq for proof verification, Mathematica for symbolic computation, CAS / interval checkers for algebra-heavy obligations.
**Agent role:** Formalize known partial results, explore proof strategies, maintain proof obligations, verify proposed proofs.

### T5 — Foundational (amenability: 0–1)
**Profile:** Metamathematical, logical, or foundational issues. May be independent of standard axioms.
**Examples:** Large cardinal consistency, continuum hypothesis variants, P vs NP.
**Tools:** Proof assistants for independence proofs, forcing constructions.
**Agent role:** Literature survey, formalization of known results, exploration of axiom alternatives.

## 4. Agent Architecture

### 4.1 Agent Roles (Denario-inspired, locally adapted)

Following the Denario framework (arXiv:2510.26887), each research task employs a team of specialized agents:

| Agent | Role | Denario Mapping |
|-------|------|-----------------|
| **Librarian** | Literature search, bibliography, related work, novelty packet | Background / literature agents |
| **Analyst** | Problem analysis, triage, reductions, feasibility routing | Methodology / planner-adjacent agents |
| **Experimentalist** | Numerical experiments, computation, verification | Results / engineer + researcher chain |
| **Prover** | Formal proofs, Lean 4 / Coq, proof strategies | Local OMEGA extension beyond Denario |
| **Writer** | Paper generation, LaTeX, scientific writing | Paper writing agents |
| **Reviewer** | Quality control, referee report, blocking review | Referee / peer-review agents |

### 4.2 Workflow (CMBAgent deep_research-inspired)

Following CMBAgent's current repository guidance, OMEGA should prefer a **deep-research, context-carrying workflow** rather than the older `planning_and_control` path.

For citation hygiene, distinguish the repo's live operator surface from the paper surfaces: cite `arXiv:2507.07257` for the planning/control system and use `arXiv:2412.00431` only as the earlier cosmology precursor.

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

1. **BRIEF** — Planner/Librarian write `data_description.md` from the registry entry and define the bounded research question
2. **NOVELTY** — Librarian produces a literature and prior-results memo before any novelty claim is allowed; when novelty depends on related-work positioning, persist `literature.md`, `literature_graph.md`, and `citation_evidence.md`
3. **TRIAGE** — Analyst assigns AI tier, selects the route (`experiment-first`, `proof-first`, `survey-first`), and estimates compute risk
4. **PLAN** — Planner + Reviewer produce a bounded, restartable plan with explicit steps, allowed tools, stop conditions, and when useful a fixed-budget keep-or-discard experiment loop
5. **EXPERIMENT / PROVE** — Experimentalist or Prover executes one bounded step at a time; proof-first runs should maintain `proof_obligations.md` and iterate `generate -> referee -> repair` on load-bearing subclaims; execution success is tracked separately from scientific validity
6. **RESULTS** — Researcher-style synthesis writes the full result narrative that downstream paper-writing depends on; computational campaigns should persist an experiment ledger in `experiments/ledger.yaml`, while proof-first runs record verifier outcomes separately under `artifacts/prover-results/`
7. **PAPER** — Writer composes the scientific artifact from the persisted research state and may emit a companion presentation pack, but claim strength must stay aligned with the stored paper and evidence class
8. **REFEREE** — Reviewer attacks claims, novelty, reproducibility, limitation disclosure, and unresolved proof obligations
9. **PROMOTE / ARCHIVE** — Planner either closes the investigation or schedules another pass; only then is the folder moved to `research/completed/`

### 4.4 Adopt / Extend / Reject Decisions from Donor Extraction

#### Adopt

- Modular stage separation: `idea -> novelty -> methods -> results -> paper -> referee`
- Project-folder contract with persisted markdown artifacts and plots
- Step-by-step execution with restartability and context carryover
- Structured plan artifacts instead of prose-only planning
- Distinction between **code executed successfully** and **scientific step completed**
- Referee stage as a first-class artifact, not an afterthought
- Versioned proof drafts plus bounded `generate -> referee -> repair` loops for proof-first work

#### Extend

- Add a dedicated **Prover** lane for Lean 4 / Coq / symbolic proof work
- Make the registry and triage matrix the first-class scheduler for thousands of problems
- Add theorem/result provenance, reproducibility manifests, and evidence classes
- Adapt `data_description.md` from generic dataset descriptions to mathematical problem briefs
- Add explicit proof-obligation packets and autonomy/novelty gradation for LLM-assisted proof work

#### Reject

- Unqualified claims of full human-free scientific reliability
- Domain-specific astrophysics assumptions from Denario examples
- Deprecated `planning_and_control` as the default orchestration path
- Any implication that an accepted workshop paper proves parity with the best human mathematical research
- Press-release autonomy language as a substitute for proof verification

### 4.5 Per-Problem Workspace Contract

Each active problem should live in its own isolated workspace under `research/active/<problem-id>/`.

Recommended layout:

```text
research/active/<problem-id>/
├── input_files/
│   ├── data_description.md
│   ├── literature.md
│   ├── literature_graph.md
│   ├── citation_evidence.md
│   ├── idea.md
│   ├── methods.md
│   ├── proof_obligations.md
│   ├── results.md
│   ├── referee.md
│   └── plots/
├── planning/
├── control/
├── paper/
├── presentation/
├── experiments/
│   └── ledger.yaml
├── reproducibility.md
└── artifacts/
     ├── run-manifest.yaml
     ├── evidence-bundle.yaml
     └── prover-results/
```

Use `python scripts/scaffold_problem.py <problem-id> --title "..."` to create this structure.

Proof-first lanes may additionally stage a versioned Lean project under `proof/lean/` by copying `templates/lean-starter/`; see `protocol/lean-bootstrap.md`.

### 4.6 Bounded Runner Surface

OMEGA now ships a **bounded local runner CLI** for workspace hygiene. It does not solve math problems autonomously; it only manages the reproducibility surfaces that the protocol already requires.

Primary commands:

```bash
python scripts/omega_runner.py start <problem-id> --route experiment-first --agent experimentalist --description "bounded search"
python scripts/omega_runner.py finish <problem-id> <run-id> --status completed --verdict positive --artifact artifacts/search.log:log
python scripts/omega_runner.py proof-result <problem-id> <run-id> --claim-label "candidate theorem" --claim-class theorem --status draft --verifier lean4 --toolchain leanprover/lean4:v4.29.0 --verifier-command "lake env lean artifacts/candidate.lean" --source-entry artifacts/candidate.lean --artifact artifacts/candidate.lean:source
python scripts/omega_runner.py evidence-bundle <problem-id>
python scripts/omega_runner.py bootstrap-lean <problem-id>
python scripts/generate_experiment_index.py
```

This surface guarantees only:

- run lifecycle management in `experiments/ledger.yaml`
- automatic checksum enrichment for recorded run artifacts
- `artifacts/evidence-bundle.yaml` generation for per-problem machine-actionable evidence state
- `artifacts/prover-results/<run-id>.yaml` emission and linkage
- regeneration of `research/active/experiment-index.yaml`
- copying `templates/lean-starter/` into `proof/lean/`

It does **not** yet provide a CAS bridge, Lean build orchestration, literature crawling, or autonomous planner execution.

### 4.7 Evidence Governance and Research Object Packaging

Two protocol pages now govern claim-bearing outputs:

- `protocol/evidence-governance.md` defines OMEGA evidence classes, confidence labels, and downgrade rules.
- `protocol/research-object-packaging.md` defines the current local research-object contract and how it maps to future FAIR Signposting, RO-Crate, and DataCite export surfaces.

The operative rule is simple: treat the local workspace as the canonical research object first; external packaging, decks, and publication claims must be generated from those stored artifacts, not from memory or hype.

### 4.8 Runtime And Language Boundary

OMEGA is an explicitly **Python-first runtime** with bounded polyglot edges.

- Use Python for orchestration, registry work, ledgers, evidence bundles, execution adapters, and future experiment-query surfaces.
- Use Lean 4 as the trusted proof substrate, not as a general orchestration language.
- Use TypeScript only when bridging back into parent MicroPhoenix MCP, UI, or governance surfaces.
- Defer Rust until OMEGA measures a concrete bottleneck that Python cannot address cleanly.

See `protocol/runtime-language-strategy.md` for the active decision, evidence base, and phased roadmap.

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

OMEGA remains standalone. It now includes a bounded local runner for ledger and prover-result hygiene, but the heavier execution adapters below are still planned or optional.

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
| Elicit / Scite / Litmaps / Inciteful / ResearchRabbit / Connected Papers / SciSpace | literature discovery, citation topology, novelty support | optional external support; collapse outputs into local literature artifacts |
| open-researcher / Vane donor patterns | bounded local search-routing doctrine | donor-derived workflow guidance, not vendored runtime |
| Paper2Slides / WorkPPT | presentation-pack generation | optional companion-output support |
| MathGPT Pro / Mathos AI / Examful | explanation and tutoring only | supplemental, non-claim-bearing |

## 8. Quality Gates

Before any OMEGA result is published:

- [ ] **Correctness check**: Independent verification of all computations
- [ ] **Reproducibility**: All code and data available, environment documented
- [ ] **Literature check**: No prior publication of the same result
- [ ] **Formatting**: Standard LaTeX, proper citations, clear exposition
- [ ] **Self-assessment**: Honest evaluation of limitations and what was NOT achieved
- [ ] **Peer review simulation**: Reviewer agent with adversarial stance
- [ ] **Execution ≠ validity**: successful code execution alone must not mark a research step complete
- [ ] **Uncertainty disclosure**: experimental claims include error bars, sensitivity limits, or a clear statement of missing uncertainty analysis
- [ ] **Novelty gating**: no novelty claim without a stored literature packet and collision check
- [ ] **Citation parity**: novelty-heavy claims preserve supporting and contrasting citations when available
- [ ] **Ledger retention**: computational campaigns preserve an experiment ledger or explain why they do not need one
- [ ] **Separation of proof / evidence / conjecture**: the final artifact must distinguish theorem, empirical finding, and speculative next step
- [ ] **Presentation parity**: slides or seminar decks do not overstate the stored paper or result artifact

## 9. Ethical Guidelines

1. **Honest attribution**: OMEGA results are AI-generated. Always state this clearly.
2. **No overclaiming**: Numerical evidence ≠ proof. Partial results ≠ complete solutions.
3. **Reproducibility**: Every result must be independently verifiable.
4. **Community respect**: Don't flood arXiv with trivial extensions. Batch results.
5. **Credit**: Cite all human work that OMEGA builds upon.
6. **Open source**: All tools, code, and data are open under MIT/CC-BY-4.0.
7. **No authorship laundering**: detector-bypass or AI-humanizer workflows are out of scope; disclose AI assistance explicitly instead.

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
