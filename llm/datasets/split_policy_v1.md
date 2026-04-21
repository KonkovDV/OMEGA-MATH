# OMEGA FT Split Policy v1

## Scope

Deterministic split policy for OMG-201 scaffold smoke.

## Split Rules

1. `train` holds supervised FT examples for smoke updates.
2. `val` holds validation examples for smoke evaluation.
3. `holdout` holds untouched examples for sanity checks.
4. Identical IDs across splits are forbidden.
5. Holdout is never used for training updates.

## Determinism

- Seed: `42`
- Manifest of record: `llm/datasets/manifest_v1.json`
- Split edits require manifest version bump.
