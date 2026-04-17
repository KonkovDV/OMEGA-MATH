# OMEGA - Open Mathematics Exploration by Generative Agents

> English: a standalone, registry-first research environment for bounded AI-assisted investigation of open mathematical problems.

> Русский: автономная исследовательская среда с реестром задач и ограниченным контуром исполнения для ИИ-поддержки исследований открытых математических проблем.

[![Validate OMEGA Registry](https://github.com/KonkovDV/OMEGA-MATH/actions/workflows/validate.yml/badge.svg)](https://github.com/KonkovDV/OMEGA-MATH/actions/workflows/validate.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Start Here / Быстрый Вход

### English

- [Abstract](#abstract)
- [Verified Snapshot (2026-04-17)](#verified-snapshot-2026-04-17)
- [What OMEGA Delivers](#what-omega-delivers)
- [Boundaries and Non-Claims](#boundaries-and-non-claims)
- [Reproducible Quick Start](#reproducible-quick-start)
- [Documentation Map](#documentation-map)

### Русский

- [Краткая аннотация](#краткая-аннотация)
- [Проверенный срез на 2026-04-17](#проверенный-срез-на-2026-04-17)
- [Что уже реализовано](#что-уже-реализовано)
- [Границы проекта](#границы-проекта)
- [Быстрый старт](#быстрый-старт)
- [Карта документации](#карта-документации)

---

## Abstract

OMEGA is not a single-problem demo and not a generic "AI for math" wrapper. It is a structured research-software repository built around five operational commitments:

1. Registry first: track targets in machine-readable form before execution.
2. Triage first: prioritize by practical AI amenability, not only by prestige.
3. Bounded execution: run explicit, restartable stages with audit-friendly state.
4. Evidence-bearing artifacts: tie claims to ledgers, manifests, and checksums.
5. Honest scope: separate what is implemented, what is experimental, and what is not yet delivered.

The project borrows architectural ideas from external research-agent ecosystems, but executes on local contracts, local scripts, and local evidence surfaces.

## Documentation Design Note (April 2026)

This README is intentionally designed as an entrypoint and router, following current documentation practice:

- GitHub README guidance: clear "what/why/how/help/maintainers" at repository entry.
- Diataxis architecture: separate explanation, how-to, and reference surfaces.
- Write the Docs principles: skimmable, current, nearby, and unique sources.

The goal is fast orientation without collapsing all project documentation into one file.

## Verified Snapshot (2026-04-17)

| Surface | Verified state | Source |
|---|---|---|
| Release version | `0.6.0` | `pyproject.toml` |
| Python support | `3.12`, `3.13` | `pyproject.toml` |
| Registry size | `252` problems | `registry/index.yaml` |
| Triage coverage | `73 / 252` (`29.0%`) | `registry/index.yaml` |
| Domain files | `14` | `registry/index.yaml` |
| Collection files | `6` | `registry/index.yaml` |
| Tier distribution | T1 `28`, T2 `22`, T3 `10`, T4 `5`, T5 `8`, untriaged `179` | `registry/index.yaml` |
| Latest local test run | `218 passed, 8 skipped in 14.24s` | `python -m pytest -q` (2026-04-17) |
| Docs closure rail | `8 passed, 0 warnings, 0 failures` | `agent:preflight:docs` |

## What OMEGA Delivers

### Core runtime surfaces

- Schema-validated registry and generated index under [registry](registry).
- Deterministic per-problem workflow controller (`omega-workflow`).
- Experiment lifecycle and evidence bundle tooling (`omega-runner`, `omega-verify-evidence`).
- Execution adapters for Lean, SAT/SMT, and CAS (`omega-lean`, `omega-solve`, `omega-cas`).
- Model routing and multi-stage orchestration (`omega-model-router`, `omega-orchestrate`).
- LeanCopilot-compatible bridge and bounded proof-repair loop (`omega-leancop-bridge`, `omega-proof-repair`).
- Einstein Arena ingestion and API surfaces (`omega-import-einstein-arena`, `omega-einstein-arena`).

### Research operations model

Primary stage chain:

`brief -> novelty -> triage -> plan -> experiment/prove -> results -> paper -> referee -> promote/archive`

OMEGA is optimized for traceability and repeatability of this chain, not for unbounded autonomous behavior.

## Boundaries and Non-Claims

OMEGA does not currently claim:

1. End-to-end autonomous publication with acceptance-grade review guarantees.
2. Full theorem-level correctness closure without human or formal verification gates.
3. Complete literature-graph or citation-evidence coverage for every registry entry.
4. Always-on proof search that can independently close nontrivial Lean workflows at scale.
5. A fully productized enterprise platform with SLA-grade operational guarantees.

These boundaries are methodological constraints, not omissions in disclosure.

## Flagship Tracks (Run-Ready Surfaces)

| Problem | Current executable surface | Primary scripts |
|---|---|---|
| Erdős-Straus | covering analysis, parametric decomposition | `phase1_covering.py`, `phase2_parametric.py` |
| Kobon triangles | arrangement search | `phase1_pseudoline_enum.py` |
| Thomson problem | multistart optimization, basin hopping, numerical certification scaffold | `phase1_multistart.py`, `phase2_basin_hopping.py`, `phase3_certify.py` |

Planned later phases remain in each workspace `planning/attack_plan.md`; only the surfaces above are treated as run-ready.

## Reproducible Quick Start

### 1) Install

```bash
python -m pip install -e .[all]
```

### 2) Validate registry and release metadata

```bash
omega-validate-registry
omega-verify-version-sync
```

### 3) Scaffold and triage a workspace

```bash
omega-scaffold-problem erdos-straus --title "Erdos-Straus Conjecture"
omega-workflow triage erdos-straus
```

### 4) Dry-run orchestration before live calls

```bash
omega-orchestrate run erdos-straus --stage plan --dry-run
```

### 5) Prefer local prover lane when available

```bash
omega-orchestrate run erdos-straus --stage prove --prefer-local
```

### 6) Optional local verification

```bash
python -m pytest -q
```

## Documentation Map

### Explanation surfaces

- [README.md](README.md)
- [PROTOCOL.md](PROTOCOL.md)
- [research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md](research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md)

### How-to surfaces

- [protocol/operator-runbook.md](protocol/operator-runbook.md)
- [protocol/lean-bootstrap.md](protocol/lean-bootstrap.md)
- [protocol/verification-pipeline.md](protocol/verification-pipeline.md)

### Reference surfaces

- [protocol/orchestrator-contract.md](protocol/orchestrator-contract.md)
- [protocol/prover-result-contract.md](protocol/prover-result-contract.md)
- [protocol/experiment-ledger-spec.md](protocol/experiment-ledger-spec.md)
- [protocol/evidence-governance.md](protocol/evidence-governance.md)

### Evidence and audit surfaces

- [docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_17.md](docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_17.md)
- [docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_06.md](docs/reports/HYPER_DEEP_AUDIT_REPORT_2026_04_06.md)
- [docs/reports/EXTRACTION_REPORT.md](docs/reports/EXTRACTION_REPORT.md)

## Repository Topology

```text
math/
├── README.md
├── PROTOCOL.md
├── protocol/
├── research/
├── docs/reports/
├── registry/
├── scripts/
├── tests/
├── templates/
├── agents/
└── .github/
```

## Governance, Help, and Contribution

- License: [LICENSE](LICENSE)
- Citation metadata: [CITATION.cff](CITATION.cff)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security policy: [SECURITY.md](SECURITY.md)
- Maintainer surface: MicroPhoenix open-source community
- Issue tracker: <https://github.com/KonkovDV/OMEGA-MATH/issues>

## Citation

If you use OMEGA in research or derived tooling, cite via [CITATION.cff](CITATION.cff).

---

## Краткая аннотация

OMEGA - это не демонстрационный проект на одну задачу и не обёртка "ИИ для всего". Это исследовательский репозиторий, в котором работа строится по прозрачному контуру:

1. сначала реестр задач,
2. затем triage по практической доступности,
3. затем ограниченное исполнение с журналированием,
4. затем пакет свидетельств и формулировка результата.

Проект сознательно отделяет реализованное, экспериментальное и пока недоступное. Это важная часть научной добросовестности.

## Проверенный срез на 2026-04-17

| Показатель | Значение |
|---|---|
| Версия | `0.6.0` |
| Поддерживаемый Python | `3.12`, `3.13` |
| Задач в реестре | `252` |
| Триажировано | `73 / 252` (`29.0%`) |
| Последний локальный тестовый прогон | `218 passed, 8 skipped` |
| Статус docs closure rail | `8 passed, 0 warnings, 0 failures` |

## Что уже реализовано

- машиночитаемый реестр с валидацией схем;
- контроллер стадийного рабочего процесса;
- раннер экспериментов и генерация evidence bundle;
- адаптеры Lean, SAT/SMT и CAS;
- маршрутизация моделей и стадийная оркестрация;
- мост LeanCopilot и ограниченный цикл исправления доказательств;
- импорт и API-контур Einstein Arena;
- набор governance-документов для открытой разработки и цитирования.

## Границы проекта

Сейчас OMEGA не заявляет:

1. полностью автономную публикацию с гарантиями уровня рецензируемого журнала;
2. закрытие теоремных утверждений без человека или формального верификатора;
3. полный литераторный граф по всем записям реестра;
4. самостоятельное закрытие сложных Lean-кейсов в непрерывном режиме;
5. зрелую корпоративную платформу со SLA-гарантиями.

## Быстрый старт

```bash
python -m pip install -e .[all]
omega-validate-registry
omega-verify-version-sync
omega-scaffold-problem erdos-straus --title "Erdos-Straus Conjecture"
omega-workflow triage erdos-straus
omega-orchestrate run erdos-straus --stage plan --dry-run
```

## Карта документации

- Полный протокол: [PROTOCOL.md](PROTOCOL.md)
- Операторский запуск: [protocol/operator-runbook.md](protocol/operator-runbook.md)
- Контракт оркестратора: [protocol/orchestrator-contract.md](protocol/orchestrator-contract.md)
- Контракт результата доказательства: [protocol/prover-result-contract.md](protocol/prover-result-contract.md)
- Политика свидетельств: [protocol/evidence-governance.md](protocol/evidence-governance.md)
- Исполнительный план: [research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md](research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md)
- Дорожная карта: [research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md](research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md)
- Аудитные отчёты: [docs/reports](docs/reports)

## Лицензия и цитирование

- Лицензия проекта: [LICENSE](LICENSE)
- Правила цитирования: [CITATION.cff](CITATION.cff)
