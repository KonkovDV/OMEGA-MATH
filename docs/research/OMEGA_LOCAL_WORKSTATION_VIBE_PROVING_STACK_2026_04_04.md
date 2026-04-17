---
title: OMEGA Local Workstation Vibe-Proving Stack
date: 2026-04-04
status: active
version: 1.1.0
last_updated: 2026-04-05
---

# OMEGA Local Workstation Vibe-Proving Stack

## Scope

This companion report answers a narrower question than the main hyperdeep vibe-proving report:

What can a serious local, open-source proof workflow actually look like on a normal workstation in April 2026?

The target is not frontier-scale closed infrastructure. The target is a source-backed, reproducible stack that a researcher can install on a laptop, desktop GPU box, or small Linux workstation and then extend inside OMEGA.

## Evidence Standard

This pass promoted only surfaces that cleared at least one of these bars:

1. official documentation for installation, runtime, or API behavior
2. maintained repository documentation for model or tool integration
3. primary-paper claims when the repo or docs alone were insufficient

This report intentionally avoids unstable claims such as exact token-per-second tables, retail-price narratives, or broad hardware marketing statements that were not confirmed by authority surfaces in this pass.

## Executive Summary

The consumer-workstation version of vibe-proving is real, but it works for a narrower reason than hype often suggests.

The decisive pattern is:

1. a trusted verifier does correctness closure
2. a local LLM proposes tactics, proof sketches, or repairs
3. a thin integration layer feeds verifier feedback back into the model
4. quantized small-to-mid-size models keep the loop local enough to be practical

On a workstation, the strongest open-source lane is not “run the biggest frontier model locally”. It is:

- Lean 4 plus mathlib4 as the kernel of truth
- VS Code plus vscode-lean4 as the interaction surface
- one local proof assistant layer such as LLMLean, LeanCopilot, llmstep, LeanTool, or UlamAI
- one local runtime such as Ollama or llama.cpp, with vLLM reserved for Linux or WSL serving and scale-out scenarios
- one small specialized prover or one general reasoning model used as a candidate generator, never as the final judge

## Why This Works Locally

Three technical facts explain most of the feasibility story.

### 1. Quantization moved the memory wall

The llama.cpp project explicitly supports integer quantization from 1.5-bit through 8-bit, with the stated goal of reducing memory use and enabling inference across a wide range of hardware. That is the core reason workstation deployment is viable.

### 2. The verifier collapses hallucination risk into a search problem

Lean 4 remains a binary checker: a proof term or tactic script either elaborates and checks or it does not. That means the local LLM can be treated as a proposal engine inside a trusted symbolic loop rather than as an authority surface.

### 3. Open runtimes are now mature enough to hide most systems friction

Ollama provides one-command local pulling, a default localhost API, and OpenAI-compatible endpoints. llama.cpp provides a lower-level GGUF-native backend with broad CPU and GPU support. vLLM provides the serving-grade end of the stack when the local workflow grows beyond single-user experimentation.

## Architecture Map

```text
┌──────────────────────────────────────────────────────────────┐
│                 LOCAL VIBE-PROVING STACK                    │
├──────────────────────────────────────────────────────────────┤
│ Layer 1: IDE and Verifier UX                                │
│   VS Code + vscode-lean4 | live.lean-lang.org              │
├──────────────────────────────────────────────────────────────┤
│ Layer 2: Lean Toolchain                                     │
│   elan | Lake | Lean 4 project | mathlib4                   │
├──────────────────────────────────────────────────────────────┤
│ Layer 3: Proof-Assistant Integration                        │
│   LLMLean | LeanCopilot | llmstep | LeanTool | UlamAI       │
├──────────────────────────────────────────────────────────────┤
│ Layer 4: Local Model Runtime                                │
│   Ollama | llama.cpp | vLLM                                 │
├──────────────────────────────────────────────────────────────┤
│ Layer 5: Candidate Generators                               │
│   BFS-Prover-V2 | DeepSeek-Prover-V2-7B | Goedel-Prover     │
│   plus optional general reasoning models for repair         │
├──────────────────────────────────────────────────────────────┤
│ Layer 6: Trusted Closure                                    │
│   Lean 4 kernel + mathlib4 + explicit proof-obligation logs │
└──────────────────────────────────────────────────────────────┘
```

