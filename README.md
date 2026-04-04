# OMEGA — Open Mathematics Exploration by Generative Agents

> Автономная мультиагентная система для исследования открытых математических проблем

## Миссия

Систематическое применение ИИ-агентов к тысячам нерешённых математических задач — от гипотезы Римана до проблемы усердного бобра — с целью:
1. **Каталогизации** всех открытых проблем в машиночитаемом формате
2. **Классификации** по доступности для ИИ-подходов
3. **Автоматической генерации** гипотез, доказательств и контрпримеров
4. **Публикации** результатов в формате научных статей

## Архитектура

```
┌─────────────────────────────────────────────────────┐
│                   OMEGA Protocol                     │
├──────────┬──────────┬──────────┬────────────────────┤
│ Registry │ Triage   │ Research │ Publication        │
│ (каталог)│ (оценка) │ (работа) │ (статьи)           │
├──────────┴──────────┴──────────┴────────────────────┤
│              Agent Teams (via Denario/CMBAgent)       │
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
| [Denario](https://github.com/AstroPilot-AI/Denario) (arXiv:2510.26887) | Мультиагентная система: idea→method→results→paper |
| [CMBAgent](https://github.com/CMBAgents/cmbagent) (arXiv:2507.07257) | Planning & Control бэкенд для автономного исследования |
| LSST DESC AI Roadmap (arXiv:2601.14235) | Методология AI/ML для масштабных научных задач |

### AI для математики (SOTA April 2026)

| Источник | Роль в проекте |
|----------|----------------|
| FunSearch (Nature, Jan 2024; Romera-Paredes et al.) | LLM-guided evolutionary program search; new cap set upper bounds |
| AlphaProof (DeepMind, Jul 2024) | Solved 4/6 IMO 2024 problems via Lean 4 + RL; SOTA formal proving |
| AlphaGeometry 2 (DeepMind, Jul 2024) | IMO-level geometry theorem proving |
| LeanDojo / ReProver (arXiv:2306.15626, NeurIPS 2023) | LLM-based Lean 4 theorem prover; open-source |
| LLEMMA (arXiv:2310.10631, 2023) | Open math-specialized LLM (7B/34B), Proof-Pile-2 training |
| DeepSeek-Prover-V2 (DeepSeek, 2025) | Open math prover; Lean 4 proofs via subgoal decomposition |
| Numina / AI-MO (2024–2025) | Open LLM math competition solving (AIMO Prize) |

### Данные и каталоги

| Источник | Роль в проекте |
|----------|----------------|
| Wikipedia: Открытые математические проблемы | Каталог 500+ проблем по 25+ разделам математики |
| OEIS (oeis.org) | Справочник целочисленных последовательностей |

## Current State

This directory is currently a **research seed**, not a runnable software package.

What exists now:
1. A machine-readable registry of selected open problems
2. A triage queue ranked by AI amenability
3. Protocol docs for research, verification, and publication
4. Initial agent-role configuration files

What does not exist yet:
1. A CLI
2. Experiment runners
3. Lean 4, SageMath, or arXiv integration code
4. Automated paper generation pipelines

## Recommended Use

1. Read `PROTOCOL.md` for the full operating model.
2. Start from `registry/triage-matrix.yaml` to choose a first target.
3. Use the files under `protocol/` to structure the investigation.
4. Use the files under `agents/` as role specs for future orchestration.

## Структура проекта

```
math/
├── README.md                          # Этот файл
├── PROTOCOL.md                        # Полный протокол исследования
├── EXTRACTION_REPORT.md               # Источники и правила начальной экстракции
│
├── registry/                          # Каталог открытых проблем
│   ├── schema.json                    # JSON Schema для записи о проблеме
│   ├── triage-matrix.yaml             # Приоритетная очередь по AI-доступности
│   ├── collections/
│   │   └── millennium-prize.yaml
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
├── protocol/                          # Операционные документы исследования
│   ├── agent-teams.md
│   ├── publication-workflow.md
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
    ├── active/README.md
    └── completed/README.md
```

## Planned Next Surface

Likely next additions:
1. Split `other-domains.yaml` into dedicated domain files
2. Add more named collection files beyond Millennium
3. Add experiment templates and result manifests
4. Add actual runners for Lean 4, SageMath, and publication workflows

## Лицензия

MIT (протокол и инструментарий) — данные и результаты исследований публикуются под CC-BY 4.0.
