# OMEGA Research Intelligence Stack

This reference maps the April 2026 research-intelligence pass onto OMEGA receiver surfaces.
OMEGA stays standalone: these donors and services inform local workflow design, but they are
not vendored as runtime dependencies by default.

Last updated: 2026-04-05 (added neural theorem proving SOTA and execution plan references).

## Open-Source Workflow Donors

| Donor | Verified reusable signal | OMEGA receiver surfaces |
|-------|--------------------------|-------------------------|
| MiroThinker | keep-N-most-recent context retention, trajectory logging, contamination-aware multi-run evaluation | novelty, results, verification, experiment ledger |
| open-researcher | metadata-first search, selective scraping, recursive continuation, lightweight credibility/date heuristics | novelty, literature packet, citation evidence |
| Vane / Perplexica | focus and source routing before search, privacy-first meta-search posture, explicit researcher workflow | novelty, literature routing, verification |
| autoresearch | fixed-budget keep or discard loop, branch-per-run isolation, experiment ledger discipline | plan, experiment, results |
| Paper2Slides | staged paper-to-slides pipeline with source-linked outputs and fast or normal modes | publication, presentation pack |
| create-llm | right-sized project templates, scaffold topology, generated starter surfaces | scaffold contract, workflow packaging |

## Formal-Math and Vibe-Proving Evidence

| Surface | Verified reusable signal | OMEGA receiver surfaces |
|---------|--------------------------|-------------------------|
| arXiv:2602.18918 (VUB vibe-proving) | consumer-LLM proof search with auditable transcripts, versioned drafts, and explicit generate/referee/repair loop | proof-first workflow, referee discipline, proof obligations |
| arXiv:2601.22401 (Gemini / Erdős) | large-scale open-problem screening plus literature-collision and rediscovery risk | novelty, literature packet, citation evidence |
| arXiv:2602.10177 (Aletheia) | autonomy and novelty gradation for long-horizon math agents | control, reporting, transparency metadata |
| Numina-Lean-Agent | open Lean-first proving stack with MCP/LSP tool use and mathematician-facing formalization workflow | future prover lane, Lean bootstrap |
| Lean 4 + mathlib4 + vscode-lean4 | trusted local verifier plus maintained IDE bootstrap for formal mathematics | Lean bootstrap, proof obligations, future prover lane |
| LLMLean / LeanCopilot / llmstep / LeanTool / UlamAI | local or locally targetable proof-assistance loop over Lean proof state and verifier feedback | interactive prover lane, repair loop, workstation workflow |
| Ollama / llama.cpp / vLLM + open prover families | workstation-to-serving continuum for local model execution, quantization-aware deployment, and OpenAI-compatible local endpoints | local runtime policy, benchmark stack, deployment notes |
| vibe-proving-with-llms | minimal verifier-plus-RL training loop in a custom proof language | toy verifier experiments, reward-loop intuition |
| StarExec-ARC | containerized ATP deployment and benchmarking infrastructure | future ATP runner infrastructure |
| arXiv:2601.19532 (Omni-MATH-2) | judge-induced error can dominate evaluation when models outrun judges | verification policy, judge skepticism |

See `research/OMEGA_LOCAL_WORKSTATION_VIBE_PROVING_STACK_2026_04_04.md` for the detailed local-stack synthesis and deployment-tier guidance.

## Neural Theorem Proving SOTA (April 2026)

The April 2026 landscape analysis added frontier neural theorem proving evidence. These
are the strongest external signals for OMEGA's proof lane architecture and execution strategy.

