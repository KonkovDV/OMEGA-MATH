# OMEGA - Open Mathematics Exploration by Generative Agents

> English: a standalone, registry-first research environment for bounded AI-assisted investigation of open mathematical problems.

> Русский: автономная исследовательская среда с реестром задач и ограниченным контуром исполнения для ИИ-поддержки исследований открытых математических проблем.

[![Validate OMEGA Registry](https://github.com/KonkovDV/OMEGA-MATH/actions/workflows/validate.yml/badge.svg)](https://github.com/KonkovDV/OMEGA-MATH/actions/workflows/validate.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Start Here / Быстрый Вход

### English

- [Abstract](#abstract)
- [Verified Snapshot (2026-04-21)](#verified-snapshot-2026-04-21)
- [What Is In The Repo Now](#what-is-in-the-repo-now)
- [Boundaries and Non-Claims](#boundaries-and-non-claims)
- [Reproducible Quick Start](#reproducible-quick-start)
- [Documentation Map](#documentation-map)

### Русский

- [Краткая аннотация](#краткая-аннотация)
- [Проверенный срез на 2026-04-21](#проверенный-срез-на-2026-04-21)
- [Что сейчас есть в репозитории](#что-сейчас-есть-в-репозитории)
- [Границы проекта](#границы-проекта)
- [Быстрый старт](#быстрый-старт)
- [Карта документации](#карта-документации)

---

## Abstract

OMEGA is not a single-problem demo and not a generic "AI for math" wrapper. It is a structured research-software repository built around five operational commitments:

1. Registry first: track targets in machine-readable form before execution.
2. Triage first: prioritize by practical AI amenability, not only by prestige.
3. Bounded execution: run explicit, restartable stages with audit-friendly state.
4. Evidence-bearing artifacts: tie claims to ledgers, manifests, checksums, and machine-readable reports.
5. Honest scope: separate what is implemented, what is experimental, and what is still only a scaffold.

OMEGA borrows ideas from external research-agent and proving ecosystems, but it executes on local contracts, local scripts, and local evidence surfaces.

## Documentation Design Note (April 2026)

This README is an entrypoint and router.

- It tells you what the repository can already do.
- It points to the protocol and evidence surfaces that carry the details.
- It avoids turning the root README into a dump of every internal document.

## Verified Snapshot (2026-04-21)

| Surface | Verified state | Source |
|---|---|---|
| Release version | `0.6.0` | `pyproject.toml` |
| Python support | `3.12`, `3.13` | `pyproject.toml` |
| Registry size | `252` problems | `registry/index.yaml` |
| Triage coverage | `73 / 252` (`29.0%`) | `registry/index.yaml` |
| Domain files | `14` | `registry/index.yaml` |
| Collection files | `6` | `registry/index.yaml` |
| Tier distribution | T1 `28`, T2 `22`, T3 `10`, T4 `5`, T5 `8`, untriaged `179` | `registry/index.yaml` |
| Latest local full test run | `241 passed in 27.74s` | `python -m pytest -q` (2026-04-21) |
| Runtime baseline report | `APPROVED` | `reports/omega_runtime_evidence_report_v1.json` |
| Execution maturity report | `WARNING` on the audited host: Lean/Lake and `z3` absent, SAT fallback still works | `reports/omega_execution_maturity_report_v1.json` |
| FT scaffold gate | `APPROVED` | `reports/omega_ft_scaffold_gate_report_v1.json` |
| Docs closure rail | `8 passed, 0 warnings, 0 failures` | `agent:preflight:docs` |

## What Is In The Repo Now

### Core research runtime

- Schema-validated registry and generated index under [registry](registry).
- Deterministic per-problem workflow controller, including stricter transition validation and machine-readable YAML or JSON output through `omega-workflow`.
- Experiment lifecycle, evidence bundle generation, and global experiment index surfaces through `omega-runner`, `omega-verify-evidence`, and `omega-generate-experiment-index`.
- Query surfaces for per-run ledgers and the global experiment index through `omega-query`.

### Execution and orchestration surfaces

- Lean, SAT/SMT, and CAS adapters through `omega-lean`, `omega-solve`, and `omega-cas`.
- Machine-readable runtime capability probing for Lean/Lake and solver backends.
- Model routing and multi-stage orchestration through `omega-model-router` and `omega-orchestrate`.
- Orchestrator result envelopes that now preserve failed stage metadata and prompt-packet file references.

### Literature and novelty surfaces

- Programmatic literature lookup, title matching, and search through `omega-literature`.
- Deterministic novelty-collision packet generation through `omega-literature novelty-packet`.
- Local literature evidence surfaces under `input_files/literature.md`, `input_files/literature_graph.md`, and `input_files/citation_evidence.md`.

### Synthetic reasoning packet lane

- A bounded synthetic reasoning contract in [protocol/synthetic-reasoning-packets.md](protocol/synthetic-reasoning-packets.md).
- Problem-local taxonomy and evaluation packet templates under [templates/synthetic-reasoning-taxonomy.md](templates/synthetic-reasoning-taxonomy.md) and [templates/synthetic-evaluation-packet.md](templates/synthetic-evaluation-packet.md).
- Ledger support for `prompt-packet`, `synthetic-taxonomy`, and `evaluation-packet` artifacts.

### Runtime evidence and export surfaces

- Runtime baseline export through `omega-export-runtime-baseline`.
- Lean or solver execution maturity export through `omega-export-execution-maturity`.
- FT scaffold gate export through `omega-export-ft-scaffold-gate`.
- Machine-readable reports under [reports](reports).

### FT scaffold (OMG-201)

- A bounded train/eval/serve smoke scaffold under [llm](llm).
- Deterministic dataset manifest and split policy for the smoke lane.
- Local smoke entrypoints for training, evaluation, and serving.
- An explicit non-claim boundary: this scaffold proves readiness prerequisites, not theorem-quality model performance or production serving.

## Boundaries and Non-Claims

OMEGA does not currently claim:

1. End-to-end autonomous publication with acceptance-grade review guarantees.
2. Full theorem-level correctness closure without human or formal verification gates.
3. Complete literature coverage for every registry entry.
4. A synthetic reasoning lane that by itself proves novelty, correctness, or proof closure.
5. A fine-tuning stack that already delivers production inference or benchmark-leading theorem capability.
6. A host-independent Lean or SMT toolchain guarantee; execution maturity reports are environment-relative.

These are scope controls, not omitted disclaimers.

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
omega-workflow status erdos-straus --format json
```

### 4) Build a novelty-collision packet before plan or publication work

```bash
omega-literature novelty-packet "erdos-straus conjecture unit fractions" --problem-id erdos-straus --max-items 10
```

### 5) Dry-run orchestration before live calls

```bash
omega-orchestrate run erdos-straus --stage plan --dry-run
```

### 6) Export runtime evidence

```bash
omega-export-runtime-baseline
omega-export-execution-maturity
```

### 7) Run the FT scaffold gate when you need the bounded smoke lane

```bash
omega-export-ft-scaffold-gate
```

### 8) Optional full local verification

```bash
python -m pytest -q
```

## Documentation Map

### Explanation surfaces

- [README.md](README.md)
- [PROTOCOL.md](PROTOCOL.md)
- [llm/README.md](llm/README.md)
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
- [protocol/literature-adapter.md](protocol/literature-adapter.md)
- [protocol/synthetic-reasoning-packets.md](protocol/synthetic-reasoning-packets.md)

### Evidence and audit surfaces

- [docs/reports/EXTRACTION_REPORT.md](docs/reports/EXTRACTION_REPORT.md)
- [reports/omega_runtime_evidence_report_v1.json](reports/omega_runtime_evidence_report_v1.json)
- [reports/omega_execution_maturity_report_v1.json](reports/omega_execution_maturity_report_v1.json)
- [reports/omega_ft_scaffold_gate_report_v1.json](reports/omega_ft_scaffold_gate_report_v1.json)

## Repository Topology

```text
math/
├── README.md
├── PROTOCOL.md
├── protocol/
├── research/
├── docs/
├── registry/
├── scripts/
├── tests/
├── templates/
├── llm/
├── reports/
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

OMEGA - это не витрина на одну задачу и не общая обёртка "ИИ для математики". Это исследовательский репозиторий, в котором работа идёт по явному контуру:

1. сначала реестр задач,
2. затем triage по практической доступности,
3. затем ограниченное исполнение по стадиям,
4. затем пакет свидетельств, отчёты и формулировка результата.

Репозиторий сознательно разделяет то, что уже исполняется локально, то, что пока является bounded scaffold, и то, что ещё не должно звучать как закрытая научная претензия.

## Проверенный срез на 2026-04-21

| Показатель | Значение |
|---|---|
| Версия | `0.6.0` |
| Поддерживаемый Python | `3.12`, `3.13` |
| Задач в реестре | `252` |
| Триажировано | `73 / 252` (`29.0%`) |
| Последний полный локальный тестовый прогон | `241 passed in 27.74s` |
| Runtime baseline report | `APPROVED` |
| Execution maturity report | `WARNING`: на проверенной машине не найден Lean/Lake и `z3`, SAT fallback работает |
| FT scaffold gate | `APPROVED` |
| Статус docs closure rail | `8 passed, 0 warnings, 0 failures` |

## Что сейчас есть в репозитории

### Базовый исследовательский runtime

- машиночитаемый реестр с валидацией схем;
- контроллер рабочего процесса по стадиям с более строгой валидацией переходов и выводом в YAML или JSON;
- раннер экспериментов, evidence bundle и глобальный experiment index;
- query surfaces для ledger и experiment index через `omega-query`.

### Исполнительные и orchestration surfaces

- адаптеры Lean, SAT/SMT и CAS;
- capability probing для Lean/Lake и solver backends;
- маршрутизация моделей и стадийная оркестрация;
- более информативные orchestrator envelopes: сохраняются failed stage metadata и prompt-packet file references.

### Literature и novelty lane

- `omega-literature` теперь покрывает lookup, search, match-title и `novelty-packet`;
- novelty packet строится детерминированно и даёт collision-risk labels для предварительной проверки новизны;
- локальные surfaces для литературы и citation evidence остаются обязательными при реальных novelty claims.

### Synthetic reasoning packet lane

- появился локальный контракт для synthetic reasoning work;
- есть problem-local шаблоны taxonomy и evaluation packet;
- ledger умеет хранить `prompt-packet`, `synthetic-taxonomy` и `evaluation-packet`.

### Runtime evidence и FT scaffold

- `omega-export-runtime-baseline` собирает общий runtime evidence report;
- `omega-export-execution-maturity` фиксирует состояние Lean и solver toolchains на текущем хосте;
- `omega-export-ft-scaffold-gate` проверяет bounded FT scaffold в `llm/`;
- под `llm/` лежит локальный smoke train/eval/serve scaffold с явными non-claims.

## Границы проекта

Сейчас OMEGA не заявляет:

1. полностью автономную публикацию с гарантиями уровня рецензируемого журнала;
2. закрытие теоремных утверждений без человека или формального верификатора;
3. полный литераторный граф по всем записям реестра;
4. что synthetic reasoning lane сам по себе доказывает новизну, корректность или proof closure;
5. что FT scaffold уже означает production inference или theorem-level model capability;
6. что Lean или SMT toolchain гарантированно доступны на любой машине без отдельной локальной настройки.

## Быстрый старт

```bash
python -m pip install -e .[all]
omega-validate-registry
omega-verify-version-sync
omega-scaffold-problem erdos-straus --title "Erdos-Straus Conjecture"
omega-workflow triage erdos-straus
omega-workflow status erdos-straus --format json
omega-literature novelty-packet "erdos-straus conjecture unit fractions" --problem-id erdos-straus --max-items 10
omega-orchestrate run erdos-straus --stage plan --dry-run
omega-export-runtime-baseline
omega-export-execution-maturity
omega-export-ft-scaffold-gate
python -m pytest -q
```

## Карта документации

- Полный протокол: [PROTOCOL.md](PROTOCOL.md)
- Операторский запуск: [protocol/operator-runbook.md](protocol/operator-runbook.md)
- Literature adapter contract: [protocol/literature-adapter.md](protocol/literature-adapter.md)
- Synthetic reasoning packet contract: [protocol/synthetic-reasoning-packets.md](protocol/synthetic-reasoning-packets.md)
- Контракт оркестратора: [protocol/orchestrator-contract.md](protocol/orchestrator-contract.md)
- Контракт результата доказательства: [protocol/prover-result-contract.md](protocol/prover-result-contract.md)
- Политика свидетельств: [protocol/evidence-governance.md](protocol/evidence-governance.md)
- FT scaffold note: [llm/README.md](llm/README.md)
- Extraction report: [docs/reports/EXTRACTION_REPORT.md](docs/reports/EXTRACTION_REPORT.md)
- Machine-readable reports: [reports](reports)

## Лицензия и цитирование

- Лицензия проекта: [LICENSE](LICENSE)
- Правила цитирования: [CITATION.cff](CITATION.cff)