## Layer-by-Layer Findings

### Layer 1. IDE and Base Lean Surface

Verified base surfaces:

- Lean quickstart recommends installation through the official Lean tooling and VS Code workflow.
- The Lean community docs recommend creating or opening Lean projects from VS Code and expose the browser surface at live.lean-lang.org for no-install experiments.
- The official vscode-lean4 repository is the maintained VS Code extension surface for Lean 4.

Practical implication for OMEGA:

The IDE contract is already solved. OMEGA does not need to invent a custom frontend for early proof work. It needs a disciplined project bootstrap and artifact policy on top of the standard Lean workflow.

### Layer 2. Lean 4, Lake, and mathlib4

Verified bootstrap path from Lean community docs:

```bash
lake +v4.29.0 new my_project math
cd my_project
lake update
lake exe cache get
code .
```

Key points from the docs:

- non-trivial Lean code should live inside a Lean project, not in isolated files
- `math` in the `lake new` command adds mathlib4 as a dependency
- `lake exe cache get` is the expected cache bootstrap for mathlib-based projects

Practical implication for OMEGA:

Any future prover lane should start with a versioned Lean project scaffold and treat `lakefile.*`, `lean-toolchain`, and cache setup as part of the reproducibility boundary.

### Layer 3. Proof-Assistant Integration Surfaces

#### LLMLean

Verified signals from the maintained repository:

- integrates LLMs with Lean for tactic suggestion and proof completion
- supports local Ollama backends
- documents both parallel generation and iterative refinement modes
- explicitly added BFS-Prover-V2 and Kimina support through Ollama in 2025

Why it matters:

LLMLean is the clearest workstation-grade bridge from a local model runtime into day-to-day Lean proof repair.

#### LeanCopilot

Verified signals:

- provides tactic suggestion, proof search, and premise selection inside Lean
- supports Linux, macOS, Windows, and Windows WSL
- allows either packaged models or user-supplied local models

Why it matters:

LeanCopilot is the strongest general-purpose Lean-native copilot surface in this pass if OMEGA wants a maintained, formal-math-first assistant rather than a custom orchestration layer.

#### llmstep

Verified signals:

- model-agnostic tactic suggester
- tactic sends proof state to a server, which calls a language model and returns suggestions
- server can run in the user’s own environment, including local CPU or GPU

Why it matters:

llmstep is still useful as the minimal proof-state to model loop even if more capable copilot layers exist.

#### LeanTool

Verified signals:

- positions itself as a “code interpreter” for Lean
- uses LiteLLM, so it can target local runtimes that expose OpenAI-compatible APIs
- is designed to let models directly interact with Lean and self-correct syntax or proof mistakes

Why it matters:

LeanTool is one of the cleanest routes into an MCP-friendly or Cursor-style agent workflow for Lean.

#### UlamAI

Verified signals:

- CLI for LLM-guided reasoning with Lean 4 verification
- documents fully local use through Ollama
- works with Codex, Claude Code, and Ollama-based configurations

Why it matters:

UlamAI is the most explicit “truth-first CLI” surface in this pass for users who want a shell-driven prover workflow rather than an editor-only tactic assistant.

### Layer 4. Local Model Runtimes

#### Ollama

Verified signals:

- native Windows installer is documented by Ollama and exposes GPU acceleration plus the local API on `http://localhost:11434`
- OpenAI-compatible endpoints are documented at `/v1/*`
- documented Modelfile instructions include `FROM`, `PARAMETER`, and `SYSTEM`
- context-size overrides are explicitly done through a custom Modelfile with `PARAMETER num_ctx`