| Surface | Verified reusable signal | OMEGA receiver surfaces |
|---------|--------------------------|-------------------------|
| DeepSeek-Prover-V2 (arXiv:2504.21801, GitHub `deepseek-ai/DeepSeek-Prover-V2`) | 88.9% MiniF2F-test, 49/658 PutnamBench; recursive subgoal decomposition by 671B → individual solving by 7B; RL with Lean 4 compiler as reward | proof-repair loop, two-level architecture (decompose + solve), workstation model selection |
| Kimina-Prover (arXiv:2504.11354, GitHub `MoonshotAI/Kimina-Prover-Preview`) | 80.7% MiniF2F pass@8192; whole-proof generation without MCTS/PRM; Formal Reasoning Pattern (think → formalize → verify); open distilled 1.5B/7B | alternative proof lane, formal reasoning pattern donor, workstation model option |
| LeanCopilot v4.28.0 (arXiv:2404.12534, GitHub `lean-dojo/LeanCopilot`, MIT) | 74.2% proof step automation; `suggest_tactics`, `search_proof`, `select_premises`; ExternalGenerator API for bring-your-own-model | primary integration surface for OMEGA proof lane, model routing API |
| Process Advantage Verifiers (arXiv:2410.08146) | +8% accuracy over outcome reward models, 5-6× sample efficiency in online RL | candidate tactic ranking in proof-repair loop |
| FrontierMath (arXiv:2411.04872, Epoch AI) | SOTA models solve <2% of research-grade math; automated verification; Tier 1-4 + Open Problems | honest calibration surface for OMEGA capability claims |
| AlphaProof (DeepMind blog, Jul 2024) | 4/6 IMO 2024 via Lean 4 + RL (closed-source) | ceiling setter for formal proving ambition |
| LeanDojo / ReProver (arXiv:2306.15626, NeurIPS 2023) | open Lean 4 interaction toolkit, premise retrieval from mathlib4 | foundation layer beneath LeanCopilot |
| LLEMMA (arXiv:2310.10631) | open math-specialized LLMs (7B/34B), Proof-Pile-2 training | baseline for math reasoning without formal-prover fine-tuning |
| ProverBench (DeepSeek repo) | 325 problems, AIME 2024-25 + textbook | T1-T2 tier calibration benchmark |
| PutnamBench (DeepSeek repo) | 658 problems from Putnam Competition, 7.4% solve rate by SOTA | undergraduate+ difficulty calibration |

Companion reports:

- `research/OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md` — full landscape report with verified benchmarks, model comparisons, capability gap analysis, and bibliography
- `research/OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md` — concrete 6-phase execution plan grounded in this landscape
- `research/OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md` — 5-horizon development strategy (2026-2076)
- `research/OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md` — standalone academic reference (25+ papers, 15+ repos, 6 benchmarks)

## External Research Services

### Research-grade support

Use these to improve literature coverage and citation topology, but persist the final evidence locally:

- Elicit
- Scite
- Litmaps
- Inciteful
- ResearchRabbit
- Connected Papers
- SciSpace

### Presentation helper

- WorkPPT

### Tutor-only supplemental surfaces

These may help explain known material, but they are not novelty or verification sources:

- MathGPT Pro / Mathos AI
- Examful

### Explicitly excluded

These conflict with OMEGA research-integrity goals and should not be adopted:

- detector-bypass tools
- AI-humanizer workflows
- authorship-obfuscation utilities

### Unverified on 2026-04-04

These were visible during market reconnaissance but were not confirmed as reliable enough to route into protocol guidance:

- Eaisly AI
- Doco

## Local Artifact Mapping

Every external search or donor-assisted workflow must collapse back into local OMEGA artifacts:

| Need | Local artifact |
|------|----------------|
| bounded problem brief | `input_files/data_description.md` |
| literature packet | `input_files/literature.md` |
| graph-aware literature topology | `input_files/literature_graph.md` |
| supporting and contrasting citation packet | `input_files/citation_evidence.md` |
| proof-first obligation ledger | `input_files/proof_obligations.md` |
| run-by-run experiment trace | `experiments/ledger.yaml` |
| verifier-visible proof outcome | `artifacts/prover-results/<run-id>.yaml` |
| publication or seminar companion deck | `presentation/` |

## Receiver Rules

1. External tools can help with retrieval, ranking, clustering, and slide generation, but the claim-bearing record stays local.
2. Literature positioning requires both supporting and contrasting citations when that evidence is available.
3. Presentation artifacts cannot introduce stronger claims than the stored paper or results artifact supports.
4. Workflow-product donors are useful when they sharpen stage contracts, scaffold topology, or artifact routing. They should not force new runtime scope on OMEGA.
5. Proof-first runs that use LLM assistance should persist a local `proof_obligations.md` covering load-bearing claims, branch/sign/endpoint checks, mechanizable substeps, and deferred risks.
6. A proof-first run that reaches a verifier-visible state should also emit `artifacts/prover-results/<run-id>.yaml`; the experiment ledger and proof result are complementary, not interchangeable.
7. Press coverage and public summaries are secondary evidence; they never outrank the primary paper or the maintained repository artifact.
8. LLM judges are diagnostic tools only. They can help enumerate objections, but they do not count as sufficient proof verification.

## Non-Goals

- vendoring external research-agent runtimes into OMEGA
- treating tutor or detector-evasion surfaces as research evidence
- replacing local reproducibility artifacts with SaaS dashboards or transient search sessions