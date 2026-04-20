# MicroPhoenix

English: you are reading it now. Russian version: [README.ru.md](README.ru.md).

## What this repository is

MicroPhoenix is a TypeScript-first AI platform and engineering workspace built around event sourcing, dependency-injected Clean Architecture, typed event contracts, and verification-heavy repository governance.

The core repository combines four concerns in one place:

- the main runtime under [src/](src), [tests/](tests), and [04-REFERENCE/](04-REFERENCE),
- an IDE and agent operating system under [docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md](docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md) and [.github/](.github),
- applied domain workstreams such as [lime/](lime), [ecg-second-opinion/](ecg-second-opinion), [ecg-analyzer/](ecg-analyzer), and [samolet/](samolet),
- and standalone or donor-style companion repos under [external/](external) plus evidence layers such as [extraction-reports/](extraction-reports) and [archive/](archive).

This README is intentionally an entrypoint. It states the current repository shape, gives a workable local start path, and routes deeper questions to the correct authority surfaces.

## Scope and authority

Use the following authority order when this README is too shallow for the question at hand:

1. [SSOT_INDEX.md](SSOT_INDEX.md)
2. [04-REFERENCE/architecture.md](04-REFERENCE/architecture.md)
3. [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), and [.github/copilot-instructions.md](.github/copilot-instructions.md)
4. [docs/protocols/DOCUMENTATION_GOVERNANCE_SOTA_2026.md](docs/protocols/DOCUMENTATION_GOVERNANCE_SOTA_2026.md)
5. [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)

If a statement here conflicts with those sources, the authority stack above prevails.

## Current repository baseline

The current synchronized baseline is:

- 10-layer Clean Architecture SSOT with the runtime entry chain documented in [04-REFERENCE/architecture.md](04-REFERENCE/architecture.md)
- 1,678 source files, 1,457 test files, and 435 DI tokens according to the live repository metrics surfaced through [SSOT_INDEX.md](SSOT_INDEX.md)
- 6 live MCP server families across context, docs, extraction, audit, code intelligence, and SPP surfaces
- an active IDE control plane for prompts, skills, agents, hooks, and MCP routing in [docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md](docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md)
- an active self-learning and lesson-governance model in [docs/superpowers/specs/2026-03-28-ide-self-learning-operating-model-design.md](docs/superpowers/specs/2026-03-28-ide-self-learning-operating-model-design.md)
- a repository-wide verification program in [docs/quality/PROJECT_VERIFICATION_PROGRAM_2026_04.md](docs/quality/PROJECT_VERIFICATION_PROGRAM_2026_04.md)

The repository also contains research packs, audits, donor intakes, and startup-oriented materials. Those documents are useful evidence and design context, but they are not equivalent to production guarantees or regulatory approval.

## Workspace map

| Surface | What it holds | Start here |
|---|---|---|
| Core platform | Runtime, DI, events, tests, and architecture SSOT | [SSOT_INDEX.md](SSOT_INDEX.md), [04-REFERENCE/architecture.md](04-REFERENCE/architecture.md) |
| Documentation and governance | Protocols, testing guides, IDE operating surfaces, quality routing | [docs/README.md](docs/README.md), [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) |
| Domain workstreams | Applied product or solution tracks such as Lime, ECG, and Samolet | local README/docs inside each directory |
| External standalones and donor evidence | Standalone repositories and curated intake material such as [external/OpenRNA](external/OpenRNA), [external/SynAPS](external/SynAPS), and [external/GitNexus](external/GitNexus) | [04-REFERENCE/extraction-protocol.md](04-REFERENCE/extraction-protocol.md), [extraction-reports/](extraction-reports) |
| Historical evidence | Archived audits, superseded plans, and dated report packs | [archive/](archive), [reports/](reports) |

## Start here

If you are new to the repository, use this reading order:

1. [SSOT_INDEX.md](SSOT_INDEX.md)
2. [04-REFERENCE/architecture.md](04-REFERENCE/architecture.md)
3. [AGENTS.md](AGENTS.md)
4. [docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md](docs/quality/IDE_AI_OPERATING_SYSTEM_2026.md)
5. [docs/superpowers/specs/2026-03-28-ide-self-learning-operating-model-design.md](docs/superpowers/specs/2026-03-28-ide-self-learning-operating-model-design.md)
6. [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)

If you want the short explanation rather than the full architecture stack, start from [AI_CHEATSHEET.md](AI_CHEATSHEET.md).

## Local quick start

### Prerequisites

| Component | Status | Notes |
|---|---|---|
| Node.js | required | Current repository docs and tooling assume Node 24+ |
| npm | required | Use the lockfile in [package-lock.json](package-lock.json) |
| PostgreSQL | required for full runtime paths | Needed for the canonical event-store and outbox-backed flows |
| Redis | recommended | Used in cache and event-bus-heavy scenarios |
| LLM API keys | optional | Only required for the AI features you actually enable |

### Install

```bash
npm ci
```

### Start the repository runtime

```bash
npm run build
npm run dev
```

Default local endpoint: `http://localhost:3000`

Operational probes exposed by the current runtime include:

- `GET /health` for a fast liveness check
- `GET /healthz` for readiness-style aggregation across core services
- `GET /health/ready` for core event service readiness
- `GET /metrics` for Prometheus output when metrics are enabled

Quick smoke check:

```bash
curl http://localhost:3000/health
curl http://localhost:3000/healthz
```

## Validation paths

For ordinary code work before a pull request:

```bash
npm run test:architecture:quick
npm run lint
npm run build
npm run agent:preflight
```

For docs-only changes:

```bash
npm run sync:metrics
npm run sync:metrics:check
npm run agent:preflight
```

If you need the broader verification philosophy rather than just the commands, use [docs/quality/PROJECT_VERIFICATION_PROGRAM_2026_04.md](docs/quality/PROJECT_VERIFICATION_PROGRAM_2026_04.md).

## Help, contribution, and trust surfaces

For public-facing repository expectations, use:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CITATION.cff](CITATION.cff)
- [LICENSE](LICENSE)

For publication and export governance, use:

- [docs/protocols/GITHUB_PUBLICATION_PROTOCOL_2026.md](docs/protocols/GITHUB_PUBLICATION_PROTOCOL_2026.md)
- [docs/protocols/GITHUB_PUSH_PREPARATION_PROTOCOL_2026_04.md](docs/protocols/GITHUB_PUSH_PREPARATION_PROTOCOL_2026_04.md)
- [docs/quality/PUBLIC_GITHUB_EXPORT_GUIDE_2026_04.md](docs/quality/PUBLIC_GITHUB_EXPORT_GUIDE_2026_04.md)

## Epistemic status

- This repository is an active engineering and research workspace, not a regulator-approved deployment artifact.
- Public documentation should be read as current engineering evidence, not as a blanket claim that every subproject is production-ready.
- Historical audits, donor reports, and dated analyses remain useful, but they belong to the evidence layer routed through [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md), [archive/](archive), and [reports/](reports).
