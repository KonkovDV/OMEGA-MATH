# OMEGA Evidence Governance

OMEGA separates claim strength from enthusiasm. A result is only as strong as the evidence surface that exists on disk and can be re-checked.

## Evidence Classes

Adapted from the parent MicroPhoenix verification program, OMEGA uses five evidence classes:

| Class | Meaning | Typical OMEGA proof surfaces |
|-------|---------|------------------------------|
| `R0` | repo-local executable proof | `experiments/ledger.yaml`, `artifacts/evidence-bundle.yaml`, `artifacts/prover-results/*.yaml`, stored logs, rerunnable commands |
| `R1` | active repo-local authority | `PROTOCOL.md`, `README.md`, active docs under `protocol/`, current scaffold outputs |
| `E1` | official external authority | official specs, primary papers, maintained vendor docs |
| `E2` | qualified external comparison | competitor workflows, reproducible benchmarks, maintained reference repos |
| `H` | hypothesis only | planned work, unverified intuition, future packaging ideas |

## Confidence Labels

For operator-facing notes, pitches, or summary decks, use these confidence boundaries:

| Label | Meaning | Minimum backing |
|-------|---------|-----------------|
| `C1` | hypothesis / exploratory | `H`, plus an upgrade path |
| `C2` | internal evidence | at least one `R0` or a coherent `R0 + R1` chain |
| `C3` | externally corroborated | `R0` plus `E1` or `E2` |

Do not use `C3` if the repo-local runtime path is missing.

## Claim Rules

1. Theorem-level language requires a proof-first run, a `prover-results/<run-id>.yaml` artifact, and a verifier or human line-check outcome that matches the prose.
2. Computational-bound language requires a stored run ledger entry, replayable commands, and artifact checksums.
3. Novelty language requires local literature artifacts: `literature.md`, `literature_graph.md`, and `citation_evidence.md` when literature positioning matters.
4. Presentation or investor-facing prose may be shorter than the paper, but it may not exceed the evidence class or confidence label of the stored artifacts.
5. Press summaries and secondary commentary are never stronger than the primary paper or the maintained repository state.

## Minimum Claim-Bearing Bundle

The smallest OMEGA claim-bearing bundle is:

1. `README.md` as the local landing page for the problem workspace
2. `reproducibility.md` with exact commands and environment notes
3. `experiments/ledger.yaml` for execution history
4. `artifacts/evidence-bundle.yaml` for checksummed machine-actionable artifact state
5. `artifacts/prover-results/*.yaml` when proof-first work reaches a verifier-visible state

## Anti-Overclaiming Rules

Do not write `solved`, `settled`, `proved`, or `verified` unless the stored artifacts justify it.

Common downgrade patterns:

- `proved` -> `draft proof candidate`
- `solved` -> `computational evidence extended to bound N`
- `novel` -> `appears novel under the currently stored literature packet`
- `formalized` -> `partially formalized` when only subclaims check

## Verification Hook

Before externalizing a result, confirm:

1. the evidence bundle regenerates cleanly
2. every listed artifact exists and matches its checksum
3. the prose in the paper or deck matches the strongest stored evidence, not the operator's hope

## Evidence Verification CLI (v0.5.0)

The `verify_evidence.py` script (`omega-verify-evidence` CLI) provides machine-executable
verification of evidence bundles:

```
omega-verify-evidence compute <problem-id>   # Recompute SHA-256 checksums for all workspace artifacts
omega-verify-evidence verify <problem-id>     # Verify stored checksums against disk state
omega-verify-evidence status <problem-id>     # Quick summary (artifact counts, last verification)
```

### Compute

Walks the problem workspace (`research/active/<problem-id>/`) and produces
`artifacts/manifest.yaml` with per-file SHA-256 checksums, discovery timestamps,
and a generation date. This replaces the earlier `omega_runner.py evidence-bundle`
surface with a standalone, auditable tool.

### Verify

Reads an existing `manifest.yaml`, re-hashes every referenced file, and reports
`PASS`, `MISSING`, or `TAMPERED` per entry. Returns exit code 0 only when all
entries match.

### Status

Shows a quick summary: total artifact count, last compute date, and any
verification warnings.