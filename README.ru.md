# MicroPhoenix

English version: [readme.md](readme.md).

## Что это за репозиторий

MicroPhoenix — это TypeScript-first AI-платформа и инженерный workspace, построенный вокруг event sourcing, dependency-injected Clean Architecture, типизированных событий и жёсткой верификационной дисциплины на уровне репозитория.

В одном дереве здесь собраны четыре слоя работы:

- основной runtime в [src/](src), [tests/](tests) и [04-REFERENCE/](04-REFERENCE),
- IDE и agent operating system в [docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md](docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md) и [.github/](.github),
- прикладные доменные треки вроде [lime/](lime), [ecg-second-opinion/](ecg-second-opinion), [ecg-analyzer/](ecg-analyzer) и [samolet/](samolet),
- отдельные standalone-репозитории и donor/evidence-контур в [external/](external), [extraction-reports/](extraction-reports) и [archive/](archive).

Этот README сознательно остаётся входной точкой, а не архитектурной энциклопедией. Его задача — коротко описать текущую форму проекта, дать честный локальный старт и направить дальше к правильным authority surfaces.

## Границы и авторитетность

Если этого README недостаточно, дальше используйте такой порядок авторитетности:

1. [SSOT_INDEX.md](SSOT_INDEX.md)
2. [04-REFERENCE/architecture.md](04-REFERENCE/architecture.md)
3. [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md) и [.github/copilot-instructions.md](.github/copilot-instructions.md)
4. [docs/protocols/DOCUMENTATION_GOVERNANCE_SOTA_2026.md](docs/protocols/DOCUMENTATION_GOVERNANCE_SOTA_2026.md)
5. [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)

Если README расходится с этими поверхностями, приоритет у authority stack выше.

## Текущий baseline репозитория

Синхронизированный baseline сейчас такой:

- 10-слойный архитектурный SSOT с канонической entry chain в [04-REFERENCE/architecture.md](04-REFERENCE/architecture.md)
- 1,678 source files, 1,457 test files и 435 DI tokens по live-метрикам из [SSOT_INDEX.md](SSOT_INDEX.md)
- 6 активных MCP server families для context, docs, extraction, audit, code intelligence и SPP
- действующий IDE control plane для prompts, skills, agents, hooks и MCP routing в [docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md](docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md)
- действующая self-learning и lesson-governance модель в [docs/superpowers/specs/2026-03-28-ide-self-learning-operating-model-design.md](docs/superpowers/specs/2026-03-28-ide-self-learning-operating-model-design.md)
- активная общерепозиторная verification program в [docs/quality/PROJECT_VERIFICATION_PROGRAM_2026_04.md](docs/quality/PROJECT_VERIFICATION_PROGRAM_2026_04.md)

Помимо core-платформы, в репозитории есть research packs, dated audits, donor intakes и startup-oriented материалы. Их корректно читать как evidence и design context, а не как автоматическое доказательство production-ready или regulator-ready статуса.

## Карта workspace

| Поверхность | Что внутри | С чего начать |
|---|---|---|
| Core platform | Runtime, DI, event discipline, tests и архитектурный SSOT | [SSOT_INDEX.md](SSOT_INDEX.md), [04-REFERENCE/architecture.md](04-REFERENCE/architecture.md) |
| Документация и governance | Protocols, testing guides, IDE operating surfaces, quality routing | [docs/README.md](docs/README.md), [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) |
| Доменные workstreams | Прикладные продуктовые и solution-треки | локальные README и docs внутри соответствующих директорий |
| External standalones и donor evidence | Standalone-репозитории и curated donor material, включая [external/OpenRNA](external/OpenRNA), [external/SynAPS](external/SynAPS) и [external/GitNexus](external/GitNexus) | [04-REFERENCE/extraction-protocol.md](04-REFERENCE/extraction-protocol.md), [extraction-reports/](extraction-reports) |
| Исторический слой | Архив аудитов, superseded plans и dated reports | [archive/](archive), [reports/](reports) |

## С чего читать проект

Если вы впервые заходите в репозиторий, этот порядок даёт самый короткий путь к актуальному состоянию:

1. [SSOT_INDEX.md](SSOT_INDEX.md)
2. [04-REFERENCE/architecture.md](04-REFERENCE/architecture.md)
3. [AGENTS.md](AGENTS.md)
4. [docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md](docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md)
5. [docs/superpowers/specs/2026-03-28-ide-self-learning-operating-model-design.md](docs/superpowers/specs/2026-03-28-ide-self-learning-operating-model-design.md)
6. [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)

Если нужен короткий operational summary без погружения во весь SSOT-стек, начните с [AI_CHEATSHEET.md](AI_CHEATSHEET.md).

## Быстрый локальный старт

### Что понадобится

| Компонент | Статус | Примечание |
|---|---|---|
| Node.js | обязателен | Текущий docs/tooling baseline исходит из Node 24+ |
| npm | обязателен | Используйте lockfile из [package-lock.json](package-lock.json) |
| PostgreSQL | обязателен для полного runtime-path | Нужен для канонического event store и outbox-backed сценариев |
| Redis | желательно | Нужен не для всех маршрутов, но полезен для cache и event-bus-heavy сценариев |
| LLM API keys | опционально | Только для тех AI-функций, которые вы реально включаете |

### Установка

```bash
npm ci
```

### Запуск runtime

```bash
npm run build
npm run dev
```

Локальная точка входа по умолчанию: `http://localhost:3000`

Текущий runtime поднимает, в частности, такие operational probes:

- `GET /health` для быстрого liveness-check
- `GET /healthz` для readiness-style агрегации по core services
- `GET /health/ready` для готовности event-layer сервисов
- `GET /metrics` для Prometheus output, если metrics enabled

Минимальная smoke-проверка:

```bash
curl http://localhost:3000/health
curl http://localhost:3000/healthz
```

## Пути валидации

Для обычной code-wave перед pull request:

```bash
npm run test:architecture:quick
npm run lint
npm run build
npm run agent:preflight
```

Для docs-only change set:

```bash
npm run sync:metrics
npm run sync:metrics:check
npm run agent:preflight
```

Если нужен не только список команд, а вся логика доказательной верификации, используйте [docs/quality/PROJECT_VERIFICATION_PROGRAM_2026_04.md](docs/quality/PROJECT_VERIFICATION_PROGRAM_2026_04.md).

## Поддержка, вклад и публичные trust surfaces

Для публичных правил взаимодействия с репозиторием используйте:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CITATION.cff](CITATION.cff)
- [LICENSE](LICENSE)

Для publication/export governance используйте:

- [docs/protocols/GITHUB_PUBLICATION_PROTOCOL_2026.md](docs/protocols/GITHUB_PUBLICATION_PROTOCOL_2026.md)
- [docs/protocols/GITHUB_PUSH_PREPARATION_PROTOCOL_2026_04.md](docs/protocols/GITHUB_PUSH_PREPARATION_PROTOCOL_2026_04.md)
- [docs/quality/PUBLIC_GITHUB_EXPORT_GUIDE_2026_04.md](docs/quality/PUBLIC_GITHUB_EXPORT_GUIDE_2026_04.md)

## Эпистемический статус

- Этот репозиторий является активным инженерным и исследовательским workspace, а не regulator-approved deployment artifact.
- Публичная документация здесь описывает текущее инженерное состояние и evidence boundary, но не даёт blanket-обещания, что каждый subproject production-ready.
- Исторические аудиты, donor reports и dated analyses остаются полезными, но проходят через [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md), [archive/](archive) и [reports/](reports) как слой evidence, а не как живая архитектурная истина.