Why it matters:

For Windows and general workstation use, Ollama is the shortest path from “no local model runtime” to “usable OpenAI-compatible local endpoint for proof assistance”.

Minimal theorem-oriented Modelfile pattern grounded in the docs:

```text
FROM deepseek-r1:14b
PARAMETER num_ctx 32768
PARAMETER temperature 0.2
PARAMETER top_k 50
PARAMETER top_p 0.95
SYSTEM """
You assist with Lean 4 proof search.
Return Lean 4 tactics, candidate lemmas, or proof sketches.
Prefer concise, checkable progress over free-form prose.
"""
```

Create and run it with:

```bash
ollama create theorem-prover -f ./Modelfile
ollama run theorem-prover
```

#### llama.cpp

Verified signals:

- described by its maintainers as enabling LLM inference with minimal setup and strong performance on a wide range of hardware
- supports GGUF, integer quantization from 1.5-bit to 8-bit, CPU plus GPU hybrid inference, and many hardware backends
- includes `llama-server`, an OpenAI-compatible HTTP server, and `llama-bench` for local measurement

Why it matters:

llama.cpp is the fallback and control surface OMEGA should trust when it needs explicit control over GGUF weights, benchmarking, CPU-only experiments, or hybrid CPU/GPU deployment.

#### vLLM

Verified signals:

- positions itself as a fast library for LLM inference and serving
- documents OpenAI-compatible serving, deployment, scaling, and quantization features
- supports Linux GPU and CPU variants, with Windows requiring WSL or community-maintained forks

Why it matters:

vLLM is not the first workstation runtime for a Windows user. It is the scale-up runtime once OMEGA wants serving discipline, bigger batch throughput, or Linux-backed shared infrastructure.

### Layer 5. Model Families Worth Tracking

#### BFS-Prover-V2

Verified signals:

- ByteDance-Seed presents BFS-Prover-V2 as a step-level theorem prover for Lean 4
- the repository states SOTA step-level results on miniF2F and ProofNet
- LLMLean explicitly documents support for BFS-Prover-V2 through Ollama

Why it matters:

BFS-Prover-V2 is the clearest specialist model family for an interactive local Lean lane.

#### DeepSeek-Prover-V2

Verified signals:

- paper reports a 7B model and a much larger 671B model
- architecture is based on subgoal decomposition and recursive proof construction
- the 7B Hugging Face model card exists as an open deployment surface

Why it matters:

The 7B variant is the realistic workstation target. The 671B line is useful as a capability reference, not as the default local deployment story.

#### Goedel-Prover

Verified signals:

- Princeton repository is Apache-2.0 licensed
- repo documents a 7B prover and a large-scale autoformalization and proof-data pipeline
- published evaluation claims are stated directly in the repo and associated papers

Why it matters:

Goedel-Prover is one of the strongest open model families for OMEGA to benchmark against the Lean-specific stack.

#### Leanstral and Kimina

Status in this pass:

- Leanstral is visible as an April 2026 paper and Hugging Face search result for a Lean-oriented 7B line, but this pass did not rely on a maintained repository README for integration claims.
- Kimina-Prover is visible through Hugging Face model search and through LLMLean’s documented Ollama support. The April 2026 SOTA follow-on also adds stronger evidence through the Kimina-Lean-Server and LeanCopilot v4.28.0 ExternalGenerator integration, so OMEGA should now treat Kimina-Prover as a promoted Tier-1 alternative proving lane rather than a watchlist-only surface.

Why this matters:

Leanstral should remain on OMEGA’s watchlist until its maintained integration docs are part of the same evidence chain as BFS, DeepSeek-Prover, or Goedel-Prover. Kimina-Prover now belongs in the promoted set, but with a newer and somewhat more indirect integration trail than BFS, DeepSeek-Prover, or Goedel-Prover.

#### General reasoning models

Verified signals from the Ollama library:

