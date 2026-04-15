---
title: "OMEGA SOTA Bibliography"
status: active
version: "1.0.0"
last_updated: "2026-04-05"
date: "2026-04-05"
role: reference
audience: internal+academic
tags: [omega, bibliography, SOTA, formal-proving, neural-theorem-proving, research-agents, benchmarks]
evidence_class: E1
---

# OMEGA SOTA Bibliography (April 2026)

## Purpose

This is the consolidated academic reference for all OMEGA protocol, roadmap, and execution
decisions. Every entry is grounded in a primary paper, a maintained repository, or an official
standards document. Press narratives and secondary commentary are excluded.

This bibliography accompanies:

- `OMEGA_SOTA_FORMAL_PROVING_LANDSCAPE_2026_04_05.md` — full landscape report
- `OMEGA_6_PHASE_EXECUTION_PLAN_2026_04_05.md` — execution plan
- `OMEGA_DEVELOPMENT_ROADMAP_2026_04_05.md` — 5-horizon roadmap

## Citation Policy

OMEGA uses a three-tier evidence classification:

| Class | Definition | Admissible in |
|-------|-----------|---------------|
| **E1** | Official external authority: primary arXiv papers, maintained repos, NIST/ISO standards | Protocol, execution plan, roadmap, claims |
| **E2** | Qualified external comparison: benchmark results, reproducible evaluations, blog-only announcements | Calibration surfaces, gap analysis |
| **H** | Hypothesis: projections, roadmap items, unverified claims | Future horizons, speculative architecture |

---

## 1. Neural Theorem Proving

### 1.1 Primary Papers

