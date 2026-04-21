# Synthetic Reasoning Taxonomy

> Copy this template into `research/active/<problem-id>/input_files/synthetic_taxonomy.md` before generating synthetic reasoning traces, prompt families, or benchmark variants.

## Scope

- Problem ID: `<problem-id>`
- Asset family: `<synthetic reasoning traces | prompt family | benchmark pack | other>`
- Purpose: `<training | evaluation | benchmark stress test | ablation support>`
- Non-claim boundary: `This taxonomy does not by itself prove theorem correctness, novelty, or proof closure.`

## Root Factors

List the top-level factors that define the concept space you intend to cover.

| Factor | Why it matters | Failure if omitted |
|--------|----------------|--------------------|
| `<factor-1>` | `<coverage rationale>` | `<what drifts or collapses>` |
| `<factor-2>` | `<coverage rationale>` | `<what drifts or collapses>` |

## Taxonomy Tree

Represent each factor as a bounded hierarchy from coarse to fine-grained cases.

```text
<factor-1>
├── <branch-a>
│   ├── <leaf-a1>
│   └── <leaf-a2>
└── <branch-b>
    ├── <leaf-b1>
    └── <leaf-b2>
```

Add one tree per root factor.

## Sampling Policy

- Coverage target: `<uniform | weighted | curriculum | adversarial>`
- Leaf selection rule: `<how leaves are chosen>`
- Complexification stage: `<how prompts/tasks are made harder after base sampling>`
- Maximum synthetic budget: `<count or token budget>`
- Stop rule: `<what counts as enough coverage for this pass>`

## Critic Gates

Define the filters a synthetic artifact must pass before it is kept.

| Gate | Question | Pass condition |
|------|----------|----------------|
| Quality | `<what makes this artifact readable/useful>` | `<bounded criterion>` |
| Correctness proxy | `<what internal consistency check exists>` | `<bounded criterion>` |
| Diversity | `<how duplicates/mode collapse are detected>` | `<bounded criterion>` |
| Scope | `<how out-of-domain drift is rejected>` | `<bounded criterion>` |

## Known Bias and Drift Risks

- `<taxonomy branch that may be overrepresented>`
- `<difficulty band that may be underrepresented>`
- `<reason the synthetic generator may collapse onto a narrow style>`

## Output Mapping

Record where the generated assets and supporting evidence will live.

| Output | Path |
|--------|------|
| Generated assets | `<path>` |
| Prompt packets | `<path>` |
| Evaluation packet | `<path>` |
| Ledger run | `<experiments/ledger.yaml run_id>` |

## Review Notes

- Reviewer or operator: `<name or role>`
- Review date: `<ISO 8601>`
- What remains unresolved: `<open risk or ambiguity>`