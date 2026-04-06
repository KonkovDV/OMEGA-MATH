# OMEGA — Open Mathematics Exploration by Generative Agents

> Изолированный standalone-репозиторий для мультиагентного исследования открытых математических проблем

## Миссия

Систематическое применение ИИ-агентов к тысячам нерешённых математических задач — от гипотезы Римана до проблемы усердного бобра — с целью:
1. **Каталогизации** всех открытых проблем в машиночитаемом формате
2. **Классификации** по доступности для ИИ-подходов
3. **Автоматической генерации** гипотез, доказательств и контрпримеров
4. **Публикации** результатов в формате научных статей

OMEGA не вендорит внешние исследовательские рантаймы напрямую. Репозиторий остаётся
полностью изолированным, но использует проверенные архитектурные паттерны из Denario,
CMBAgent и LSST DESC AI roadmap как доноры проектных решений.

## Canonical Planning Surfaces

- Current canonical roadmap: `research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md`
- 6-phase execution plan: `research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md`
- SOTA formal proving landscape: `research/OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md`
- SOTA bibliography: `research/OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md`
- Far-horizon speculative architecture: `research/OMEGA_HYPER_ARCHITECTURE_2076.md`
- Local proving and workstation stack: `research/OMEGA_LOCAL_WORKSTATION_VIBE_PROVING_STACK_2026_04_04.md`
- Formal assurance scope matrix: `research/OMEGA_ASSURANCE_SCOPE_MATRIX_2026_04_05.md`
- Market and source ledger: `research/OMEGA_MARKET_AND_SOURCE_LEDGER_2026_04_05.md`

## Research Intelligence Stack

OMEGA also tracks a small research-intelligence support layer for literature discovery,
workflow design, presentation packaging, and a verified local formal-math workstation stack.

- Open-source workflow donors: MiroThinker, open-researcher, Vane / Perplexica, autoresearch, Paper2Slides, create-llm
- Formal-math and vibe-proving evidence layer: arXiv:2602.18918, arXiv:2601.22401, arXiv:2602.10177, Numina-Lean-Agent, vibe-proving-with-llms, StarExec-ARC, Omni-MATH-2
- Local workstation prover stack: Lean 4, mathlib4, vscode-lean4, LLMLean, LeanCopilot, llmstep, LeanTool, UlamAI, Ollama, llama.cpp, vLLM, BFS-Prover-V2, DeepSeek-Prover-V2 (7B variant), Goedel-Prover
- Research-grade external support: Elicit, Scite, Litmaps, Inciteful, ResearchRabbit, Connected Papers, SciSpace
- Presentation helper: WorkPPT
- Tutor-only supplemental surfaces: MathGPT Pro / Mathos AI, Examful
- Explicitly excluded: detector-bypass and AI-humanizer workflows

See `protocol/research-intelligence-stack.md` for the receiver mapping and artifact rules, and `research/OMEGA_LOCAL_WORKSTATION_VIBE_PROVING_STACK_2026_04_04.md` for the local-stack synthesis.

> This list shows operationally promoted surfaces as of the April 2026 audit. For secondary and watchlist tools (Leanstral, ProofGym, etc.) and the reasoning behind each classification, see `research/OMEGA_LOCAL_WORKSTATION_VIBE_PROVING_STACK_2026_04_04.md`. Kimina-Prover was promoted to Tier-1 in the April 2026 SOTA update (see `research/OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md`).

## Архитектура

```
┌─────────────────────────────────────────────────────┐
│                   OMEGA Protocol                     │
├──────────┬──────────┬──────────┬────────────────────┤
│ Registry │ Triage   │ Research │ Publication        │
│ (каталог)│ (оценка) │ (работа) │ (статьи)           │
├──────────┴──────────┴──────────┴────────────────────┤
│      Agent Teams (Denario-inspired + CMBAgent control)│
├──────────┬──────────┬──────────┬────────────────────┤
│ Librarian│ Analyst  │ Prover   │ Writer             │
│ Agent    │ Agent    │ Agent    │ Agent              │
├──────────┴──────────┴──────────┴────────────────────┤
│              Compute & Verification Layer            │
│  Lean4 / Coq │ Python/SageMath │ LaTeX │ arXiv API  │
└─────────────────────────────────────────────────────┘
```

