# OMEGA Agent Teams

OMEGA uses a small fixed research team instead of a single monolithic agent.

## Core Team

### Planner

Purpose:
- choose the next problem
- assign the workflow
- enforce phase gates

Inputs:
- registry entry
- triage score
- available compute budget
- prior experiment logs

Outputs:
- data_description.md
- task allocation
- success criteria

### Librarian

Purpose:
- gather prior work
- extract known bounds, lemmas, failed approaches, and current status

Outputs:
- bibliography
- literature.md
- known-results summary

### Analyst

Purpose:
- convert a raw problem into executable research hypotheses
- identify search constraints, invariants, and promising reductions

Outputs:
- idea.md
- methods.md
- failure-mode checklist

### Experimentalist

Purpose:
- run numerical or combinatorial experiments
- generate datasets, candidate constructions, or counterexamples

Outputs:
- experiment log
- reproducible scripts or pseudocode
- results.md

### Prover

Purpose:
- attempt proofs of bounded claims
- formalize lemmas
- verify candidate arguments in proof assistants or symbolic systems

Outputs:
- proof sketch
- proof_obligations.md
- `artifacts/prover-results/<run-id>.yaml`
- formalization status
- dependency chain of lemmas

### Writer

Purpose:
- turn raw artifacts into a paper, note, or survey
- preserve limitations and evidence quality explicitly

Outputs:
- draft paper
- abstract
- claims table

### Reviewer

Purpose:
- attack the result before publication
- separate proof from experiment from speculation

Outputs:
- referee.md
- blocking issues
- publication recommendation

## Standard Workflow

1. Planner opens `data_description.md` from the registry entry.
2. Librarian returns a prior-work packet and novelty memo.
3. Analyst defines tractable sub-questions and writes the first idea/method notes.
4. Planner/Reviewer approve a bounded step plan.
5. Experimentalist or Prover executes first, depending on tier; proof-first work should use a bounded `generate -> referee -> repair` loop and keep explicit proof obligations. Every run is logged in the experiment ledger (see `docs/protocol/experiment-ledger-spec.md`), and proof-first runs that reach a verifier-visible state also emit a prover result artifact (see `docs/protocol/prover-result-contract.md`).
6. Writer drafts the artifact using a template from `templates/` and fills in `reproducibility.md` from `templates/reproducibility-manifest.md`.
7. Reviewer challenges it and records `referee.md`.
8. Planner either closes the cycle or schedules another pass.

For step-by-step operator procedures, see `docs/protocol/operator-runbook.md`.

## Handoff Artifacts

Each handoff must be concrete.

Required artifacts:
- input_files/data_description.md
- input_files/literature.md
- input_files/methods.md
- input_files/proof_obligations.md when proof work is involved
- input_files/results.md
- experiments/ledger.yaml (run records per `docs/protocol/experiment-ledger-spec.md`)
- artifacts/prover-results/<run-id>.yaml when proof work reaches a verifier-visible outcome
- reproducibility.md (from `templates/reproducibility-manifest.md`)
- assumptions list
- open questions list
- evidence links to exact files or outputs

## Escalation Rules

Escalate to human review when:
- a proof claim depends on a step the Prover cannot verify
- proof obligations remain unresolved but theorem language is already being drafted
- a result appears novel but literature coverage is incomplete
- computation required exceeds the configured budget
- the Writer cannot cleanly separate theorem, evidence, and conjecture

## Orchestrator Integration (v0.5.0)

The `agent_orchestrator.py` script (`omega-orchestrate` CLI) implements the
standard workflow above as an executable 8-stage pipeline with LLM dispatch:

| Pipeline stage | Agent role | Primary output |
|----------------|-----------|----------------|
| `brief` | planner | data description, success criteria |
| `novelty` | librarian | literature memo, known bounds |
| `triage` | planner | amenability assessment, tier routing |
| `plan` | planner | phased research plan |
| `experiment` | experimentalist | experiment log, computational results |
| `prove` | prover | proof sketch, obligations |
| `paper` | writer | draft, claims table |
| `referee` | reviewer | referee report, blocking issues |

Stage-to-role mapping is also stored in `agents/team.yaml` under the
`orchestration.pipeline_stages` key, and the orchestrator reads it at startup.

### Tier-Based Routing

For Tier 4 structural problems, the pipeline reorders to run `prove` before
`experiment`. For all other tiers, `experiment` runs first. The routing rules
in `team.yaml` determine which role handles the primary execution stage.

### API Support

Supported backends: OpenAI-compatible (OpenAI, DeepSeek, LM Studio, Ollama),
Anthropic Claude, and LiteLLM universal router. The `--model` flag selects the
model; the `--api` flag selects the backend (default: `openai`).

### Dry-Run Mode

Use `--dry-run` to preview the constructed prompt and skip the LLM API call.
This produces a full `<yaml>` block with the prompt text instead of LLM output.
