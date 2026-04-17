# OMEGA Extraction Report

Date: 2026-04-16
Status: seed + research-intelligence expansion + FrenzyMath extraction complete

## Scope

This workspace seeds an OMEGA research surface for open mathematics:

- a machine-readable registry of selected open problems
- a triage matrix ranked by AI amenability
- operational protocol docs for agent-led investigation
- initial team configuration files for research orchestration

## Sources Used

1. Wikipedia, List of unsolved problems in mathematics
   Role: master taxonomy and initial problem inventory
   Snapshot basis: page content fetched on 2026-04-04
2. Denario, arXiv:2510.26887
   Role: modular scientific-agent runtime donor (idea, novelty, method, results, paper, referee)
3. CMBAgent, arXiv:2507.07257 (Xu et al., 2025)
   Role: planner-executor control donor for scientific workflows
4. CMBAgent GitHub repository
   Role: current implementation evidence; confirms `deep_research` supersedes legacy `planning_and_control`
5. OpenReview `LENY7OWxmN` (Agents4Science 2025)
   Role: external evaluation evidence for one Denario-generated paper; confirms acceptance and mixed reviewer assessments
6. LSST DESC AI Roadmap, arXiv:2601.14235
   Role: scientific-governance donor for UQ, robustness, reproducibility, validation, and infrastructure requirements
7. Verbeken et al., arXiv:2602.18918 + VUB press release + SciTechDaily summary
   Role: auditable vibe-proving case study; used to separate paper-backed workflow lessons from press framing
8. Feng et al., arXiv:2601.22401 and arXiv:2602.10177
   Role: autonomy-gradation and literature-collision evidence for AI-assisted mathematics research
9. Liu et al., arXiv:2601.14027 + `project-numina/numina-lean-agent`
   Role: open formal-math agent donor for future Lean/Prover lane design
10. `jacopotagliabue/vibe-proving-with-llms`
    Role: minimal verifier-plus-RL reference for proof-checker-backed training loops
11. `StarExecMiami/StarExec-ARC`
    Role: ATP containerization and benchmarking infrastructure donor
12. Ballon et al., arXiv:2601.19532
    Role: judge-reliability warning surface for proof and benchmark evaluation
13. Breakthrough milestone papers checked in this pass
    Role: historical grounding for 2024-2025 math closures and claims normalization (`2405.03599`, `2405.03648`, `2409.07051`, `2409.08670`, `2409.09856`, `2209.04736`, `2502.17655`, `2503.01800`)
14. `togethercomputer/EinsteinArena-new-SOTA` (README snapshot, April 2026)
   Role: benchmark donor for objective-aligned score tables, public baseline comparisons, and verifier-first notebook patterns
15. Ju et al., arXiv:2604.03789
   Role: primary evidence for dual-agent conjecture-resolution with formal verification (`Rethlas + Archon`)
16. `frenzymath/Rethlas`
   Role: informal-generation and verifier-loop donor (problem markdown -> blueprint -> verification contract)
17. `frenzymath/Archon`
   Role: project-scale formalization orchestrator donor (plan/prover/review staging with Lean workflow controls)
18. `frenzymath/Anderson-Conjecture`
   Role: reproducibility donor for statement/proof separation and comparator-based verification envelope
19. FrenzyMath conjecture post + CRC Substack commentary
   Role: secondary narrative/context surfaces; not used as primary authority over paper/repo evidence

## What Was Extracted

- domain-level registry files under math/registry/domains/
- collection indexes for Millennium, Hilbert, Landau, and Smale problem families
- Einstein Arena benchmark collection under `registry/collections/einstein-arena-benchmarks.yaml`
- a global triage queue under math/registry/triage-matrix.yaml
- a generated registry index under math/registry/index.yaml
- protocol docs under math/protocol/
- agent configuration files under math/agents/
- maintenance scripts under math/scripts/
- Einstein Arena importer script: `scripts/import_einstein_arena.py`
- Optional Einstein solution snapshot extraction under `research/benchmarks/einstein-arena/<problem>/solutions/` when a local donor checkout is provided
- a buildable Python packaging surface under `math/pyproject.toml`
- a dated evidence report under `math/docs/research/OMEGA_VIBE_PROVING_HYPERDEEP_REPORT_2026_04_04.md`
- a dated FrenzyMath extraction report under `math/docs/research/OMEGA_FRENZYMATH_EXTRACTION_2026_04_16.md`

