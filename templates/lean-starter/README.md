# OMEGA Lean Starter

Minimal mathlib-backed Lean 4 starter for proof-first OMEGA work.

This starter is intentionally small: it gives OMEGA a reproducible Lean project boundary before any model-assisted proving surface is added.

## Sources

- official Lean project bootstrap guidance
- current `mathlib4` toolchain
- `lake exe cache get` workflow from Lean community and mathlib docs

## Recommended Placement

Copy this directory into a problem-local proof workspace such as:

```text
research/active/<problem-id>/proof/lean/
```

## Bootstrap

```bash
lake update
lake exe cache get
lake build OmegaWorkbench
lake env lean OmegaWorkbench/Test.lean
```

After `lake update`, commit the generated `lake-manifest.json` so the dependency graph stays reproducible.

## What This Starter Does

- pins the Lean toolchain to the current mathlib-compatible version
- pins `mathlib4` to the matching release tag
- provides a tiny `OmegaWorkbench` library surface
- includes one deterministic sanity theorem in `OmegaWorkbench/Test.lean`

## What This Starter Does Not Do

- it does not install LLMLean, LeanCopilot, or any local model runtime
- it does not claim theorem-proving autonomy
- it does not replace `artifacts/prover-results/<run-id>.yaml`

Use `protocol/lean-bootstrap.md` to layer proof-assistant integrations on top of this starter.