- DeepSeek-R1 is available in multiple sizes from 1.5B through 671B
- QwQ is available as a 32B reasoning model

Why it matters:

These are useful for strategy generation and proof repair, but they should be treated as general reasoning assistants around the verifier loop, not as proof checkers.

## Deployment Tiers That Actually Make Sense

The right way to size a workstation stack is not to copy a viral hardware table. It is to reason from model size, quantization level, and runtime overhead.

Approximate weight-memory rule:

$$
\text{weight memory} \approx \text{parameter count} \times \frac{\text{bits per weight}}{8}
$$

This is only the weight footprint. Real runtime memory is higher because of KV cache, context length, batching, and backend overhead.

### Tier A. CPU-only or integrated GPU

Recommended use:

- small general reasoning models
- tactic suggestion
- proof repair on short contexts
- verifier-first experiments where Lean does the heavy filtering

Reasonable target band:

- roughly 3B to 8B models in lower-bit quantized formats

Best runtime:

- llama.cpp first
- Ollama when the model exists in its library and convenience matters more than low-level tuning

### Tier B. 8 to 12 GB GPU class

Recommended use:

- entry-level local proving workstation
- 7B specialized prover models in Q4 or Q8 style formats
- 14B general reasoning models in more compressed settings

Best fit:

- BFS-Prover-V2 7B class
- DeepSeek-Prover-V2-7B class
- general repair model alongside Lean verification

### Tier C. 24 GB GPU or large unified-memory laptop/desktop

Recommended use:

- stronger general reasoning models in the 24B to 32B band with quantization
- two-model workflows where one model proposes and another repairs or summarizes Lean feedback

Best fit:

- QwQ 32B class reasoning models
- larger repair loops around a smaller specialized prover

### Tier D. Larger Linux workstation or multi-GPU research box

Recommended use:

- vLLM-based serving
- benchmarking larger quantized models
- multi-user or batched proof-search services

Important correction:

This is where the stack starts to look like a local lab service, not a single-user “ordinary PC” setup. OMEGA should treat this as a scale-up lane, not as the baseline story.

## Cross-Platform Quickstart

### Windows-first path

1. Install Lean via the official Lean quickstart and the VS Code Lean workflow.
2. Create a mathlib-backed project.

```bash
lake +v4.29.0 new my_project math
cd my_project
lake update
lake exe cache get
code .
```

> **Note**: The maintained `mathlib4` toolchain was already on `leanprover/lean4:v4.29.0` in the April 2026 source pass. Check the current mathlib toolchain before bootstrapping a new project.

3. Install Ollama from the official Windows installer or PowerShell bootstrap.

```powershell
irm https://ollama.com/install.ps1 | iex
```

4. Pull a specialized prover model (and optionally a general reasoning model for repair).

```bash
ollama pull bfs-prover-v2
ollama pull deepseek-r1:8b   # optional: general reasoning for repair loops
```

5. If using LLMLean, add the dependency in the Lean project and point `~/.config/llmlean/config.toml` at the Ollama model.

```toml
api = "ollama"
model = "bfs-prover-v2"
mode = "iterative"
```

LLMLean's own documentation marks BFS-Prover-V2 as "highly recommended for `llmstep`". See the [LLMLean Ollama models doc](https://github.com/cmu-l3/llmlean/blob/main/docs/ollama-models.md) for additional model options and configuration keys.

6. Start with a minimal theorem and keep the loop verifier-first.

```lean
import Mathlib
import LLMlean

example (n : ℕ) : n + 0 = n := by
  llmstep ""
```

### Linux or macOS path

Use the same Lean bootstrap path, then either:

- Ollama for the convenience route
- llama.cpp for GGUF-native control and benchmarking
- vLLM when the workflow needs Linux serving, batching, or scale-out deployment

## Promoted vs Secondary Surfaces

### Promoted in this pass

