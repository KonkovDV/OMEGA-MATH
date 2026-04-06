# Reproducibility Manifest

> Copy this template into `research/active/<problem-id>/reproducibility.md` and fill in all fields.

## Problem

- Registry ID: `<problem-id>`
- Problem name: `<human-readable name>`

## Environment

- OS: `<e.g. Windows 11, Ubuntu 24.04>`
- Python version: `<e.g. 3.12.4>`
- Lean toolchain: `<e.g. leanprover/lean4:v4.29.0>` (if applicable)
- Key dependencies:
  ```
  <paste from requirements.txt, lakefile.lean, lake-manifest.json, or equivalent>
  ```

## Execution

- Entry command:
  ```bash
  <exact command to reproduce the result>
  ```
- Expected runtime: `<estimate>`
- Hardware note: `<CPU/GPU/RAM if relevant to runtime or result>`

## Input Artifacts

| Artifact | Path | Checksum (SHA-256) |
|----------|------|--------------------|
| Dataset | `<path>` | `<hash>` |
| Config | `<path>` | `<hash>` |

## Output Artifacts

| Artifact | Path | Checksum (SHA-256) |
|----------|------|--------------------|
| Result | `<path>` | `<hash>` |
| Log | `<path>` | `<hash>` |

## Verification

- Evidence class: `<computational | structural | formal>`
- Verified by: `<agent role or human name>`
- Verification date: `<ISO 8601>`
- Ledger run ID: `<from experiments/ledger.yaml>`
- Prover result: `<path under artifacts/prover-results/ or n/a>`

## Known Limitations

- `<what might differ across environments or re-runs>`
