# OMEGA Prover Result Contract

Every proof-first run that reaches a verifier-visible outcome must persist a separate prover-result artifact.

The experiment ledger records execution history. The prover result records the current status of a claim.

## Canonical Path

```text
research/active/<problem-id>/artifacts/prover-results/<run-id>.yaml
```

Use the same `run_id` as the linked entry in `experiments/ledger.yaml` whenever the proof result belongs to a single run.

## Required Fields

```yaml
run_id: "<problem-id>-<YYYYMMDD>-<seq>"
problem_id: "<registry problem ID>"
claim_label: "<theorem, lemma, conjecture variant, or counterexample certificate>"
claim_class: "lemma | theorem | structural-claim | counterexample-cert"
ledger_run_id: "<linked run_id from experiments/ledger.yaml>"
proof_obligations_path: "input_files/proof_obligations.md"
source_entry: "<primary source file or draft location>"
status: "draft | partial | verified | rejected | needs-human-review"
verifier:
  kind: "lean4 | coq | isabelle | cas | human-line-check"
  toolchain: "<versioned verifier surface>"
  command: "<exact verification command or procedure>"
updated_at: "<ISO 8601 timestamp>"
```

## Recommended Fields

```yaml
novelty_gate: "unchecked | checked"
dependencies:
  - "<lemma, paper result, or imported module>"
artifacts:
  - path: "<relative path to log, transcript, or proof file>"
    type: "source | log | transcript | proof-term | report"
    checksum: "<SHA-256 or null>"
notes: "<free-text operator note>"
```

## Status Semantics

| Status | Meaning |
|--------|---------|
| `draft` | A proof attempt exists, but the verifier outcome is not yet stable enough to report. |
| `partial` | Some subclaims or modules verify, but the top-level claim does not yet close. |
| `verified` | The stated claim passes the named verifier or documented human line-by-line closure. |
| `rejected` | The verifier or review process refuted the current claim or proof attempt. |
| `needs-human-review` | Machine checks passed locally, but publication-grade human review is still mandatory. |

## Separation From The Ledger

1. `experiments/ledger.yaml` tracks research execution.
2. `artifacts/prover-results/<run-id>.yaml` tracks claim status.
3. A `positive` ledger verdict does not automatically imply `verified` proof status.
4. One ledger run may produce multiple prover results if it tests multiple claims.

## Minimal Artifact Rule

If a proof result is claim-bearing, attach at least one supporting artifact:

- Lean, Coq, or Isabelle source file
- verifier log
- transcript showing the accepted repair loop
- human review note when the closure is manual rather than mechanized

## Verification Use

The verification pipeline should treat this file as the first place to answer:

1. what exact claim was checked
2. by which verifier and command
3. whether the current status is `verified`, `partial`, or `rejected`
4. which obligations remain open