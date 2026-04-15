# OMEGA Orchestrator Contract

## Overview

The OMEGA agent orchestrator (`scripts/agent_orchestrator.py`, CLI: `omega-orchestrate`)
executes the 7-agent team workflow as a bounded, auditable LLM-backed pipeline.

It is not an autonomous research system. It is a dispatcher that:
1. Loads agent role definitions from `agents/*.yaml`
2. Assembles problem context from registry + workspace
3. Constructs structured prompts for each pipeline stage
4. Invokes an LLM backend via the model router (`scripts/model_router.py`)
5. Parses structured YAML output artifacts from the response
6. Persists artifacts with SHA-256 checksums to the workspace

## Pipeline Stages

The orchestrator supports 8 stages, each mapped to one agent role:

| Stage | Role | Primary output |
|-------|------|----------------|
| `brief` | planner | Research brief, success criteria, budget estimate |
| `novelty` | librarian | Literature memo, prior-work packet, known bounds |
| `triage` | planner | Amenability assessment, tier classification |
| `plan` | planner | Phased research plan, method specification |
| `experiment` | experimentalist | Experiment design, parameters, expected outputs |
| `prove` | prover | Proof strategy, lemmas, formal obligations |
| `paper` | writer | Draft research note (LaTeX-compatible) |
| `referee` | reviewer | Reviewer report, blocking issues, verdict |

Stage ordering is context-dependent:
- Tier 1–3 problems (computational, experimental, pattern): brief → novelty → plan → experiment → results → paper → referee
- Tier 4–5 problems (structural, foundational): brief → novelty → plan → prove → results → paper → referee

## Model Router Integration

The orchestrator resolves LLM models automatically via `model_router.py`:
- Each agent role has a default model profile (e.g., prover defaults to `deepseek-reasoner`)
- Tier-specific overrides exist (e.g., T4 planner uses reasoning model instead of chat)
- Fallback chains are configured per profile (e.g., deepseek → gpt-4o)
- An explicit `--model` CLI flag overrides automatic routing

See `protocol/model-routing.md` (when created) for the full routing table.

## Prompt Architecture

Each stage dispatch produces two prompts:

### System Prompt
Built from the agent YAML definition:
- Role identity and purpose
- Expected inputs and outputs
- Success criteria
- Evidence-class labeling rules
- Anti-overclaiming constraints

### User Prompt
Built from assembled problem context:
- Registry entry (title, domain, statement)
- Triage info (tier, amenability score, approach)
- Workspace README (problem description)
- Workflow state (current stage, owner, route)
- Prior run summaries (last 5 experiment ledger entries)
- Proof obligations (when applicable)
- Stage-specific instruction
- Structured output format specification

## Artifact Lifecycle

1. LLM response is received as plain text with an embedded `\`\`\`yaml` block
2. YAML block is extracted and parsed (evidence class, confidence, key findings)
3. Full response is saved as `artifacts/<stage>_<timestamp>.md` with YAML frontmatter
4. SHA-256 checksum is computed and recorded in `artifacts/manifest.yaml`
5. The manifest serves as the evidence-bundle input for `omega-verify-evidence`

## Dry-Run Mode

`--dry-run` prints the constructed prompts without invoking the LLM API.
Useful for:
- Debugging prompt construction
- Cost estimation (token counting)
- Reviewing system + user prompt quality before a real run

## Dispatch Modes

### `omega-orchestrate run <problem-id> --stage <stage>`
Single-stage execution. Resolves the agent role from stage, dispatches, saves artifact.

### `omega-orchestrate dispatch <problem-id> --role <role> --stage <stage>`
Direct role dispatch. Bypasses stage-to-role mapping (for custom routing).

### `omega-orchestrate pipeline <problem-id> --from-stage <s1> --to-stage <s2>`
Multi-stage execution. Runs stages sequentially from s1 to s2 (inclusive).
Stops on first failure.

## Error Handling

- Missing agent YAML → `FileNotFoundError` with path
- Invalid stage name → error dict with valid-stage list
- LLM API failure → `urllib.error.URLError` propagated with context
- No YAML block in response → metadata defaults to `evidence_class: E2, confidence: C2`
- Pipeline failure → partial results returned with failing stage identified

## Integration Points

- `agents/team.yaml` → `orchestration.pipeline_stages` is the SSOT for stage-to-role mapping
- `registry/domains/*.yaml` → problem definitions
- `registry/triage-matrix.yaml` → tier routing
- `research/active/<id>/control/workflow-state.yaml` → workflow FSM state
- `research/active/<id>/experiments/ledger.yaml` → prior run context
- `scripts/model_router.py` → LLM model resolution
- `scripts/verify_evidence.py` → post-run artifact verification

## Constraints

1. All LLM outputs are classified as evidence class E2 (LLM-assisted, requires verification) unless a formal verification step has been applied.
2. Anti-overclaiming rules in the system prompt prevent theorem-level language in LLM outputs.
3. Token budgets per role (defined in `ROLE_TOKEN_BUDGET`) cap response length to prevent runaway cost.
4. No tool-use or function-calling is supported — the orchestrator is prompt-in/text-out only.
5. No autonomous looping — the pipeline runs stages sequentially and stops. Iterative refinement requires explicit re-dispatch.
