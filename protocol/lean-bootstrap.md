# OMEGA Lean 4 Bootstrap Protocol

This protocol documents the verified local Lean 4 + proof-assistant setup for OMEGA formal-math work. All commands and configuration here are grounded in official docs as of April 2026.

## Prerequisites

- VS Code with the [vscode-lean4](https://github.com/leanprover/vscode-lean4) extension
- Git
- A local model runtime (Ollama recommended for Windows; llama.cpp or vLLM for Linux)

## Step 1: Create a mathlib-backed Lean project

From the Lean community docs, non-trivial Lean code should live inside a versioned Lean project, not in isolated `.lean` files.

```bash
lake +v4.29.0 new my_project math
cd my_project
lake update
lake exe cache get
code .
```

> **Note**: OMEGA should track the current mathlib toolchain. As of April 2026, the maintained `mathlib4` `lean-toolchain` points to `leanprover/lean4:v4.29.0`. Check the current mathlib toolchain before bootstrapping a fresh project.

The `math` argument in `lake new` adds mathlib4 as a dependency. The `lake exe cache get` command downloads prebuilt mathlib oleans so you don't rebuild from source.

## OMEGA starter surface

Repository-local starter files live under `templates/lean-starter/`.

Recommended embedding path for a proof-first investigation:

```text
research/active/<problem-id>/proof/lean/
```

After copying the starter surface into that folder:

```bash
lake update
lake exe cache get
lake build OmegaWorkbench
```

Commit the generated `lake-manifest.json` once `lake update` succeeds. This keeps the Lean dependency graph inside the reproducibility boundary.

## Step 2: Install a local model runtime

### Ollama (recommended for Windows and quick setup)

```powershell
irm https://ollama.com/install.ps1 | iex
```

Pull at least one specialized prover model:

```bash
ollama pull bfs-prover-v2
```

Optionally pull a general reasoning model for repair loops:

```bash
ollama pull deepseek-r1:8b
```

### llama.cpp (recommended for GGUF control and benchmarking)

Build from source or use a prebuilt release. Then serve via `llama-server`:

```bash
llama-server -m ./model.gguf --port 8080
```

### vLLM (Linux only, for serving and scale-out)

Only needed when the workflow grows beyond single-user experimentation. See the [vLLM docs](https://docs.vllm.ai/) for deployment.

## Step 3: Wire a proof-assistant integration

Choose one of the following surfaces. LLMLean is recommended for interactive tactic work.

### LLMLean

Add to `lakefile.lean`:

```lean
require llmlean from git
  "https://github.com/cmu-l3/llmlean.git"
```

Configure `~/.config/llmlean/config.toml` (Linux/macOS) or `%APPDATA%\llmlean\config.toml` (Windows):

```toml
api = "ollama"
model = "bfs-prover-v2"
mode = "iterative"
```

LLMLean marks BFS-Prover-V2 as "highly recommended for `llmstep`". See the [LLMLean Ollama models doc](https://github.com/cmu-l3/llmlean/blob/main/docs/ollama-models.md) for additional model options.

Import in your Lean file:

```lean
import LLMlean
```

### LeanCopilot

Provides tactic suggestion, proof search, and premise selection inside Lean. Supports Linux, macOS, Windows, and WSL. Allows both packaged and user-supplied local models.

See the [LeanCopilot repo](https://github.com/lean-dojo/LeanCopilot) for setup.

### Other surfaces

- **llmstep**: minimal proof-state → model loop for tactic suggestion
- **LeanTool**: code-interpreter style Lean interaction via LiteLLM (OpenAI-compatible)
- **UlamAI**: CLI for LLM-guided reasoning with Lean 4 verification; documents Ollama use

## Step 4: First verification loop

Start with a minimal theorem to confirm the full stack works:

```lean
import Mathlib
import LLMlean

example (n : ℕ) : n + 0 = n := by
  llmstep ""
```

If the local model runtime is running and the config is correct, `llmstep` will query the model for tactic suggestions and Lean will verify them.

Before introducing an LLM layer, confirm the starter surface builds deterministically:

```bash
lake build OmegaWorkbench
lake env lean OmegaWorkbench/Test.lean
```

## Step 5: Bridge LeanCopilot to a local/open model endpoint

OMEGA now provides a LeanCopilot-compatible bridge server:

```bash
omega-leancop-bridge --model goedel-prover-v2-32b --base-url http://localhost:8000/v1
```

The bridge exposes:

- `GET /health`
- `POST /generate` (LeanCopilot ExternalGenerator contract)

This is the recommended runtime surface for BYOM tactic generation.

## Step 6: Run verifier-guided proof repair loop

For Lean files containing `sorry`, run bounded iterative repair:

```bash
omega-proof-repair repair research/active/<problem-id>/proof/lean/OmegaWorkbench/Test.lean \
  --model goedel-prover-v2-32b \
  --base-url http://localhost:8000/v1 \
  --max-iterations 32 \
  --in-place
```

The loop applies verifier-guided self-correction:

1. detect first unresolved `sorry`
2. generate tactic candidates
3. re-check with Lean
4. keep only improving candidates
5. stop on verified proof or exhausted budget

## OMEGA conventions on top of this stack

1. **Proof obligations first**: every proof-first research run must populate `input_files/proof_obligations.md` before starting model-assisted search.
2. **Verifier is the judge**: LLM output is a proposal engine. Lean 4 kernel + mathlib is the only authority surface.
3. **Persist artifacts**: failed drafts, verifier logs, and repair attempts are first-class local artifacts; verifier-visible outcomes should be written to `artifacts/prover-results/<run-id>.yaml`.
4. **Version control the project**: `lakefile.lean`, `lean-toolchain`, and `lake-manifest.json` must be committed.
5. **Regression control**: if a proof draft passes, tag the commit. If a later repair attempt breaks it, the tag is the rollback point.

## Model selection guide

| Tier | GPU VRAM | Recommended models |
|------|----------|--------------------|
| CPU-only / iGPU | — | 3B–8B models, lower-bit quants via llama.cpp |
| 8–12 GB | entry | BFS-Prover-V2 7B, DeepSeek-Prover-V2-7B (Q4/Q8) |
| 24 GB | mid | QwQ 32B (Q4), two-model propose+repair loops |
| Multi-GPU / Linux | lab | vLLM serving, larger quants, batch proof search |

## References

- Lean quickstart: https://lean-lang.org/lean4/doc/quickstart.html
- mathlib4 docs: https://leanprover-community.github.io/
- LLMLean: https://github.com/cmu-l3/llmlean
- Ollama: https://ollama.com/
- llama.cpp: https://github.com/ggml-org/llama.cpp
- vLLM: https://docs.vllm.ai/
- OMEGA workstation stack report: `research/OMEGA_LOCAL_WORKSTATION_VIBE_PROVING_STACK_2026_04_04.md`
