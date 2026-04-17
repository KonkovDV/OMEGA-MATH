---
title: "OMEGA Hyper-Deep Audit 2026-04-04"
status: "active"
version: "1.0.0"
last_updated: "2026-04-05"
role: evidence
tags: [omega, audit, research, startup, reproducibility]
---

# OMEGA Hyper-Deep Audit 2026-04-04

## Scope

Проверены:

- текущий diff standalone-репозитория `math/`
- protocol and registry surfaces
- CI and validation scripts
- research/startup surfaces в основном MicroPhoenix runtime
- внешние best practices по citation, experiment tracking, theorem-prover onboarding и Python project metadata

## Verified Findings

### Critical Before This Session

1. `odd-perfect-numbers` имел заниженное `decades_open: 20`, хотя сама проблема известна намного дольше; это создавало semantic drift в canonical registry.
2. `millennium-prize.yaml` был слабо связан с canonical registry: без `registry_id` validator не мог проверять cross-links для большинства записей.
3. GitHub Actions validation rail падал на drift generated files без нормального remediation message.

### Fixed In This Session

1. Исправлена data-correctness ошибка для odd perfect numbers.
2. Millennium collection теперь cross-referenceable через `registry_id` там, где canonical domain entry существует.
3. CI теперь явно говорит, что нужно регенерировать `registry/index.yaml`, и показывает diff.
4. Python dependencies для validator rail зафиксированы до точных версий.
5. Добавлен `CITATION.cff` для GitHub-ready research citation surface.
6. README и PROTOCOL теперь явно разводят canonical domain registry и quick-reference collection overlays.

### Follow-On Implementation Delta (2026-04-05)

1. Добавлен bounded local runner для `experiment-first`, `proof-first` и `survey-first` run bookkeeping: `scripts/omega_runner.py` + thin CLI wrapper `scripts/omega-runner.py`.
2. Добавлен `scripts/generate-experiment-index.py` и фактическая генерация `research/active/experiment-index.yaml` из per-problem ledgers.
3. Добавлены standalone Python unit tests для runner substrate и CI шаг, который их запускает.
4. `protocol/operator-runbook.md` теперь отражает реальный CLI workflow, а не только ручное редактирование YAML.

## Remaining Gaps

### High Value

1. Нет real execution adapter layer для Lean 4 / mathlib builds, CAS, SageMath, SAT/SMT и literature retrieval, хотя bounded CLI bookkeeping уже есть.
2. Нет search/query layer поверх experiment history beyond the generated latest-run index.
3. Нет artifact checksum automation или provenance enrichment inside the runner itself.
4. Нет solver-backed closure lane для algebra-heavy `proof_obligations.md` workflows.

### Medium Value

1. Triage coverage лишь `25.1%`, поэтому current queue хорош для приоритетного старта, но не для balanced exploration.
2. Collection coverage всё ещё частичная: taxonomy шире, чем реально реализованные YAML overlays.
3. Reproducibility manifests are scaffolded, but there is still no automatic population or verification of checksums/commands.

## External Best-Practice Synthesis

### Citation and Repository Legibility

- GitHub и Citation File Format рекомендуют root-level `CITATION.cff`, чтобы репозиторий автоматически показывал `Cite this repository` и отдавал APA/BibTeX exports.
- Для OMEGA это особенно важно, потому что проект позиционируется как research software, а не просто заметки.

### Experiment Tracking

- MLflow Tracking организует работу вокруг `runs`, `experiments`, `metrics`, `params` и `artifacts`.
- Для OMEGA эквивалентом должны стать `campaign -> run -> artifact set -> verdict`, а не просто папки с markdown.
- На следующем шаге имеет смысл добавить local-first experiment ledger, а не сразу тяжёлый cloud stack.

### Formal Prover Integration

- Lean documentation и mathlib4 показывают, что practical integration начинается не с "AGI proves theorems", а с reproducible toolchain: `lean-toolchain`, `lake`, `mathlib` dependency, cached builds, searchable docs.
- Для OMEGA это означает, что Prover lane должен стартовать с bounded Lean workspace templates и доказуемого import/build pipeline.

### Python Project Hygiene

- PyPA рекомендует `pyproject.toml` как central metadata surface для Python projects.
- OMEGA пока ещё не packaged Python project, поэтому немедленное добавление packaging surface не является обязательным, но появится как только scripts превратятся в installable CLI/tooling package.

## MicroPhoenix Technologies Relevant To OMEGA

### Directly Reusable Research Assets

1. `docs/scientific/SCIENTIFIC_PUBLICATION_PROTOCOL.md` — уже готовая scientific-governance and publication pipeline.
2. `src/scripts/scientific-data-extractor.ts` — extraction of live metrics, anonymization, reproducibility-locked datasets.
3. `src/scripts/zenodo-auto-stager.ts` — FAIR/RO-Crate/DataCite/Zenodo packaging surface.
4. `src/scripts/retraction-monitor.ts`, `citation-validator.ts`, `ai-peer-reviewer.ts` — epistemic guard layer для research outputs.
5. MCP SPP server — publication-protocol checks как отдельная tool surface.

### Directly Reusable Agentic Assets

1. MCP Context / Docs / Extraction / Audit / Code Intelligence / SPP estate.
2. MAS task types already include `research`.
3. DI token surface already contains `IDeepResearchService`, `IResearchLabOrchestrator`, `IResearchPlanImplementWorkflow`, `ResearcherAgent`.
4. `IScientificSkillPlugin` и `IPythonSkillBridge` already exist in the main runtime vocabulary.
5. Memory + Graph surfaces create a path toward experiment memory, literature memory, and proof-state memory.

### Startup-Relevant Assets

1. `docs/protocols/STARTUP_SPINOFF_PROTOCOL.md` — bounded startup-router semantics.
2. `docs/startups/INVESTOR_DOC_STANDARD_2026.md` — claim-confidence and evidence-first investor communication contract.
3. `docs/startups/AUTONOMOUS_SOFTWARE_FACTORY_PLAYBOOK_2026.md` — productization thesis for turning internal capabilities into externally operable startup artifacts.

## 100/100 Upgrade Backlog

1. Extend the new runner from bookkeeping into actual execution adapters with bounded runtime policies.
2. Add Lean 4 build/verification automation on top of the existing bootstrap and prover-result contract.
3. Add provenance URLs and literature packets to top T1/T2 entries.
4. Add searchable experiment history and checksum automation instead of latest-run summaries only.
5. Add startup-facing evidence packet specifically for OMEGA as a research-software product candidate.