1. **DeepSeek-Prover-V2**
   DeepSeek-AI. *DeepSeek-Prover-V2: Advancing Formal Mathematical Reasoning via Reinforcement Learning for Subgoal Decomposition.* 2025.
   - GitHub: [`deepseek-ai/DeepSeek-Prover-V2`](https://github.com/deepseek-ai/DeepSeek-Prover-V2)
   - Evidence class: E1
   - Key result: 88.9% MiniF2F-test, 49/658 PutnamBench
   - Architecture: recursive subgoal decomposition (671B → 7B) + RL with Lean 4 compiler as reward
   - OMEGA role: dominant paradigm for formal proving; two-level architecture; workstation 7B variant

2. **Kimina-Prover**
   Wang, H., Unsal, M., Lin, X., Baksys, M., Liu, J., Dos Santos, M., Sung, F., Vinyes, M., Ying, Z., et al. *Kimina-Prover Preview: Towards Large Formal Reasoning Models with Reinforcement Learning.* arXiv:2504.11354 [cs.AI], April 2025.
   - GitHub: [`MoonshotAI/Kimina-Prover-Preview`](https://github.com/MoonshotAI/Kimina-Prover-Preview)
   - Evidence class: E1
   - Key result: 80.7% MiniF2F pass@8192 (72B), open-weight distilled 1.5B/7B
   - Architecture: whole-proof generation, Formal Reasoning Pattern (think → formalize → verify), no MCTS
   - OMEGA role: alternative proof lane; workstation model option; Kimina-Lean-Server for verification

3. **LeanCopilot**
   Song, P., Yang, K., Anandkumar, A. *Lean Copilot: Large Language Models as Copilots for Theorem Proving in Lean.* arXiv:2404.12534. Published at NeuS 2025.
   - GitHub: [`lean-dojo/LeanCopilot`](https://github.com/lean-dojo/LeanCopilot) — MIT License
   - Evidence class: E1
   - Key result: automates 74.2% of proof steps; ExternalGenerator API for bring-your-own-model
   - Current version: v4.28.0 (tracks Lean 4 v4.28.0 stable)
   - OMEGA role: **primary integration surface** for proof lane; replaces need for custom Lean-LLM bridge

4. **LeanDojo / ReProver**
   Yang, K., Swope, A., Gu, A., Chalapathy, R., Song, P., Yu, S., Godil, S., Prenger, R., Anandkumar, A. *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models over Lean.* arXiv:2306.15626. NeurIPS 2023.
   - GitHub: [`lean-dojo/LeanDojo`](https://github.com/lean-dojo/LeanDojo)
   - Evidence class: E1
   - Key contribution: open-source Lean 4 interaction toolkit; premise retrieval from mathlib4
   - OMEGA role: foundation layer beneath LeanCopilot

5. **LLEMMA**
   Azerbayev, Z., Schoelkopf, H., Paster, K., Dos Santos, M., McAleer, S., Jiang, A.Q., Deng, J., Biderman, S., Welleck, S. *LLEMMA: An Open Language Model For Mathematics.* arXiv:2310.10631, 2023.
   - Evidence class: E1
   - Key contribution: open math-specialized LLMs (7B/34B), Proof-Pile-2 training
   - OMEGA role: baseline for math reasoning without formal-prover fine-tuning

6. **Process Advantage Verifiers (PAVs)**
   Lu, S., et al. *Process Advantage Verifiers.* arXiv:2410.08146, 2024.
   Luo, L., et al. *Improve Mathematical Reasoning in Language Models by Automated Process Supervision.* arXiv:2406.06592, 2024.
   - Evidence class: E1
   - Key finding: +8% accuracy over outcome reward models; 5-6× sample efficiency in online RL
   - OMEGA role: step-level scoring for candidate tactic ranking in proof-repair loop

7. **AlphaProof**
   DeepMind. *AI achieves silver-medal standard solving International Mathematical Olympiad problems.* Blog post, July 2024.
   - Evidence class: E2 (no peer-reviewed paper)
   - Key claim: 4/6 IMO 2024 problems via Lean 4 + RL (closed-source)
   - OMEGA role: ceiling setter; validates Lean 4 + RL paradigm

8. **FunSearch**
   Romera-Paredes, B., Barekatain, M., Novikov, A., Balog, M., Kumar, M.P., Dupont, E., Ruíz, F.J.R., Brockschmidt, M., Vinyals, O., de Freitas, N. *Mathematical discoveries from program search with large language models.* Nature, January 2024.
   - Evidence class: E1
   - Key result: new cap set upper bounds via LLM-guided evolutionary program search
   - OMEGA role: demonstrates LLM utility for experimental mathematics

### 1.2 Maintained Repositories (Proof Ecosystem)

| Repository | License | OMEGA role |
|-----------|---------|----------|
| [`deepseek-ai/DeepSeek-Prover-V2`](https://github.com/deepseek-ai/DeepSeek-Prover-V2) | Open-weight | SOTA formal prover; workstation 7B variant |
| [`MoonshotAI/Kimina-Prover-Preview`](https://github.com/MoonshotAI/Kimina-Prover-Preview) | Open-weight | Alternative formal prover; distilled 1.5B/7B |
| [`lean-dojo/LeanCopilot`](https://github.com/lean-dojo/LeanCopilot) | MIT | Primary integration surface |
| [`lean-dojo/LeanDojo`](https://github.com/lean-dojo/LeanDojo) | MIT | Lean 4 interaction toolkit |
| [`project-numina/kimina-lean-server`](https://github.com/project-numina/kimina-lean-server) | Open-source | Lean verification backend |
| [`cmu-l3/llmlean`](https://github.com/cmu-l3/llmlean) | Open-source | LLM-Lean bridge with Ollama |
| [`wellecks/llmstep`](https://github.com/wellecks/llmstep) | Open-source | Model-agnostic tactic suggester |
| [`leanprover-community/mathlib4`](https://github.com/leanprover-community/mathlib4) | Apache-2.0 | Standard math library for Lean 4 |
| [`bytedance-seed/BFS-Prover`](https://github.com/bytedance-seed/BFS-Prover) | Open-weight | Step-level theorem prover |
| [`Goedel-LM/Goedel-Prover`](https://github.com/Goedel-LM/Goedel-Prover) | Apache-2.0 | Open prover + autoformalization |

---

## 2. Research-Agent Systems

9. **Denario**
   Villaescusa-Navarro, F., Bolliet, B., Villanueva-Domingo, P., Bayer, A.E., et al. *The Denario project: Deep knowledge AI agents for scientific discovery.* arXiv:2510.26887, 2025.
   - GitHub: [`AstroPilot-AI/Denario`](https://github.com/AstroPilot-AI/Denario)
   - Evidence class: E1
   - OMEGA role: architectural donor for modular pipeline (idea → novelty → methods → results → paper → referee)

10. **Agents4Science (Denario acceptance evidence)**
    OpenReview: [`LENY7OWxmN`](https://openreview.net/forum?id=LENY7OWxmN#discussion)
    - Evidence class: E2
    - OMEGA role: confirms at least one Denario paper was accepted; reviews are mixed and substantive

11. **CMBAgent**
    Xu, L., Sarkar, M., Lonappan, A.I., Zubeldia, Í., Villanueva-Domingo, P., Casas, S., et al. *Open Source Planning & Control System with Language Agents for Autonomous Scientific Discovery.* arXiv:2507.07257, 2025. Precursor: arXiv:2412.00431, 2024.
    - GitHub: [`CMBAgents/cmbagent`](https://github.com/CMBAgents/cmbagent)
    - Evidence class: E1
    - OMEGA role: planning/control runtime donor; `deep_research` workflow with context carryover

12. **LSST DESC AI/ML Roadmap**
    LSST DESC. *AI/ML Roadmap.* arXiv:2601.14235, 2026.
    - Evidence class: E1
    - OMEGA role: requirements for uncertainty quantification, validation, robustness, reproducibility

13. **Aletheia / Autonomous Math Research**
    Feng, T., Trinh, T.H., Bingham, G., Hwang, D., et al. *Towards Autonomous Mathematics Research.* arXiv:2602.10177, 2026.
    - Evidence class: E1
    - Key contribution: autonomy and novelty gradation for math research agents
    - OMEGA role: reporting transparency; long-horizon research-agent architecture

14. **Gemini on Erdős Problems**
    Feng, T., Trinh, T., Bingham, G., Kang, J., et al. *Semi-Autonomous Mathematics Discovery with Gemini: A Case Study on the Erdős Problems.* arXiv:2601.22401, 2026.
    - Evidence class: E1
    - Key finding: of 13 addressed problems, 8 had existing solutions in the literature; literature collision is first-class risk
    - OMEGA role: mandatory anti-rediscovery checking; novelty verification

15. **Numina-Lean-Agent**
    Liu, T., et al. *Numina-Lean-Agent.* arXiv:2601.14027, 2026.
    - Evidence class: E1
    - Key contribution: open Lean-first formal-math agent; Putnam 12/12 claim; Brascamp-Lieb formalization
    - OMEGA role: future prover lane architecture reference

---

## 3. Vibe-Proving and Proof Workflow

16. **VUB Vibe-Proving Case Study**
    Verbeken, B., Vagenende, B., Guerry, M.-A., Algaba, A., Ginis, V. *Early Evidence of Vibe-Proving with Consumer LLMs: A Case Study on Spectral Region Characterization with ChatGPT-5.2 (Thinking).* arXiv:2602.18918, 2026.
    - Evidence class: E1
    - Key contribution: consumer-LLM (ChatGPT) materially assisted human-verified proof; 7 shareable threads; 4 versioned drafts; explicit generate → referee → repair loop
    - OMEGA role: vibe-proving workflow donor; proves consumer LLMs are useful proposal engines within formally verified loops

---

## 4. Benchmarks and Calibration

17. **MiniF2F**
    Zheng, K., Han, J.M., Polu, S. *MiniF2F: a cross-system benchmark for formal olympiad-level mathematics.* ICLR 2022.
    - Evidence class: E1
    - OMEGA reading: approaching saturation (88.9% SOTA); use as calibration baseline, not research target

18. **PutnamBench**
    DeepSeek-Prover-V2 repository. 658 problems from Putnam Competition.
    - Evidence class: E1
    - OMEGA reading: 49/658 = 7.4% shows gap between competition and research-grade proving

19. **ProverBench**
    DeepSeek-Prover-V2 repository. 325 problems (AIME 2024-25 + textbook).
    - Evidence class: E1
    - OMEGA reading: useful for T1-T2 tier calibration

20. **FrontierMath**
    Glazer, E., Erdil, E., Besiroglu, T., Chicharro, D., Chen, E., Gunning, A., Falkman Olsson, C., Denain, J.-S., et al. *FrontierMath: A Benchmark for Evaluating Advanced Mathematical Reasoning in AI.* arXiv:2411.04872 [cs.AI], November 2024 (v7 December 2025).
    - Evidence class: E1
    - Key result: SOTA models solve **under 2%** of research-grade math problems
    - Tier structure: 1-3 (undergrad → early postdoc), 4 (research-level), Open Problems
    - OMEGA role: honest calibration surface; target T1-T2 subproblems; FrontierMath Open Problems aspirational only

21. **Omni-MATH-2 / Judge Saturation**
    Ballon, B., et al. *Omni-MATH-2.* arXiv:2601.19532, 2026.
    - Evidence class: E1
    - Key finding: judge-induced error dominates evaluation once models outrun judges; LLM judging is systematically biased
    - OMEGA role: LLM judging is diagnostic only; formal verification (Lean compiler, SAT solvers) must be ground truth

---

## 5. Formal Assurance and Standards

22. **NIST Post-Quantum Cryptography Standards**
    NIST. FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), 2024.
    - Evidence class: E1
    - OMEGA role: strongest near-term applied formal-assurance wedge; creates sustained demand for formal verification of PQC implementations

---

## 6. Local Workstation Tool Ecosystem

### 6.1 Proof Assistants and Lean Tooling

| Tool | Source | OMEGA role |
|------|--------|----------|
| Lean 4 | [`leanprover/lean4`](https://github.com/leanprover/lean4) | Trusted proof substrate |
| mathlib4 | [`leanprover-community/mathlib4`](https://github.com/leanprover-community/mathlib4) | Standard math library |
| vscode-lean4 | [`leanprover/vscode-lean4`](https://github.com/leanprover/vscode-lean4) | IDE surface |
| elan | [`leanprover/elan`](https://github.com/leanprover/elan) | Lean toolchain manager |
| Lake | Built into Lean 4 distribution | Build system |

### 6.2 Proof-Assistant Integration

| Tool | Source | OMEGA role |
|------|--------|----------|
| LLMLean | [`cmu-l3/llmlean`](https://github.com/cmu-l3/llmlean) | Workstation-grade Lean-LLM bridge |
| LeanCopilot | [`lean-dojo/LeanCopilot`](https://github.com/lean-dojo/LeanCopilot) | Primary integration surface |
| llmstep | [`wellecks/llmstep`](https://github.com/wellecks/llmstep) | Minimal proof-state to model loop |
| LeanTool | GitHub maintained | MCP-friendly Lean code interpreter |
| UlamAI | [`UlamAI`](https://github.com/UlamAI) | CLI for LLM + Lean 4 verification |

### 6.3 Local Model Runtimes

| Runtime | Source | OMEGA role |
|---------|--------|----------|
| Ollama | [`ollama/ollama`](https://github.com/ollama/ollama) | Shortest path to local proving on Windows |
| llama.cpp | [`ggerganov/llama.cpp`](https://github.com/ggerganov/llama.cpp) | GGUF-native backend for benchmarking |
| vLLM | [`vllm-project/vllm`](https://github.com/vllm-project/vllm) | Scale-up serving for Linux |

### 6.4 Open Prover Model Families

| Model Family | Parameters | Open-Weight | OMEGA Tier |
|-------------|-----------|-------------|-----------|
| DeepSeek-Prover-V2-7B | 7B | Yes (HuggingFace) | Tier-1 promoted (recommended workstation model) |
| DeepSeek-Prover-V2-671B | 671B (MoE) | Yes (HuggingFace) | Tier-1 promoted (API-hosted decomposition) |
| Kimina-Prover-72B | 72B | Yes (HuggingFace) | Tier-1 promoted (alternative proving) |
| Kimina-Prover-Distill-7B | 7B | Yes (HuggingFace AI-MO) | Tier-1 promoted (workstation alternative) |
| Kimina-Prover-Distill-1.5B | 1.5B | Yes (HuggingFace AI-MO) | Tier-1 promoted (lightweight) |
| BFS-Prover-V2 | 7B class | Yes | Tier-1 promoted (step-level prover) |
| Goedel-Prover | 7B | Yes (Apache-2.0) | Tier-1 promoted (autoformalization) |
| LLEMMA | 7B/34B | Yes | Baseline (general math reasoning) |
| DeepSeek-R1 | 1.5B–671B | Yes | General reasoning for repair loops |

---

## 7. Research-Intelligence Workflow Donors

23. **MiroThinker** — context retention, trajectory logging, contamination-aware evaluation
24. **open-researcher** — metadata-first search, selective scraping, recursive continuation
25. **Vane / Perplexica** — focus and source routing, privacy-first meta-search
26. **autoresearch** — fixed-budget keep-or-discard loop, branch-per-run isolation
27. **Paper2Slides** — staged paper-to-slides pipeline
28. **create-llm** — right-sized project templates, scaffold topology

---

## 8. External Research Services

### Research-Grade Support (Optional)

| Service | Role | Integration |
|---------|------|------------|
| Semantic Scholar | Mandatory for novelty verification | Free API, 100 req/sec |
| arXiv API | Fresh preprint search | Free REST API |
| Elicit | Literature discovery | Optional external |
| Scite | Citation context analysis | Optional external |
| Litmaps | Citation topology visualization | Optional external |
| Inciteful | Citation network discovery | Optional external |
| ResearchRabbit | Related paper recommendations | Optional external |
| Connected Papers | Visual similarity graph | Optional external |
| SciSpace | Paper explanation and summarization | Optional external |

### Explicitly Excluded

- Detector-bypass tools
- AI-humanizer workflows
- Authorship-obfuscation utilities

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-04-05 | Initial consolidated bibliography from OMEGA April 2026 audit |
