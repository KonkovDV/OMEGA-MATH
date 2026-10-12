# OMEGA Lean Execution Adapter

Defines the contract for programmatic interaction with Lean 4 from the OMEGA Python runtime.

## Purpose

The Lean execution adapter wraps the Lean 4 CLI (`lake build`, `lean`) and returns structured
machine-readable results. It replaces ad-hoc shell commands with a reproducible, testable surface.

## SOTA Grounding (April 2026)

- **DeepSeek-Prover-V2** (arXiv:2504.21801): recursive subgoal decomposition via large LLM →
  Lean 4 subgoals → independent proving with smaller models → RL training. SOTA 88.9% miniF2F-test.
  The adapter must support individual file checking (subgoal-level), not just full project builds.
- **LeanCopilot** (lean-dojo/LeanCopilot, arXiv:2404.12534): v4.28.0 provides `suggest_tactics`,
  `search_proof`, `select_premises` natively in Lean 4. Bring-your-own-model via Python API server.
  The adapter's `check_file` and `build_project` are the execution substrate that LeanCopilot-style
  tools can be layered on top of.
- **Kimina-Prover** (arXiv:2504.11354): RL-trained formal reasoning models (1.5B/7B distilled).
  80.7% miniF2F pass@8192. The iterative think-formalize-verify pattern requires repeated Lean
  file checks, which this adapter provides.
- **mathlib4** v4.29.0 (leanprover-community/mathlib4): active standard library for Lean 4.
  The adapter must handle mathlib-dependent projects (lake package resolution).

## SOTA Grounding (October 2026)

Tsoukalas et al. (*Science*, 8 October 2026; arXiv:2605.22763) used this same
shape of tool: an LLM writes Lean, the compiler answer comes back, the next
episode continues. Their basic loop solved the same nine Erdős problems as
the evolutionary agent with AlphaProof attached. `check-file` remains the
verification primitive. The adapter does not decide that a compiled file
solves the informal problem; that comparison is `statement_fidelity` on the
prover-result artifact. A file that still contains `sorry` is not a success,
including when the `sorry` sits in a helper lemma.

## Adapter Contract

### Input: `LeanRequest`

```yaml
action: "check-file | build-project | run-command"
lean_file: "<path to .lean file, for check-file>"
project_dir: "<path to Lake project root, for build-project>"
command: "<arbitrary lean/lake command, for run-command>"
timeout_seconds: 120
toolchain: "leanprover/lean4:v4.29.0"  # optional override
env: {}  # optional environment variables
sandbox_mode: "off | auto | required"
```

### Output: `LeanResult`

```yaml
success: true | false
action: "<echoed action>"
exit_code: 0
stdout: "<captured stdout>"
stderr: "<captured stderr>"
duration_seconds: 1.23
errors: []        # list of parsed error objects
warnings: []      # list of parsed warning objects
sandbox_mode: "off | auto | required"
sandbox_applied: true | false
sandbox_tool: "landrun | null"
lean_version: "4.29.0"
```

### Error Object

```yaml
- file: "<file path>"
  line: 42
  column: 10
  severity: "error | warning | info"
  message: "<error message text>"
```

## Actions

### `check-file`

Runs `lean <file>` against the specified Lean file. Parses stdout/stderr for structured
diagnostic messages. Returns success=true if exit code is 0 and no errors are found.

### `build-project`

Runs `lake build` in the specified project directory. Captures output and parses for
build errors. Returns success=true if the project builds cleanly.

### `run-command`

Executes an arbitrary `lean` or `lake` shell command. This is the escape hatch for
commands not covered by the structured actions. The adapter captures output but does
not attempt to parse it.

## Error Parsing

Lean 4 emits diagnostics in the format:
```
<file>:<line>:<col>: error: <message>
```

The adapter parses these into structured error objects. Multi-line messages are
concatenated until the next diagnostic header.

## Timeout Handling

If the subprocess exceeds `timeout_seconds`, the adapter kills it and returns:
```yaml
success: false
exit_code: -1
errors:
  - severity: error
    message: "Lean process timed out after 120 seconds"
```

  If `sandbox_mode: required` and no sandbox runner is available, the adapter returns a non-success result with
  `exit_code: -2` and a descriptive sandbox error.

## Integration Points

- **omega-runner**: `proof-first` runs invoke `check-file` or `build-project` and record
  the `LeanResult` as a prover-result artifact.
- **Prover agent**: uses `check-file` in a bounded generate-and-check loop.
  Subgoal decomposition remains available for an isolated obligation. It is
  not the first pass on an open statement (PROTOCOL.md §1.9).
- **CI/verification-pipeline**: `build-project` confirms that a Lean project compiles
  before accepting a proof draft.

## Future: LeanCopilot Integration

When GPU runtime is available, a future extension can add:
- `action: "suggest-tactics"` — call LeanCopilot's ExternalGenerator API
- `action: "search-proof"` — invoke proof search with configurable model

This is deferred because it requires model download and GPU setup, which is an
environment boundary, not a code boundary.
