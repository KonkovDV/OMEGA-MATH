# OMEGA — Open Mathematics Exploration by Generative Agents

> English: a standalone, registry-first research runtime for bounded AI-assisted work on open mathematical problems.

> Русский: автономный репозиторий для систематической, верифицируемой и ограниченной по рискам AI-поддержки исследований открытых математических задач.

[![Validate OMEGA Registry](https://github.com/KonkovDV/OMEGA-MATH/actions/workflows/validate.yml/badge.svg)](https://github.com/KonkovDV/OMEGA-MATH/actions/workflows/validate.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Start Here / Начать Здесь

- [English overview](#english-overview)
- [Русское описание](#русское-описание)
- [Quick start](#quick-start)
- [What exists now](#what-exists-now)
- [What does not exist yet](#what-does-not-exist-yet)
- [Repository map](#repository-map)
- [Flagship research tracks](#flagship-research-tracks)
- [Project health and governance](#project-health-and-governance)

Primary entry surfaces:

- [PROTOCOL.md](PROTOCOL.md) — full operating contract and research protocol
- [protocol/operator-runbook.md](protocol/operator-runbook.md) — operator workflow and bounded runtime usage
- [protocol/orchestrator-contract.md](protocol/orchestrator-contract.md) — orchestrator contract and stage semantics
- [research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md](research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md) — concrete execution plan
- [research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md](research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md) — long-horizon roadmap
- [docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_17.md](docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_17.md) — latest deep audit and gap matrix
- [CITATION.cff](CITATION.cff), [LICENSE](LICENSE), [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md)

## English Overview

### What OMEGA is

OMEGA is a standalone Python-first research runtime for systematic work on open mathematical problems. It is not a single-problem demo, not a notebook collection, and not a vague “AI for math” wrapper. The repository is organized around four operational commitments:

1. **Registry-first scope control**: open problems are tracked in machine-readable form before work starts.
2. **Triage before execution**: problems are ranked by AI amenability, not only by mathematical prestige.
3. **Bounded execution**: experiments, proof attempts, and orchestration stages are explicit, logged, and restartable.
4. **Evidence-bearing outputs**: claims are tied to ledgers, artifacts, checksums, and verifier-visible states.

OMEGA borrows architectural patterns from external research-agent systems, but it does not vendor their runtimes. The repository executes on its own local contracts, scripts, schemas, and documentation surfaces.

### Why this repository exists

Most mathematical AI projects optimize for one of two extremes: either polished benchmark demos with weak reproducibility, or fragmented experimental code with no durable research process. OMEGA addresses the missing middle layer:

- a **catalog** of targets
- a **workflow** for choosing targets rationally
- a **runtime** for executing bounded stages
- an **evidence model** for storing what happened
- a **publication path** that does not overclaim autonomy or correctness

The intent is not to simulate a fully autonomous mathematical laboratory. The intent is to build a disciplined substrate for research operations where negative results, partial proofs, failed runs, and bounded repairs are first-class outputs rather than discarded noise.

### Verified Project State

| Surface | Verified state |
|--------|----------------|
| Release version | `0.6.0` |
| Supported Python | `3.12`, `3.13` |
| Registry size | `252` canonical problems |
| AI triage coverage | `73 / 252` (`29.0%`) |
| Test status | `226 passed` on the latest verified run |
| Registry validation | `0 errors` |
| Version sync | `pyproject.toml`, `CITATION.cff`, `PROTOCOL.md` aligned |
| Security/governance workflows | `validate`, `ci`, `codeql`, `dependency-review`, `scorecard`, `sync-einstein-arena` |

## What Exists Now

OMEGA already provides a meaningful bounded runtime rather than just planning documents.

### Core repository surfaces

- schema-validated registry under [registry](registry)
- deterministic per-problem workflow controller via `omega-workflow`
- experiment lifecycle and evidence-bundle runtime via `omega-runner` and `omega-verify-evidence`
- Lean 4, SAT/SMT, and CAS execution adapters via `omega-lean`, `omega-solve`, and `omega-cas`
- model routing and orchestration via `omega-model-router` and `omega-orchestrate`
- LeanCopilot-compatible bridge and bounded proof-repair loop via `omega-leancop-bridge` and `omega-proof-repair`
- Einstein Arena importer and API adapter surfaces for benchmark synchronization

### Documentation and research control plane

- top-level [protocol](protocol) for active operational documentation
- top-level [research](research) for core planning, SOTA, and workstation strategy surfaces
- [docs/reports](docs/reports) for audits and extraction reports
- VS Code/Copilot operational surfaces under [.github](.github)

### Claim model

OMEGA treats most model-assisted outputs as evidence-bearing but not self-verifying. Proof-oriented work remains subordinate to explicit verifier states and downstream review. The repository is designed to store candidate mathematical work, not to collapse verification and generation into a single unverifiable step.

## What Does Not Exist Yet

OMEGA is deliberately explicit about its boundaries.

It does **not** currently provide:

1. end-to-end autonomous paper production with trustworthy acceptance-level review
2. full correctness closure for theorem-level claims without human or formal verification
3. a complete literature-graph or citation-evidence service for all registry entries
4. an always-on proof-search runtime that can independently close nontrivial Lean workflows at scale
5. a mature publication pipeline for broad research dissemination across all problem classes

That boundary is not a weakness in documentation; it is part of the project’s methodological honesty.

## Quick Start

### Install

```bash
python -m pip install -e .[all]
```

### Validate the repository

```bash
omega-validate-registry
omega-verify-version-sync
```

### Scaffold one problem workspace

```bash
omega-scaffold-problem erdos-straus --title "Erdos-Straus Conjecture"
omega-workflow triage erdos-straus
```

### Dry-run the orchestrator before live calls

```bash
omega-orchestrate run erdos-straus --stage plan --dry-run
```

### Prefer the local prover lane when available

```bash
omega-orchestrate run erdos-straus --stage prove --prefer-local
```

## Core Documentation Map

This repository now follows a clearer separation between entrypoint, active protocol, core research context, and evidence layers.

| Need | Best starting surface |
|------|------------------------|
| Understand the project at a high level | [README.md](README.md) |
| Understand the full operating contract | [PROTOCOL.md](PROTOCOL.md) |
| Run the system safely | [protocol/operator-runbook.md](protocol/operator-runbook.md) |
| Understand orchestration semantics | [protocol/orchestrator-contract.md](protocol/orchestrator-contract.md) |
| Understand evidence rules | [protocol/evidence-governance.md](protocol/evidence-governance.md) |
| Understand formal-math setup | [protocol/lean-bootstrap.md](protocol/lean-bootstrap.md) |
| Understand the execution plan | [research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md](research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md) |
| Understand long-horizon strategy | [research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md](research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md) |
| Understand current gaps and remediation | [docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_17.md](docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_17.md) |

This structure aligns with April 2026 documentation guidance from GitHub, Diátaxis, and Write the Docs:

- the root README is the **discoverable GitHub entrypoint**
- protocol and research surfaces are **nearby** and **unique** sources rather than hidden deep in a docs tree
- longer, dated, or historical audit material remains in **reports/evidence** surfaces

## Research Model

### External architectural donors

OMEGA uses donor patterns rather than donor runtime coupling.

| Source | Operational role in OMEGA |
|--------|----------------------------|
| Denario | modular research pipeline and artifact shape |
| CMBAgent | planning/control runtime ideas and staged execution semantics |
| LSST DESC AI roadmap | scientific validation, robustness, and reproducibility expectations |
| EinsteinArena-new-SOTA | reproducible benchmark and public-verification donor surface |

### Formal-math and theorem-proving context

The April 2026 OMEGA stack is explicitly informed by the open formal-math landscape rather than benchmark folklore alone.

Prominent surfaces include:

- DeepSeek-Prover-V2
- Kimina-Prover
- LeanCopilot
- Numina-Lean-Agent
- FrontierMath
- proof-verifier literature such as Process Advantage Verifiers

The repository-level consequence is straightforward: OMEGA treats proof generation as a multi-stage activity involving decomposition, candidate generation, bounded repair, and explicit verifier-visible checkpoints.

## Flagship Research Tracks

OMEGA currently has three Tier-1 flagship workspaces under [research/active](research/active).

| Problem | Current run-ready surface | Primary scripts |
|--------|----------------------------|-----------------|
| Erdős–Straus | covering analysis and parametric decomposition | `phase1_covering.py`, `phase2_parametric.py` |
| Kobon triangles | arrangement search | `phase1_pseudoline_enum.py` |
| Thomson problem | multistart optimization, basin hopping, numerical certification scaffold | `phase1_multistart.py`, `phase2_basin_hopping.py`, `phase3_certify.py` |

Planned later stages remain in each workspace’s `planning/attack_plan.md`, but the repository only treats the executable phase surfaces above as currently run-ready.

## Runtime Surface

The CLI surface is intentionally broad enough to support bounded research operations without pretending to be a general autonomous lab runtime.

### Registry and workflow

- `omega-validate-registry`
- `omega-scaffold-problem`
- `omega-workflow`
- `omega-generate-index`
- `omega-generate-experiment-index`
- `omega-query`

### Execution adapters

- `omega-lean`
- `omega-solve`
- `omega-cas`
- `omega-proof-repair`
- `omega-leancop-bridge`

### Orchestration and routing

- `omega-orchestrate`
- `omega-model-router`

### Evidence and benchmark sync

- `omega-runner`
- `omega-verify-evidence`
- `omega-import-einstein-arena`
- `omega-einstein-arena`
- `omega-verify-version-sync`

## Repository Map

```text
math/
├── README.md                     # GitHub entrypoint
├── PROTOCOL.md                   # Full operating contract
├── protocol/                     # Active protocol documentation
├── research/                     # Core planning docs + active/completed workspaces
├── docs/reports/                 # Audits and extraction reports
├── registry/                     # Canonical problem registry + schemas + triage
├── scripts/                      # CLIs, adapters, routing, orchestration
├── tests/                        # Python test suite
├── templates/                    # Publication and Lean starter templates
├── agents/                       # Role configuration files
└── .github/                      # Workflows, prompts, skills, agent surfaces
```

## Project Health and Governance

This repository already exposes the standard open-source health surfaces GitHub recommends for serious collaboration.

- [LICENSE](LICENSE)
- [CITATION.cff](CITATION.cff)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)

Supply-chain and review surfaces:

- `validate.yml`
- `ci.yml`
- `codeql.yml`
- `dependency-review.yml`
- `scorecard.yml`
- `sync-einstein-arena.yml`

Maintainer metadata currently identifies the project as maintained by the **MicroPhoenix open-source community**.

## Citation and License

OMEGA is released under the MIT license for protocol and tooling surfaces. Research outputs may carry additional publication or data-sharing constraints depending on their artifact class.

If you use the repository or build derived academic outputs from it, cite the project via [CITATION.cff](CITATION.cff).

---

## Русское описание

### Что такое OMEGA

OMEGA — это не “ещё один AI demo для математики” и не набор случайных скриптов. Это самостоятельный research runtime, построенный вокруг трёх вещей:

1. **машиночитаемый реестр задач**
2. **приоритизация по AI-доступности**
3. **ограниченный, верифицируемый контур исполнения**

Идея проекта проста: не бросать модель сразу на одну знаменитую гипотезу, а выстроить воспроизводимую исследовательскую систему, где каталог, triage, workspace, эксперименты, попытки доказательства, evidence bundle и write-up связаны в одну цепочку.

### Что уже реализовано

На текущем срезе проект уже содержит не только документы, но и рабочую инфраструктуру:

- реестр открытых задач с валидацией схем
- triage queue по AI-amenability
- bounded workflow controller
- runner для экспериментов и evidence bundles
- execution adapters для Lean 4, SAT/SMT и CAS
- model router и orchestrator для стадийного запуска агентов
- LeanCopilot-compatible bridge и bounded proof repair loop
- importer и API adapter для Einstein Arena
- репозиторные governance surfaces: лицензия, citation, contributing, security, code of conduct, CI/security workflows

Проверенное состояние проекта:

| Показатель | Значение |
|-----------|----------|
| Версия | `0.6.0` |
| Поддержка Python | `3.12`, `3.13` |
| Канонических задач в реестре | `252` |
| Триажировано | `73 / 252` (`29.0%`) |
| Последний верифицированный тестовый прогон | `226 passed` |
| Registry validation | `0 errors` |

### Чего пока нет

OMEGA принципиально не притворяется “полностью автономной математической лабораторией”. Сейчас проект **не** даёт:

- надёжного end-to-end paper pipeline с финальным научным review
- полной корректностной замены человеку или формальному проверяющему инструменту
- зрелого литераторного graph layer для всего реестра
- гарантированного закрытия нетривиальных theorem-level claims без ручного или формального контроля

Эти ограничения не замаскированы. Они являются частью исследовательской честности проекта.

### Быстрый старт

```bash
python -m pip install -e .[all]
omega-validate-registry
omega-verify-version-sync
omega-scaffold-problem erdos-straus --title "Erdos-Straus Conjecture"
omega-workflow triage erdos-straus
omega-orchestrate run erdos-straus --stage plan --dry-run
```

### Куда смотреть в первую очередь

- [PROTOCOL.md](PROTOCOL.md) — если нужен полный operating contract
- [protocol/operator-runbook.md](protocol/operator-runbook.md) — если нужно реально запускать workflow
- [protocol/orchestrator-contract.md](protocol/orchestrator-contract.md) — если нужен contract оркестратора
- [research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md](research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md) — если нужен ближайший execution plan
- [research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md](research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md) — если нужен длинный горизонт проекта
- [docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_17.md](docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_17.md) — если нужен текущий gap analysis

### Почему README устроен именно так

На апрель 2026 сильный README для GitHub-репозитория должен делать несколько вещей одновременно:

- быстро объяснять, **что делает проект**
- показывать, **чем он полезен и где его границы**
- давать **короткий путь к запуску**
- указывать, **где искать подробности**
- не дублировать весь корпус документации в одном файле

Поэтому этот README выступает как **entrypoint and router**, а не как бесконечный монолит. Подробный протокол живёт в [PROTOCOL.md](PROTOCOL.md), активные procedural/reference surfaces — в [protocol](protocol), ключевой research context — в [research](research), а отчёты и evidence-аудиты — в [docs/reports](docs/reports).

### Следующие научные приоритеты

Следующая волна работы в проекте — не “добавить больше AI”, а усилить проверяемость и воспроизводимость:

1. надёжный локальный provisioning для Lean toolchain
2. полный evidence-bearing closure на трёх Tier-1 tracks
3. углубление formal proof lane с bounded verifier checkpoints
4. усиление novelty and collision checks перед publication stages
5. публикационные конвейеры, которые сохраняют provenance, downgrade rules и reviewer-visible evidence

## License

MIT for repository tooling and protocol surfaces. See [LICENSE](LICENSE).
