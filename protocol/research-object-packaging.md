# OMEGA Research Object Packaging

OMEGA is local-first. It does not yet emit RO-Crate, DataCite, or Signposting payloads automatically, but it now stores the repository surfaces that such packaging would need.

## Current Local Research Object

For each active problem, the local research object is the workspace under:

```text
research/active/<problem-id>/
```

The current packaging contract is:

| Role | Local surface |
|------|---------------|
| landing page | `README.md` |
| reproducibility metadata | `reproducibility.md` |
| literature and novelty packet | `input_files/literature.md`, `input_files/literature_graph.md`, `input_files/citation_evidence.md` |
| proof obligations | `input_files/proof_obligations.md` |
| run history | `experiments/ledger.yaml` |
| machine-actionable evidence bundle | `artifacts/evidence-bundle.yaml` |
| verifier-visible proof outcomes | `artifacts/prover-results/*.yaml` |

## Why The Evidence Bundle Exists

`artifacts/evidence-bundle.yaml` is the smallest local bridge between markdown-heavy research work and machine-actionable packaging.

It records:

1. the problem id
2. the active supporting documents
3. every stored run artifact
4. checksums and sizes for those artifacts
5. a stable summary of run count and artifact types

That gives OMEGA a deterministic local manifest before any external archival automation is introduced.

## Future Mapping To External Standards

The current local layout maps cleanly to the external standards already studied for OMEGA.

### FAIR Signposting

The local mapping is designed so a future web-published problem workspace could expose:

- `README.md` as the landing page
- `reproducibility.md` and related metadata files as `describedby` resources
- run outputs and proof artifacts as `item` content resources
- a future linkset document as the Level 2 machine map

### RO-Crate 1.1

The problem workspace already has the core entities RO-Crate expects:

- a root data entity (`research/active/<problem-id>/`)
- data entities (artifacts, ledgers, proof results)
- contextual entities (problem title, sources, verifier surfaces, future creators and licenses)

### DataCite 4.5

If a problem workspace or derived dataset later receives a DOI, OMEGA already stores the minimum local surfaces needed to generate a future metadata record:

- title
- creators / contributors
- resource type
- related identifiers
- artifact lineage

## Non-Goals In The Current Slice

This implementation does not yet:

1. emit RO-Crate JSON-LD
2. emit DataCite JSON or XML
3. emit FAIR Signposting HTTP headers or linksets
4. publish to Zenodo or any DOI provider

Those are intentionally deferred until OMEGA has a stronger execution and archival lane.

## Operator Rule

Treat the local workspace as the canonical research object first. External packaging comes later and must be generated from these local files, never from prose summaries alone.