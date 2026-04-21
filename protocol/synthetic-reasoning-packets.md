# OMEGA Synthetic Reasoning Packets

OMEGA does not yet run a full synthetic-data pipeline, but it now defines the local artifact
contract for future synthetic reasoning work.

## Purpose

Use synthetic reasoning packets when a problem workspace needs to generate or evaluate:

- synthetic reasoning traces
- prompt families for bounded benchmark generation
- stress-test variants for evaluation
- taxonomy-backed synthetic corpora for later training or ablation work

These packets are methodology artifacts. They are not proof artifacts.

## Required Files

When this lane is active, keep these files in the problem workspace:

- `input_files/synthetic_taxonomy.md`
- `input_files/synthetic_evaluation_packet.md`
- `experiments/ledger.yaml`

Base templates live at:

- `templates/synthetic-reasoning-taxonomy.md`
- `templates/synthetic-evaluation-packet.md`

## Packet Roles

### Synthetic taxonomy

`synthetic_taxonomy.md` defines:

- the concept-space factors
- the tree of branches and leaves to sample from
- the sampling policy
- the critic gates
- the output mapping to generated assets and prompt packets

### Synthetic evaluation packet

`synthetic_evaluation_packet.md` records:

- what was generated
- which taxonomy leaves were covered
- how complexity was distributed
- which critic gates passed or failed
- whether downstream utility actually improved

## Claim Discipline

1. Synthetic packet results can support training or evaluation planning.
2. Synthetic packet results cannot by themselves support theorem, novelty, or proof claims.
3. If a downstream result depends on synthetic assets, keep the synthetic packet linked from the run ledger and evidence bundle.

## Minimal Workflow

1. Copy `templates/synthetic-reasoning-taxonomy.md` into the problem workspace.
2. Define the factor tree and stop rule before generation.
3. Generate synthetic assets or prompt packets in a bounded run.
4. Copy `templates/synthetic-evaluation-packet.md` into the problem workspace.
5. Record coverage, complexity, critic failures, and downstream utility.
6. Link the outputs back into `experiments/ledger.yaml`.

Recommended artifact typing in the ledger:

- `input_files/synthetic_taxonomy.md` -> `synthetic-taxonomy`
- `input_files/synthetic_evaluation_packet.md` -> `evaluation-packet`
- generated prompt bundles or prompt packet exports -> `prompt-packet`

## Review Questions

Before reusing a synthetic packet, answer:

1. Which taxonomy branches were not covered?
2. Did critic failures cluster in one band or branch?
3. Did higher complexity help, hurt, or saturate?
4. Is any claimed value still only hypothetical?
5. Has anyone accidentally upgraded a synthetic-data result into a proof or novelty claim?