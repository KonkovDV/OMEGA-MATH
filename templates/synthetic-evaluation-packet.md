# Synthetic Evaluation Packet

> Copy this template into `research/active/<problem-id>/input_files/synthetic_evaluation_packet.md` when evaluating synthetic reasoning traces, prompt families, or benchmark variants.

## Scope

- Problem ID: `<problem-id>`
- Asset family: `<synthetic reasoning traces | prompt family | benchmark pack | other>`
- Taxonomy source: `input_files/synthetic_taxonomy.md`
- Ledger run ID: `<run-id from experiments/ledger.yaml>`
- Evidence class: `R0 | R1 | E2`

## Input Set

| Input | Path | Notes |
|-------|------|-------|
| Synthetic asset file | `<path>` | `<count / size>` |
| Prompt packet bundle | `<path>` | `<optional>` |
| Critic output | `<path>` | `<optional>` |
| Downstream eval artifact | `<path>` | `<optional>` |

## Coverage Evaluation

Report how much of the declared taxonomy was actually exercised.

| Factor | Total leaves | Covered leaves | Coverage ratio | Notes |
|--------|-------------|----------------|----------------|-------|
| `<factor-1>` | `<n>` | `<k>` | `<k/n>` | `<gaps>` |
| `<factor-2>` | `<n>` | `<k>` | `<k/n>` | `<gaps>` |

## Complexity Evaluation

Describe how difficulty or complexity was distributed.

| Band | Definition | Count | Notes |
|------|------------|-------|-------|
| base | `<simple or seed-level cases>` | `<n>` | `<notes>` |
| medium | `<moderately complex cases>` | `<n>` | `<notes>` |
| high | `<stress or adversarial cases>` | `<n>` | `<notes>` |

## Critic Outcomes

| Gate | Passed | Failed | Failure pattern |
|------|--------|--------|-----------------|
| Quality | `<n>` | `<n>` | `<common failure>` |
| Correctness proxy | `<n>` | `<n>` | `<common failure>` |
| Diversity | `<n>` | `<n>` | `<common failure>` |
| Scope | `<n>` | `<n>` | `<common failure>` |

## Downstream Utility Check

- Evaluation mode: `<manual review | benchmark stress test | training ablation | other>`
- What improved: `<bounded, reproducible outcome>`
- What did not improve: `<bounded, reproducible outcome>`
- Non-monotonic lesson: `<where more data or more complexity stopped helping>`

## Claim Boundary

State explicitly what this packet does and does not justify.

- Safe claim: `<what the packet supports>`
- Unsafe claim: `This packet does not prove theorem correctness, novelty, or proof closure.`

## Follow-up

- Keep: `<what should be reused>`
- Drop: `<what should be removed from the synthetic set>`
- Next pass target: `<coverage gap or complexity gap>`