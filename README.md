# OMEGA — Open Mathematics Exploration by Generative Agents

> Изолированный standalone-репозиторий для мультиагентного исследования открытых математических проблем

[![Validate OMEGA Registry](https://github.com/KonkovDV/OMEGA-MATH/actions/workflows/validate.yml/badge.svg)](https://github.com/KonkovDV/OMEGA-MATH/actions/workflows/validate.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## TL;DR

- **Что это:** local-first платформа для AI-assisted math research с реестром задач, triage, оркестрацией агентов и evidence governance.
- **Что уже работает:** bounded execution pipeline, experiment ledgers, SHA-256 evidence bundles, Einstein Arena bridge, schema-валидация артефактов, тестовый контур `225` passing tests.
- **Чего пока нет:** production-grade автономного закрытия proof-first цикла без оператора (формально верифицированные результаты требуют ручного/итеративного контроля).

## Release Status — v0.6.0 (2026-04-16)

- Закрыт блокер из Hyper-Deep Audit: флагманский execution tier снова в зелёном статусе.
- `tests/test_flagship_experiments.py` и `tests/test_registry_e2e.py` проходят без падений.
- Полный тестовый прогон (`pytest -q`) проходит целиком.

## Latest Update (2026-04-17)

- Runtime: добавлен dual-lane маршрут `plan -> experiment -> prove -> results` в оркестраторе для совместного неформального и формального контуров.
- Proof governance: для prove-стадий и claim-bearing prover results теперь обязательно используется `input_files/statement_spec.md` (жёсткое statement/proof separation).
- Prover lifecycle: расширен статусный контракт `draft -> verifier-checked -> formally-checked` с явными promotion gates в prover-result артефактах.
- Failure observability: добавлен run-level канал `control/failure-patterns.jsonl`, который фиксирует stagnation/repair события для bounded retry анализа.
- Lean execution safety: адаптер поддерживает sandbox policy `off|auto|required` с явной фиксацией sandbox-метаданных в результатах.
- Extraction/docs: интегрирован FrenzyMath donor package (`Rethlas`, `Archon`, `Anderson-Conjecture`, arXiv:2604.03789) с evidence-class mapping.
- Validation snapshot: `pytest -q` = `225 passed`; `agent:preflight:code` = APPROVED.

## Quick Start (10 Minutes)

```bash
git clone https://github.com/KonkovDV/OMEGA-MATH.git
cd OMEGA-MATH
python -m pip install -e .[all]
python scripts/validate_registry.py
python scripts/scaffold_problem.py erdos-straus --title "Erdos-Straus Conjecture"
python scripts/omega_workflow.py triage erdos-straus
python scripts/agent_orchestrator.py run erdos-straus --stage plan --dry-run
```

For live dispatches, set model credentials first (for example `DEEPSEEK_API_KEY`) and then run `omega-orchestrate` without `--dry-run`.

## Миссия

Систематическое применение ИИ-агентов к тысячам нерешённых математических задач — от гипотезы Римана до проблемы усердного бобра — с целью:
1. **Каталогизации** всех открытых проблем в машиночитаемом формате
2. **Классификации** по доступности для ИИ-подходов
3. **Автоматической генерации** гипотез, доказательств и контрпримеров
4. **Публикации** результатов в формате научных статей

OMEGA не вендорит внешние исследовательские рантаймы напрямую. Репозиторий остаётся
полностью изолированным, но использует проверенные архитектурные паттерны из Denario,
CMBAgent и LSST DESC AI roadmap как доноры проектных решений.

## Quick Start

1. Install the runtime surface:

```bash
python -m pip install -e .[all]
```

2. Validate repository integrity (registry + workspace artifact contracts + release metadata sync):

```bash
omega-validate-registry
omega-verify-version-sync
```

3. Initialize one problem workspace and deterministic workflow state:

```bash
omega-scaffold-problem erdos-straus --title "Erdos-Straus Conjecture"
omega-workflow triage erdos-straus
```

4. Dry-run orchestrator prompts before live calls:

```bash
omega-orchestrate run erdos-straus --stage plan --dry-run
```

5. Prefer local prover routing (Goedel-Prover-V2-32B via vLLM profile):

```bash
omega-orchestrate run erdos-straus --stage prove --prefer-local
```

## Help and Support

- Operator procedures: `protocol/operator-runbook.md`
- Orchestrator runtime contract: `protocol/orchestrator-contract.md`
- Lean bootstrap and proving workflow: `protocol/lean-bootstrap.md`
- Evidence and claim policy: `protocol/evidence-governance.md`

## Canonical Planning Surfaces

- Current canonical roadmap: `research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md`
- 6-phase execution plan: `research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md`
- SOTA formal proving landscape: `research/OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md`
- SOTA bibliography: `research/OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md`
- SOTA landscape update (April 13): `research/OMEGA_SOTA_LANDSCAPE_UPDATE_2026_04_13.md`
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

## Flagship Experimental Tracks

OMEGA is now concretely prepared around three Tier-1 flagship workspaces under `research/active/`:

| Problem | Current executable phase surface | Primary script |
|---------|----------------------------------|----------------|
| Erdős–Straus | Phase 1 covering analysis + Phase 2 parametric decomposition | `research/active/erdos-straus/experiments/phase1_covering.py`, `phase2_parametric.py` |
| Kobon triangles | Phase 1 arrangement search | `research/active/kobon-triangles/experiments/phase1_pseudoline_enum.py` |
| Thomson problem | Phase 1 multi-start optimization + Phase 2 basin-hopping + Phase 3 numerical certification scaffold | `research/active/thomson-problem/experiments/phase1_multistart.py`, `phase2_basin_hopping.py`, `phase3_certify.py` |

Planned later phases remain documented in each problem's `planning/attack_plan.md`, but only the executable phase surface above should be treated as run-ready today.

For VS Code / Copilot usage inside this standalone repo, use the workspace customizations under `.github/agents/`, `.github/prompts/`, and `.github/skills/`.

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
16. LeanCopilot-compatible external bridge server (`omega-leancop-bridge`) for BYOM tactic generation over OpenAI-compatible endpoints
17. Verifier-guided proof repair loop (`omega-proof-repair`) with bounded iterative retries and Lean feedback incorporation
18. Release metadata guard (`omega-verify-version-sync`) to enforce pyproject/CITATION/PROTOCOL version consistency

What does not exist yet:
1. Automated paper generation pipelines (templates exist; writer agent can draft, but no end-to-end LaTeX compilation)
2. Local adapters for literature-graph, citation-evidence, and presentation-pack services
3. LLM-backed proof search via LeanCopilot / DeepSeek-Prover integration (execution adapters and model routing are wired; the LeanCopilot ExternalGenerator bridge is not)

Newly added in v0.5.0:
1. LLM-backed agent orchestrator (`omega-orchestrate`) supporting 7-role dispatch, 8-stage pipeline execution, multi-API routing (OpenAI, Anthropic, LiteLLM, Ollama), and dry-run mode
2. Standalone evidence verification CLI (`omega-verify-evidence`) for computing and auditing SHA-256 evidence bundles
3. End-to-end integration test coverage for the full pipeline (brief → experiment → results → evidence bundle)
4. Model router (`omega-model-router`) with declarative role-to-model profiles, tier-aware routing, fallback chains, and LLM backend health checks

Hardened in April 2026 updates:
1. Orchestrator prompt-packet traceability: each non-dry dispatch now persists full prompt packets under `artifacts/prompts/*.prompt.json` and records `prompt_packet_sha256` in artifact metadata and manifest entries.
2. Stage prerequisites are now enforced: all post-brief stages require an initialized workspace and auto-materialize baseline files (`README.md`, `input_files/data_description.md`) plus stage-specific literature/proof placeholders.
3. Dispatch metadata now includes requested vs resolved model, backend, temperature, and token budget, so evidence bundles capture full routing context.
4. Model router local prover profile now targets `goedel-prover-v2-32b` (vLLM) with fallback to `deepseek-prover-v2:7b`.
5. Einstein Arena PoW registration path includes explicit timeout/progress controls (`--pow-timeout`, `--pow-progress-interval`).

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
4. Install the local Python CLI surface with `python -m pip install -e .` for registry-only or protocol work, or `python -m pip install -e .[all]` for the active research tracks and experiment scripts.
5. Create a Denario-compatible research workspace with `python scripts/scaffold_problem.py <problem-id> --title "..."` or `omega-scaffold-problem ...` after editable install.
6. Materialize the local control state with `python scripts/omega_workflow.py triage <problem-id>` or `omega-workflow triage <problem-id>` after the workspace exists.
7. Inspect or advance the current workflow with `omega-workflow status <problem-id>` and `omega-workflow advance <problem-id> --outcome complete|block|resume|close`.
8. Open and close experiment runs with `python scripts/omega_runner.py start ...` and `python scripts/omega_runner.py finish ...` instead of hand-editing the ledger; these lifecycle commands now auto-sync `control/workflow-state.yaml` into the execution and results phases.
9. For proof-first work, start from `templates/lean-starter/` and `protocol/lean-bootstrap.md`, then persist verifier-visible outcomes with `python scripts/omega_runner.py proof-result ...`.
10. Regenerate the checksummed evidence view with `python scripts/omega_runner.py evidence-bundle <problem-id>` when needed; `finish` and `proof-result` already refresh it automatically.
11. Read `protocol/evidence-governance.md`, `protocol/research-object-packaging.md`, and `protocol/runtime-language-strategy.md` before extending the runtime or writing claim-bearing outputs.
12. Regenerate the active workflow-and-run summary with `python scripts/generate_experiment_index.py` when needed, or query it directly with `omega-query --global --stage plan` / `omega-query --global --blocked-only --format table`.
13. Use the files under `protocol/` to structure the investigation.
14. Use the files under `agents/` as role specs for future orchestration.
15. Query past experiment runs with `omega-query --problem <id>` or `omega-query --verdict positive` to find prior evidence before starting new work.
16. Use the workspace agent `omega-math`, the prompts in `.github/prompts/`, and the reusable workflows in `.github/skills/` when running the flagship tracks from VS Code Copilot.
17. Check Lean files with `omega-lean check-file <file.lean>`, build Lean projects with `omega-lean build-project <dir>`, or emit structured results with `omega-lean run-command "<cmd>"`.
18. Solve SAT/SMT instances with `omega-solve smt "<z3-spec>"` or `omega-solve sat --clauses "[[1,2],[-1,3]]" --num-vars 3`.
19. Run CAS computations with `omega-cas simplify <expr>`, `omega-cas solve <equation>`, `omega-cas series <expr>`, or `omega-cas custom "result = ..."`.
20. Dispatch an agent for a specific problem and stage: `omega-orchestrate run erdos-straus --stage experiment --model deepseek-chat`.
21. Run a full pipeline across multiple stages: `omega-orchestrate pipeline erdos-straus --from-stage plan --to-stage results`.
22. Dry-run a stage to preview prompts and workspace-contract checks without calling the API: `omega-orchestrate run erdos-straus --stage plan --dry-run`.
23. Compute a fresh evidence bundle with `omega-verify-evidence compute erdos-straus` and verify it with `omega-verify-evidence verify erdos-straus`.
24. Check LLM backend health with `omega-model-router health`, inspect routing profiles with `omega-model-router profiles`, and resolve a model for a role/tier with `omega-model-router resolve --role prover --tier T4-structural`.
25. Validate registry and workspace artifact contracts (`experiments/ledger.yaml`, `evidence-bundle.yaml`) with `omega-validate-registry`.
26. Verify release metadata version sync (`pyproject.toml`, `CITATION.cff`, `PROTOCOL.md`) with `omega-verify-version-sync`.
27. Start a LeanCopilot ExternalGenerator-compatible bridge with `omega-leancop-bridge --model goedel-prover-v2-32b --base-url http://localhost:8000/v1`.
28. Run bounded verifier-guided proof repair on a Lean file with `omega-proof-repair repair proof/lean/OmegaWorkbench/Test.lean --in-place --max-iterations 32`.
29. Import Einstein Arena benchmark table into OMEGA collections with `omega-import-einstein-arena --readme-file .benchmarks/einstein-arena-readme.md`.
30. Override slug-to-registry mapping without code edits using `omega-import-einstein-arena --aliases-file registry/collections/einstein-arena-aliases.yaml`.
31. Import Einstein Arena table and copy benchmark constructions from a local donor clone with `omega-import-einstein-arena --readme-file .benchmarks/einstein-arena-readme.md --repo-dir ../EinsteinArena-new-SOTA`.
32. Query Einstein Arena API with bounded retries/backoff and PoW controls using `omega-einstein-arena --timeout 45 --max-retries 3 --retry-backoff 1.0 --pow-timeout 600 <action> ...`.
33. Use the scheduled sync workflow `.github/workflows/sync-einstein-arena.yml` to auto-open a PR when EinsteinArena benchmark snapshots drift.

## Структура проекта

```
math/
├── .github/
│   ├── agents/                       # VS Code custom agents for OMEGA workflows
│   ├── prompts/                      # VS Code prompt files for flagship tracks
│   └── skills/                       # Reusable experiment, referee, citation, and closure workflows
│
├── README.md                          # Этот файл
├── PROTOCOL.md                        # Полный протокол исследования
├── EXTRACTION_REPORT.md               # Источники и правила начальной экстракции
├── pyproject.toml                     # Python package surface for installable OMEGA CLI tools
│
├── registry/                          # Каталог открытых проблем
│   ├── schema.json                    # JSON Schema для записи о проблеме
│   ├── schemas/
│   │   ├── experiment-ledger.schema.json
│   │   └── evidence-bundle.schema.json
│   ├── triage-matrix.yaml             # Приоритетная очередь по AI-доступности
│   ├── collections/
│   │   ├── einstein-arena-aliases.yaml
│   │   ├── einstein-arena-benchmarks.yaml
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
│   ├── scaffold_problem.py
│   ├── generate_index.py
│   ├── generate_experiment_index.py
│   ├── import_einstein_arena.py       # EinsteinArena README importer (+ optional solutions/ snapshot copy)
│   ├── einstein_arena_adapter.py       # EinsteinArena API adapter (PoW, retries, discussion endpoints)
│   ├── omega_runner.py
│   ├── validate_registry.py
│   ├── experiment_query.py            # Searchable experiment-history queries
│   ├── literature_adapter.py          # Semantic Scholar + arXiv API adapter
│   ├── lean_adapter.py                # Lean 4 CLI execution adapter
│   ├── solver_adapter.py              # SAT/SMT (Z3/PySAT) execution adapter
│   ├── cas_adapter.py                 # CAS (SymPy/SageMath) execution adapter
│   ├── omega_workflow.py              # Deterministic workflow/FSM controller
│   ├── agent_orchestrator.py          # LLM-backed 7-role agent dispatch engine
│   ├── verify_evidence.py             # SHA-256 evidence bundle compute/verify/status
│   ├── model_router.py                # LLM backend routing, profiles, and health checks
│   ├── leancop_bridge.py              # LeanCopilot ExternalGenerator BYOM HTTP bridge
│   ├── proof_repair_loop.py           # Verifier-guided Lean proof repair loop
│   ├── verify_version_sync.py         # pyproject/CITATION/PROTOCOL version consistency check
│   └── README-compatible entrypoints are provided through `pyproject.toml`
│
├── tests/                             # Standalone Python test suite
│   ├── test_omega_runner.py
│   ├── test_python_surface.py
│   ├── test_experiment_query.py
│   ├── test_lean_adapter.py
│   ├── test_solver_adapter.py
│   ├── test_cas_adapter.py
│   ├── test_omega_workflow.py
│   ├── test_agent_orchestrator.py
│   ├── test_verify_evidence.py
│   ├── test_e2e_pipeline.py            # End-to-end integration tests
│   ├── test_flagship_experiments.py     # Flagship problem experiment tests
│   ├── test_literature_adapter.py
│   ├── test_model_router.py            # Model router routing + health tests
│   ├── test_import_einstein_arena.py   # EinsteinArena importer parser tests
│   ├── test_registry_pipeline.py
│   ├── test_registry_e2e.py
│   ├── test_leancop_bridge.py
│   ├── test_proof_repair_loop.py
│   └── test_version_sync.py
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
│   ├── orchestrator-contract.md        # Agent orchestrator specification
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
    ├── OMEGA_SOTA_LANDSCAPE_UPDATE_2026_04_13.md
    ├── active/README.md
    └── completed/README.md
```

## Planned Next Surface

Likely next additions (aligned with the 6-Phase Execution Plan):

### Phase 1: Pipeline Closure (immediate priority)
1. ~~Connect `lean_adapter.py` to real `lake build` with pinned mathlib toolchain~~ (Done: `lean_adapter.py` wired)
2. ~~Write integration tests for `solver_adapter.py` with concrete problem instances~~ (Done: `test_solver_adapter.py` + `test_e2e_pipeline.py`)
3. ~~Create `scripts/literature_adapter.py`~~ (Done: Semantic Scholar + arXiv API)
4. Execute full lifecycle on 3 Tier 1 problems with real evidence bundles (pending real LLM API keys)
5. ~~Create agent orchestrator with multi-API LLM dispatch~~ (Done: `agent_orchestrator.py`)
6. ~~Add standalone evidence verification CLI~~ (Done: `verify_evidence.py`)

### Phase 2: LLM-Backed Proof Search
7. Create `scripts/model_router.py` routing to Ollama + DeepSeek-Prover-V2-7B / LeanCopilot ExternalGenerator / vLLM
8. Implement bounded proof-repair loop (generate → verify → enrich → retry, max 64 iterations)
9. Implement two-level subgoal decomposition (72B+ decomposes → local 7B solves)
10. Produce first neural-generated Lean 4 proof with zero remaining `sorry`

### Phase 3: Literature and Novelty Verification
11. Add machine-readable novelty packet generator per problem
12. Add mandatory anti-rediscovery gate at TRIAGE → PLAN workflow transition

### Phase 4–6: Publication, Formal Assurance, Scaling
13. LaTeX generation from stored artifacts with audit trail
14. Automated paper generation pipelines (Writer → Reviewer loop)
15. Post-quantum cryptography formal assurance wedge (NIST FIPS 203/204/205)

See `research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md` for complete task specifications with evidence gates and academic grounding.

## Лицензия

MIT (протокол и инструментарий) — данные и результаты исследований публикуются под CC-BY 4.0.