## Источники и SOTA

### Мультиагентные исследовательские системы

| Источник | Роль в проекте |
|----------|----------------|
| [Denario](https://github.com/AstroPilot-AI/Denario) (arXiv:2510.26887) | Донор модульной схемы `idea → novelty → methods → results → paper → referee`, файлового контракта проекта и paper/referee пайплайна |
| [CMBAgent](https://github.com/CMBAgents/cmbagent) (repo; arXiv:2507.07257, precursor arXiv:2412.00431) | Донор planning/control runtime; для operator guidance актуален `deep_research`, а не устаревающий `planning_and_control`; для paper-level citations следует опираться на `2507.07257`, а `2412.00431` трактовать как более ранний cosmology-specific precursor |
| [Agents4Science OpenReview](https://openreview.net/forum?id=LENY7OWxmN#discussion) | Подтверждает, что по крайней мере одна Denario-работа принята на workshop/conference уровне; reviews при этом смешанные и содержательные, а не безусловно восторженные |
| LSST DESC AI Roadmap (arXiv:2601.14235) | Донор требований к uncertainty quantification, validation, robustness, reproducibility и data/software infrastructure |

### AI для математики (SOTA April 2026)

| Источник | Роль в проекте |
|----------|----------------|
| FunSearch (Nature, Jan 2024; Romera-Paredes et al.) | LLM-guided evolutionary program search; new cap set upper bounds |
| AlphaProof (DeepMind, Jul 2024) | Solved 4/6 IMO 2024 problems via Lean 4 + RL; SOTA formal proving |
| AlphaGeometry 2 (DeepMind, Jul 2024) | IMO-level geometry theorem proving |
| LeanDojo / ReProver (arXiv:2306.15626, NeurIPS 2023) | LLM-based Lean 4 theorem prover; open-source |
| LeanCopilot (arXiv:2404.12534, NeuS 2025) | 74.2% proof step automation; ExternalGenerator API for BYOM; primary OMEGA integration surface |
| LLEMMA (arXiv:2310.10631, 2023) | Open math-specialized LLM (7B/34B), Proof-Pile-2 training |
| DeepSeek-Prover-V2 (arXiv:2504.21801, 2025) | 88.9% MiniF2F-test, 49/658 PutnamBench; subgoal decomposition 671B→7B; open-weight |
| Kimina-Prover (arXiv:2504.11354, 2025) | 80.7% MiniF2F pass@8192; whole-proof generation; open distilled 7B/1.5B |
| Process Advantage Verifiers (arXiv:2410.08146, 2024) | Step-level scoring for proof-search candidate ranking |
| FrontierMath (arXiv:2411.04872, Epoch AI, 2024) | Research-grade math benchmark; SOTA <2%; honest calibration surface |
| VUB vibe-proving case study (arXiv:2602.18918, 2026) | Consumer-LLM proof-search case with auditable transcripts, versioned drafts, and a human verification bottleneck |
| Gemini on Erdős problems (arXiv:2601.22401, 2026) | Semi-autonomous screening of 700 open-problem records; highlights novelty-collision and literature-rediscovery risk |
| Aletheia / autonomous math research (arXiv:2602.10177, 2026) | Long-horizon research-agent framing with autonomy and novelty gradation for math outputs |
| Numina-Lean-Agent (arXiv:2601.14027, 2026) | Open Lean-based formal-math agent; Putnam 12/12 claim plus Brascamp-Lieb formalization |
| Omni-MATH-2 / judge saturation (arXiv:2601.19532, 2026) | Warning that weak judges can mask real capability differences once models improve |
| Numina / AI-MO (2024–2025) | Open LLM math competition solving (AIMO Prize) |

### Данные и каталоги

| Источник | Роль в проекте |
|----------|----------------|
| Wikipedia: Открытые математические проблемы | Каталог 500+ проблем по 25+ разделам математики |
| OEIS (oeis.org) | Справочник целочисленных последовательностей |

## Current State

This directory is currently a **research seed with a bounded operator CLI**, not a full autonomous math-lab runtime.

What exists now:
1. A machine-readable registry of selected open problems
2. A triage queue ranked by AI amenability
3. Protocol docs for research, verification, and publication
4. A reference mapping for literature graphs, citation evidence, proof-obligation packets, experiment ledgers, and presentation packs
5. Initial agent-role configuration files
6. Collection indexes for Millennium, Hilbert, Landau, and Smale problem families
7. Registry maintenance scripts for validation and index generation
8. A bounded local runner surface for experiment ledgers, prover-result artifacts, experiment-index regeneration, and Lean starter bootstrapping
9. GitHub Actions CI for registry integrity checks, adapter tests, and Python package build
10. A standalone git repository boundary independent from the main MicroPhoenix runtime
11. Automatic checksum capture plus per-problem evidence bundles for completed run artifacts
12. A buildable Python package surface with installable CLI entrypoints for the OMEGA runtime
13. Execution adapters for Lean 4 (`omega-lean`), SAT/SMT solvers (`omega-solve`), and CAS (`omega-cas`)
14. A searchable experiment-history query surface (`omega-query`) over ledger and experiment-index data
15. A deterministic local workflow controller (`omega-workflow`) that materializes per-problem control state from registry triage and advances bounded stages without hand-editing YAML

What does not exist yet:
1. A full autonomous orchestration loop across planner, librarian, prover, and writer roles
2. Automated paper generation pipelines
3. Local adapters for literature-graph, citation-evidence, and presentation-pack services
4. LLM-backed proof search via LeanCopilot / DeepSeek-Prover integration (execution adapters are wired; model routing is not)

## Registry Maturity

- Canonical problem records live in `registry/domains/*.yaml` and are the schema-validated source of truth.
- Collection files under `registry/collections/*.yaml` are quick-reference overlays; when a canonical problem record exists, they should point back with `registry_id`.
- Current AI triage coverage is `60 / 239` problems (`25.1%`), so the queue is suitable for prioritized exploration, not for exhaustive balanced routing across the full registry.

## Isolation Status

This repository is intentionally isolated from the main MicroPhoenix application surface.

- Separate git history and CI under `math/`
- No runtime imports from `src/` or `tests/` of the parent project
- Protocols may reuse MicroPhoenix architectural ideas, but execution contracts live locally
- Generated registry artifacts are validated locally before any GitHub push

## Recommended Use

1. Read `PROTOCOL.md` for the full operating model.
2. Start from `registry/triage-matrix.yaml` to choose a first target.
3. Read `protocol/research-intelligence-stack.md` before novelty-heavy work, proof-first investigations, or publication prep.
4. Optionally install the local Python CLI surface with `python -m pip install -e .`.
5. Create a Denario-compatible research workspace with `python scripts/scaffold-problem.py <problem-id> --title "..."` or `omega-scaffold-problem ...` after editable install.
6. Materialize the local control state with `python scripts/omega-workflow.py triage <problem-id>` or `omega-workflow triage <problem-id>` after the workspace exists.
7. Inspect or advance the current workflow with `omega-workflow status <problem-id>` and `omega-workflow advance <problem-id> --outcome complete|block|resume|close`.
8. Open and close experiment runs with `python scripts/omega-runner.py start ...` and `python scripts/omega-runner.py finish ...` instead of hand-editing the ledger; these lifecycle commands now auto-sync `control/workflow-state.yaml` into the execution and results phases.
9. For proof-first work, start from `templates/lean-starter/` and `protocol/lean-bootstrap.md`, then persist verifier-visible outcomes with `python scripts/omega-runner.py proof-result ...`.
10. Regenerate the checksummed evidence view with `python scripts/omega-runner.py evidence-bundle <problem-id>` when needed; `finish` and `proof-result` already refresh it automatically.
11. Read `protocol/evidence-governance.md`, `protocol/research-object-packaging.md`, and `protocol/runtime-language-strategy.md` before extending the runtime or writing claim-bearing outputs.
12. Regenerate the active workflow-and-run summary with `python scripts/generate-experiment-index.py` when needed, or query it directly with `omega-query --global --stage plan` / `omega-query --global --blocked-only --format table`.
13. Use the files under `protocol/` to structure the investigation.
14. Use the files under `agents/` as role specs for future orchestration.
15. Query past experiment runs with `omega-query --problem <id>` or `omega-query --verdict positive` to find prior evidence before starting new work.
16. Check Lean files with `omega-lean check-file <file.lean>`, build Lean projects with `omega-lean build-project <dir>`, or emit structured results with `omega-lean run-command "<cmd>"`.
17. Solve SAT/SMT instances with `omega-solve smt "<z3-spec>"` or `omega-solve sat --clauses "[[1,2],[-1,3]]" --num-vars 3`.
18. Run CAS computations with `omega-cas simplify <expr>`, `omega-cas solve <equation>`, `omega-cas series <expr>`, or `omega-cas custom "result = ..."`.

## Структура проекта

```
math/
├── README.md                          # Этот файл
├── PROTOCOL.md                        # Полный протокол исследования
├── EXTRACTION_REPORT.md               # Источники и правила начальной экстракции
├── pyproject.toml                     # Python package surface for installable OMEGA CLI tools
│
├── registry/                          # Каталог открытых проблем
│   ├── schema.json                    # JSON Schema для записи о проблеме
│   ├── triage-matrix.yaml             # Приоритетная очередь по AI-доступности
│   ├── collections/
│   │   ├── hilbert-problems.yaml
│   │   ├── landau-problems.yaml
│   │   ├── millennium-prize.yaml
│   │   └── smale-problems.yaml
│   └── domains/
│       ├── algebra.yaml
│       ├── analysis.yaml
│       ├── combinatorics.yaml
│       ├── computer-science.yaml
│       ├── dynamical-systems.yaml
│       ├── game-theory.yaml
│       ├── geometry.yaml
│       ├── graph-theory.yaml
│       ├── model-theory.yaml
│       ├── number-theory.yaml
│       ├── other-domains.yaml         # DEPRECATED — split into dedicated files
│       ├── probability-theory.yaml
│       ├── set-theory.yaml
│       └── topology.yaml
│
├── scripts/                           # CLI tools and execution adapters
│   ├── scaffold-problem.py
│   ├── generate-index.py
│   ├── generate-experiment-index.py
│   ├── omega-runner.py
│   ├── omega_runner.py
│   ├── validate-registry.py
│   ├── experiment_query.py            # Searchable experiment-history queries
│   ├── lean_adapter.py                # Lean 4 CLI execution adapter
│   ├── solver_adapter.py              # SAT/SMT (Z3/PySAT) execution adapter
│   ├── cas_adapter.py                 # CAS (SymPy/SageMath) execution adapter
│   ├── omega_workflow.py              # Deterministic workflow/FSM controller
│   ├── query-experiments.py           # Wrapper → experiment_query.py
│   ├── lean-check.py                  # Wrapper → lean_adapter.py
│   ├── solve.py                       # Wrapper → solver_adapter.py
│   └── omega-workflow.py              # Wrapper → omega_workflow.py
│
├── tests/                             # Standalone Python test suite
│   ├── test_omega_runner.py
│   ├── test_python_surface.py
│   ├── test_experiment_query.py
│   ├── test_lean_adapter.py
│   ├── test_solver_adapter.py
│   ├── test_cas_adapter.py
│   └── test_omega_workflow.py
│
├── templates/                         # Публикационные и proving starter surfaces
│   ├── reproducibility-manifest.md
│   ├── short-note.tex
│   ├── survey-memo.tex
│   └── lean-starter/
│       ├── README.md
│       ├── lean-toolchain
│       ├── lakefile.lean
│       └── OmegaWorkbench/
│
├── protocol/                          # Операционные документы исследования
│   ├── agent-teams.md
│   ├── amenability-rubric.md
│   ├── cas-execution-adapter.md        # CAS adapter contract
│   ├── experiment-ledger-spec.md
│   ├── evidence-governance.md
│   ├── lean-bootstrap.md
│   ├── lean-execution-adapter.md       # Lean 4 adapter contract
│   ├── operator-runbook.md
│   ├── publication-workflow.md
│   ├── prover-result-contract.md
│   ├── research-intelligence-stack.md
│   ├── research-object-packaging.md
│   ├── runtime-language-strategy.md
│   ├── solver-execution-adapter.md     # SAT/SMT adapter contract
│   ├── triage-matrix.md
│   └── verification-pipeline.md
│
├── agents/                            # Конфигурации ролей
│   ├── analyst.yaml
│   ├── experimentalist.yaml
│   ├── librarian.yaml
│   ├── planner.yaml
│   ├── prover.yaml
│   ├── reviewer.yaml
│   ├── team.yaml
│   └── writer.yaml
│
└── research/
    ├── OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md
    ├── OMEGA_ASSURANCE_SCOPE_MATRIX_2026_04_05.md
    ├── OMEGA_COMPETITIVE_ANALYSIS.md
    ├── OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md
    ├── OMEGA_HYPER_ARCHITECTURE_2076.md
    ├── OMEGA_HYPER_DEEP_AUDIT_2026_04_04.md
    ├── OMEGA_INDIE_GTM_PLAYBOOK.md
    ├── OMEGA_INTERNAL_EVIDENCE_PACKET_2026_04_05.md
    ├── OMEGA_INVESTMENT_AND_MONETIZATION.md
    ├── OMEGA_LOCAL_WORKSTATION_VIBE_PROVING_STACK_2026_04_04.md
    ├── OMEGA_MARKET_AND_SOURCE_LEDGER_2026_04_05.md
    ├── OMEGA_OPEN_SOURCE_STACK.md
    ├── OMEGA_PROJECT_OVERVIEW_AND_NAMING.md
    ├── OMEGA_SEED_NARRATIVE_2026_04_05.md
    ├── OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md
    ├── OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md
    ├── OMEGA_UNICORN_PITCH_DECK.md
    ├── OMEGA_VIBE_PROVING_HYPERDEEP_REPORT_2026_04_04.md
    ├── active/README.md
    └── completed/README.md
```

## Planned Next Surface

Likely next additions (aligned with the 6-Phase Execution Plan):

### Phase 1: Pipeline Closure (immediate priority)
1. Connect `lean_adapter.py` to real `lake build` with pinned mathlib toolchain
2. Write integration tests for `solver_adapter.py` with concrete problem instances (Erdős–Straus, Kobon triangles)
3. Create `scripts/literature_adapter.py` with Semantic Scholar API retrieval (100 req/sec, free tier)
4. Execute full lifecycle on 3 Tier 1 problems with real evidence bundles

### Phase 2: LLM-Backed Proof Search
5. Create `scripts/model_router.py` routing to Ollama + DeepSeek-Prover-V2-7B / LeanCopilot ExternalGenerator / vLLM
6. Implement bounded proof-repair loop (generate → verify → enrich → retry, max 64 iterations)
7. Implement two-level subgoal decomposition (72B+ decomposes → local 7B solves)
8. Produce first neural-generated Lean 4 proof with zero remaining `sorry`

### Phase 3: Literature and Novelty Verification
9. Add arXiv API supplement for fresh preprint search
10. Add machine-readable novelty packet generator per problem
11. Add mandatory anti-rediscovery gate at TRIAGE → PLAN workflow transition

### Phase 4–6: Orchestration, Publication, Formal Assurance
12. Multi-agent orchestration (Librarian → Analyst → Experimentalist → Prover → Writer → Reviewer)
13. LaTeX generation from stored artifacts with audit trail
14. Post-quantum cryptography formal assurance wedge (NIST FIPS 203/204/205)

See `research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md` for complete task specifications with evidence gates and academic grounding.

## Лицензия

MIT (протокол и инструментарий) — данные и результаты исследований публикуются под CC-BY 4.0.