## Current Coverage Level

The registry is intentionally curated rather than exhaustive.

Included now:
- highest-signal flagship problems across major domains
- computationally amenable problems prioritized for early agent work
- representative foundational problems for long-horizon tracking

Not yet complete:
- full one-to-one transcription of every Wikipedia entry
- notebook collections split into separate files
- problem provenance beyond seed-level references
- formal theorem-prover encodings

## Extraction Rules

- Problem statements were normalized into concise paraphrases.
- AI triage is based on current practical amenability, not prestige.
- Open, partially resolved, and historically disproved items are labeled distinctly where needed.
- The registry prefers stable identifiers and short problem summaries over encyclopedic detail.
- External donor claims are only adopted when backed by repository code, paper text, or review records.
- Denario and CMBAgent are treated as architectural donors, not as direct runtime dependencies of OMEGA.

## Supplemental Donor Extraction (April 2026)

### Denario — Adopt / Extend / Build

- **Adopt**: modular research stages, project-folder artifact contract, paper/referee separation, restartable draft generation
- **Extend**: adapt `data_description.md` from dataset briefs to mathematical problem briefs; add a Prover lane and theorem evidence model
- **Build locally**: registry-driven scheduler, triage engine, and math-specific reproducibility manifests inside this standalone repo

### CMBAgent — Adopt / Extend / Build

- **Adopt**: step-by-step planning/control, structured plan artifacts, distinction between execution status and step completion, context carryover semantics
- **Extend**: replace domain-specific astrophysics context with math registry + theorem/proof context
- **Build locally**: repository-local scaffolding and future runners instead of vendoring the full CMBAgent runtime

### LSST DESC — Governance Rules Imported

- uncertainty quantification must be explicit for experimental claims
- robustness to distribution shift and implementation drift matters even in scientific prototypes
- validation, reproducibility, and software/data infrastructure are first-class, not post hoc clean-up

## Research-Intelligence Expansion (April 2026)

### Open-source workflow donors mapped into OMEGA

Validated as architectural donors for this standalone repo:

- MiroThinker: bounded context retention, trajectory logging, benchmark-contamination awareness
- open-researcher: metadata-first literature discovery, selective scraping, recursive continuation
- Vane / Perplexica: source and focus routing before search, privacy-first meta-search posture
- autoresearch: fixed-budget keep-or-discard experiment loops plus ledger discipline
- Paper2Slides: staged paper-to-slides pipeline for companion presentation artifacts
- create-llm: scaffold topology and generated starter-surface design for workflow packaging

### External services classified for reference use

Research-grade support:

- Elicit
- Scite
- Litmaps
- Inciteful
- ResearchRabbit
- Connected Papers
- SciSpace

Supplemental only:

- WorkPPT for presentation help
- MathGPT Pro / Mathos AI and Examful as tutor-only surfaces

Explicitly rejected for research-integrity reasons:

- detector-bypass tools
- AI-humanizer workflows
- authorship-obfuscation utilities

Unverified or inaccessible during the April 2026 pass:

- Eaisly AI
- Doco

### OMEGA receiver surfaces created by this expansion

- `input_files/literature_graph.md`
- `input_files/citation_evidence.md`
- `input_files/proof_obligations.md`
- `experiments/ledger.yaml`
- `artifacts/evidence-bundle.yaml`
- `artifacts/prover-results/<run-id>.yaml`
- `presentation/`

These are local contracts only. OMEGA still does not vendor external runtimes or service SDKs.

## Vibe-Proving and Formal-Math Expansion (April 2026)

### Verified evidence adopted into OMEGA