- Lean 4
- mathlib4 project bootstrap
- vscode-lean4
- LLMLean
- LeanCopilot
- llmstep
- LeanTool
- UlamAI
- Ollama
- llama.cpp
- vLLM
- BFS-Prover-V2
- DeepSeek-Prover-V2-7B line
- Goedel-Prover
- Kimina-Prover

### Secondary or watchlist only

- Leanstral
- ProofGym
- miniF2F-Dafny
- DL4TP survey repo

These are useful, visible, or promising, but this pass did not elevate them to the same operational status because their integration evidence was weaker, newer, or more indirect.

### Explicitly not promoted as authority claims

- exact consumer hardware token-per-second tables
- “Mac mini for X dollars runs Y parameter class” narratives
- broad claims that frontier MoE systems are ordinary-PC local workloads

Those may become true in narrow configurations, but they were not the kind of claims this pass was willing to anchor into OMEGA protocol guidance.

## OMEGA Implications

The correct first local prover lane for OMEGA is now clearer.

1. Standardize on Lean 4 plus mathlib project scaffolds.
2. Treat proof assistance as a local candidate-generation loop over a trusted verifier.
3. Prefer Ollama for Windows-friendly local experiments, llama.cpp for fallback or benchmark control, and vLLM only for Linux-backed service scale.
4. Start benchmark work with 7B-class specialized prover models and only then add larger reasoning models for repair or strategy synthesis.
5. Store proof obligations, failed drafts, verifier logs, and repair attempts as first-class local artifacts.

## Bottom Line

The workstation story is no longer “prove frontier mathematics by brute-forcing giant local models”.

The real local breakthrough is that an ordinary machine can now host the full candidate-generation side of a verifier-driven proof workflow. That is enough to make formal-math experimentation, tactic repair, bounded theorem exploration, and auditable proof-search pipelines realistic for OMEGA without needing frontier-lab infrastructure.

## Addendum: April 2026 SOTA Integration (2026-04-05)

The April 2026 landscape analysis produced three companion documents that extend and ground
this workstation stack report in external evidence:

- `OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md` — full SOTA landscape with verified benchmarks
- `OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md` — concrete phased execution plan
- `OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md` — 5-horizon roadmap (2026-2076)

### Key Updates to Model Families

| Model | Status change | Evidence |
|-------|--------------|----------|
| **Kimina-Prover-72B** | Watchlist → Tier-1 promoted | 80.7% MiniF2F pass@8192; Formal Reasoning Pattern verified; open distilled 1.5B/7B; LeanCopilot integration confirmed |
| **DeepSeek-Prover-V2-7B** | Remains Tier-1 promoted (strengthened) | 88.9% MiniF2F-test by 671B sibling; 7B variant is recommended OMEGA workstation model; 32K context; GGUF-quantizable |
| **Kimina-Prover-Distill-7B** | New entry: Tier-1 promoted | Distilled from 72B via RL; available on HuggingFace AI-MO; workstation-deployable |

### Integration Strategy Update

LeanCopilot v4.28.0 is now the recommended primary integration surface for OMEGA's proof lane.
The ExternalGenerator Python API server allows routing through any local backend (Ollama, vLLM,
llama.cpp) without building a custom Lean-LLM bridge.

The recommended two-level architecture (from DeepSeek-Prover-V2):
1. Large model (API-hosted 72B+ or DeepSeek-V2-671B) decomposes theorem into subgoals
2. Local 7B model solves each subgoal through proof-repair loop via LeanCopilot

### Benchmark Calibration Update

| Benchmark | SOTA | OMEGA reading |
|-----------|------|--------------|
| MiniF2F-test (244) | 88.9% (DeepSeek-V2-671B) | Approaching saturation; use as calibration baseline only |
| PutnamBench (658) | 49 solved (7.4%) | Gap indicator for undergraduate+ proving |
| ProverBench (325) | Strong (exact TBD) | Useful T1-T2 calibration |
| FrontierMath | <2% SOTA | Honest calibration: OMEGA should target T1-T2 subproblems only |