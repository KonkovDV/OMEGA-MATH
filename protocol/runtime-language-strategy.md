# OMEGA Runtime And Language Strategy

This page defines the active language and runtime strategy for OMEGA.

## Decision Summary

OMEGA is now explicitly **Python-first with bounded polyglot boundaries**.

That means:

1. **Python** is the primary implementation language for OMEGA orchestration, registry maintenance, experiment tracking, reproducibility surfaces, packaging, and future execution/query layers.
2. **Lean 4** is not an optional library choice but the trusted proof substrate for formal verification work.
3. **TypeScript** remains valuable at the parent MicroPhoenix layer for MCP servers, web-facing control planes, and research-governance integrations, but it is not the primary runtime inside the standalone `math/` repository.
4. **Rust** is deferred. It may become relevant later for performance-critical verifiers, storage engines, or ATP acceleration, but it is not the best first implementation language for the current OMEGA roadmap.

## Evidence Base

The decision is grounded in current repo state and in the external evidence checked during the April 2026 review.

### Current Repo State

The OMEGA runtime already exists in Python:

- `scripts/omega_runner.py`
- `scripts/scaffold_problem.py`
- `scripts/generate_index.py`
- `scripts/generate_experiment_index.py`
- `scripts/validate_registry.py`
- standalone Python unit tests under `tests/`

Changing the primary runtime language now would create architectural churn without solving a verified bottleneck.

### Official External Guidance

- **Lean official docs** recommend Lean 4 + VS Code extension as the standard setup path for theorem work.
- **PyPA packaging guidance** recommends a `pyproject.toml` surface with `[build-system]`, `[project]`, and console scripts for installable CLIs.
- **MLflow Tracking** models experiment management around experiments, runs, metrics, parameters, artifacts, and searchable histories. This maps closely onto OMEGA's ledger and evidence-bundle surfaces.
- **DataCite guidance** continues to emphasize machine-actionable metadata, landing pages, related identifiers, and provenance-aware DOI metadata.

### Open-Source Analogs And Competitors

#### Python-first research systems

- **Denario**: Python-first scientific research assistant with `pyproject.toml`, virtualenv/uv install flows, and project-directory artifact contract.
- **CMBAgent**: Python-only autonomous research engine with extras by domain, stepwise planning/control, and editable install workflow.
- **Numina-Lean-Agent**: Python-first agent runtime with Lean as the formal proving substrate.
- **AutoGen**: Python-dominant agent framework with some cross-language support, but the main orchestration surface is still Python.

#### Lean ecosystem signal

- **LeanCopilot** shows that the proof-assistant layer itself is inherently polyglot: Lean + C++ + Python can coexist, but the orchestration around it can still remain Python-first.

## Why Python Wins Now

### 1. Strongest research-tooling fit

OMEGA's immediate roadmap is dominated by:

- experiment ledgers
- provenance bundles
- CAS and symbolic execution
- literature and metadata processing
- proof-run orchestration around Lean

Python has the strongest ecosystem fit across all five.

### 2. Lowest migration risk

Python is already the implemented runtime. Formalizing it avoids a rewrite tax and lets OMEGA improve the actual missing layers instead of relitigating infrastructure.

### 3. Best fit for future execution adapters

The next high-value gaps identified in OMEGA are:

1. execution adapters for Lean/CAS/SAT/SMT
2. searchable experiment history
3. stronger reproducibility automation

All three are easier to ship quickly in Python than in TypeScript or Rust.

### 4. Clean polyglot boundary is already available

Python-first does **not** mean mono-language everywhere.

The correct boundary is:

- Python: orchestration and research runtime
- Lean: proof kernel and formal objects
- TypeScript: optional parent-repo integration, MCP, UI, and publication-governance reuse
- Rust: only after a concrete performance bottleneck is measured

## Why Not TypeScript-first

TypeScript is strong for service backends, MCP servers, and typed integration layers. But for OMEGA specifically it is weaker than Python on:

- CAS and scientific ecosystem breadth
- notebook and local experiment ergonomics
- compatibility with donor systems already studied
- proximity to current OMEGA code

TypeScript should therefore be treated as an integration language, not the lab runtime.

## Why Not Rust-first

Rust would improve some future concerns:

- storage safety
- concurrency control
- performance-critical parsing or indexing

But Rust is the wrong first move because it would slow down:

- research iteration
- CLI evolution
- metadata/provenance work
- Lean and Python ecosystem integration

Until OMEGA measures a real CPU, memory, or concurrency bottleneck, Rust is premature.

## Active Architecture Rule

When adding a new OMEGA runtime capability, default to the smallest sound tier:

1. **Python-first** implementation inside `math/`
2. **Lean-side** artifact or command integration if proof verification is involved
3. **TypeScript bridge** only when the feature must plug into the parent MicroPhoenix MCP, UI, or governance stack
4. **Rust** only with measured need and a narrow scope

## Phased Roadmap

### Phase P0 — Runtime Formalization

- Keep the current CLI semantics stable.
- Add a buildable Python packaging surface.
- Preserve script-path compatibility while enabling installable entrypoints.

### Phase P1 — Searchable Experiment History

- Add a Python query surface over `experiments/ledger.yaml` and `artifacts/evidence-bundle.yaml`.
- Support filtering by problem, route, verdict, artifact type, and time.
- Keep it local-first before adding databases.

### Phase P2 — Execution Adapters

- Add Python execution adapters for Lean build/check flows.
- Add bounded CAS and symbolic execution lanes.
- Emit machine-readable verifier outcomes instead of relying on operator narration.

### Phase P3 — Parent Integration Layer

- Reuse selected TypeScript-based MicroPhoenix assets for citation validation, FAIR packaging, AI peer review, and startup-facing evidence packets.
- Keep this as a bridge layer, not as the main lab runtime.

### Phase P4 — Optional Performance Specialization

- Introduce Rust only if OMEGA later measures a clear bottleneck in storage, query indexing, or verification throughput.

## Operator Guidance

If a new feature proposal requires asking "Python, TypeScript, Rust, or polyglot?", apply this default:

- If it is a research-runtime concern, choose Python.
- If it is a prover concern, keep the proof object in Lean and orchestrate it from Python.
- If it is an MCP/UI/governance concern shared with MicroPhoenix, TypeScript may own the outer interface.
- If the only reason to choose Rust is "future performance", do not choose Rust yet.