- arXiv:2602.18918 confirms a consumer-LLM `generate -> referee -> repair` workflow with transcript-linked auditability and human correctness-critical closure.
- arXiv:2601.22401 and arXiv:2602.10177 confirm that autonomy and novelty must be graded and that literature collision is a first-class risk in AI-assisted mathematics.
- arXiv:2601.14027 plus the Numina repo confirm that open formal-math agent systems now exist as realistic design references for Lean-first proving.
- arXiv:2601.19532 confirms that weak judges can become the bottleneck once model capability rises.

### Adopt / Extend / Reject

- **Adopt**: explicit proof obligations, versioned drafts, bounded referee passes, parallel patch search, and Lamport-style dependency exposure.
- **Extend**: local `proof_obligations.md` receiver surface plus future autonomy/novelty metadata in manifests.
- **Reject**: press-release autonomy phrasing, judge-only proof verification, and unverified ecosystem claims that cannot be backed by primary sources.

## FrenzyMath Conjecture-Resolution Extraction (April 2026)

### Verified donor package

- `arXiv:2604.03789` (primary paper)
- `frenzymath/Rethlas` (informal reasoning + verification loop implementation)
- `frenzymath/Archon` (project-level Lean formalization orchestrator)
- `frenzymath/Anderson-Conjecture` (open formalization artifact and comparator verification contract)
- FrenzyMath/CRC pages as secondary explanatory surfaces

### Extraction decisions

- **Adopt**: informal/formal lane split, strict verifier verdict contract, statement/proof trust separation.
- **Extend**: run-scoped memory channels and stage observability in OMEGA artifacts.
- **Build**: optional independent-kernel cross-check lane for high-assurance proof outputs.
- **Reject**: unsafe unattended execution defaults and commentary-only capability claims.

Detailed mapping is recorded in:

- `docs/research/OMEGA_FRENZYMATH_EXTRACTION_2026_04_16.md`

## Known Gaps

1. Erdős and notebook-style collections are not yet split into dedicated collection YAML files.
2. Partial-results and source references remain sparse outside the highest-priority T1 entries.
3. A bounded local runner now exists for ledger lifecycle, artifact checksum capture, evidence-bundle emission, prover-result emission, experiment-index regeneration, and Lean starter bootstrapping, but it is still an operator CLI rather than a full autonomous execution layer.
4. No formal theorem-prover runner or Lean/Coq execution adapter exists yet beyond the current bootstrap and result-contract management.
5. `proof_obligations.md` is now a local contract, but there is still no CAS or Lean bridge to discharge those obligations mechanically.
6. Python is now formalized as the primary OMEGA runtime, but the query and execution layers still need to be built on top of that choice.

## Recommended Next Additions

1. ~~Split grouped domains into dedicated files~~ — ✅ Done (April 2026): computer-science, set-theory, probability-theory, game-theory, model-theory
2. ~~Add collection indexes for Hilbert, Landau, and Smale problems~~ — ✅ Done (April 2026)
3. ~~Introduce a registry index file with coverage statistics~~ — ✅ Done: registry/index.yaml (now generated)
4. ~~Add a bounded local runner for experiment ledgers and prover-result artifacts~~ — ✅ Done: `scripts/omega_runner.py` and `scripts/generate_experiment_index.py`
5. ~~Add local adapters for literature-graph capture and citation-evidence collation~~ — ✅ Done: `scripts/literature_adapter.py` + `protocol/literature-adapter.md`
6. Add export-grade research-object emitters built from the local evidence bundle.
7. ~~Add a paper template, reproducibility manifest~~ — done: `templates/short-note.tex`, `templates/survey-memo.tex`, and `templates/reproducibility-manifest.md` exist; presentation-pack generator still needed.
8. Add an Erdős problems collection (~50 problems, highest community activity) and additional benchmark-oriented collections beyond Einstein Arena.
9. Wire the Lean starter and prover-result contract into an actual proof runner or CAS closure lane for algebra-heavy `proof_obligations.md` workflows.
10. Build the next Python-first layers: searchable experiment history, Lean/CAS execution adapters, and packaging-aware CLI distribution.

## Output Intent

This extraction is designed to support actual research automation, not just documentation. The docs and YAML files are now consumed by the bounded local runner substrate and are structured to support future orchestration code, execution adapters, or agent runners.
