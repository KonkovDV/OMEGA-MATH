# OMEGA Operator Runbook

Step-by-step procedures for registry maintenance, experiment management, and CI recovery.

## 1. Adding a New Problem to the Registry

1. Identify the target domain file: `registry/domains/<domain>.yaml`.
2. Add a new entry following the schema in `registry/schema.json`.
   - Required fields: `id`, `name`, `domain`, `status`, `statement`, `ai_triage`.
   - Use `ai_triage.tier` values: T1 (high amenability), T2 (medium), T3 (low), T4 (currently intractable).
3. Run the validator:
   ```bash
   python scripts/validate_registry.py
   ```
4. Regenerate the index:
   ```bash
   python scripts/generate_index.py
   ```
5. Update `registry/triage-matrix.yaml` if the problem should appear in the prioritized queue.
6. Commit all changed files together.

## 2. Adding a Collection Overlay

Collection files under `registry/collections/*.yaml` are quick-reference groupings.

1. Create or edit the target collection file.
2. For problems that already have a canonical record, use `registry_id` to cross-reference:
   ```yaml
   - registry_id: "nt-goldbach"
     collection_note: "Landau's problem #1"
   ```
3. Run the validator — it checks that every `registry_id` resolves to a canonical entry.
4. Commit.

## 2.1 Syncing Einstein Arena Overlay Safely

When refreshing `registry/collections/einstein-arena-benchmarks.yaml`:

1. Prefer a pinned local README snapshot when available:
   ```bash
   omega-import-einstein-arena --readme-file .benchmarks/einstein-arena-readme.md
   ```
2. Keep slug alias updates in `registry/collections/einstein-arena-aliases.yaml` instead of editing importer logic.
3. If you need donor solution files, use:
   ```bash
   omega-import-einstein-arena --readme-file .benchmarks/einstein-arena-readme.md --repo-dir ../EinsteinArena-new-SOTA
   ```
4. Re-run contract tests after any importer or adapter change:
   ```bash
   python -m pytest tests/test_import_einstein_arena.py tests/test_einstein_arena_adapter.py -q
   ```
5. For live API interaction via `omega-einstein-arena`, use bounded retry settings:
   ```bash
   omega-einstein-arena --timeout 45 --max-retries 3 --retry-backoff 1.0 <action> ...
   ```

## 3. Contesting a Problem Status

If a problem's status (open, partially-resolved, resolved) needs updating:

1. Verify the claim against primary sources (paper, formal proof repository, or official announcement).
2. Update the `status` field in the canonical domain YAML.
3. Add a `status_note` with the source reference and date.
4. Update `partial_results` if applicable.
5. Run the validator and regenerate the index.
6. If the change affects triage scores, update `triage-matrix.yaml`.

## 4. Refreshing Provenance and Literature

1. Update `provenance_urls` in the canonical entry.
2. If the problem has an active workspace under `research/active/<id>/`, update `input_files/literature.md`.
3. Re-run the Librarian agent or manually check arXiv, MathSciNet, and OEIS for new results.
4. Record the refresh date in the entry's `last_checked` field if available.

## 5. CI Validation Recovery

When the GitHub Actions `validate.yml` workflow fails:

1. Read the CI output to identify which file and which check failed.
2. Common failures:
   - **Schema violation**: a required field is missing or has the wrong type → fix the YAML entry.
   - **Cross-reference failure**: a `registry_id` in a collection doesn't match any canonical entry → add the canonical entry first or fix the ID.
   - **Duplicate ID**: two entries share the same `id` → rename one.
   - **Workspace artifact schema violation**: `research/active/*/experiments/ledger.yaml` or evidence-bundle file does not match `registry/schemas/*.schema.json` → fix the artifact structure or regenerate through runner/verification CLIs.
3. After fixing, run locally:
   ```bash
   python scripts/validate_registry.py
   python scripts/generate_index.py
   ```
4. Confirm both pass, then push.

## 6. Scaffolding a New Problem Workspace

Use the scaffolder to create a standard problem directory:

```bash
python scripts/scaffold_problem.py <problem-id>
```

This creates:

```
research/active/<problem-id>/
  input_files/
    data_description.md
    literature.md
      literature_graph.md
      citation_evidence.md
      idea.md
    methods.md
    proof_obligations.md
      results.md
      referee.md
  experiments/
    ledger.yaml
   artifacts/
      evidence-bundle.yaml
      run-manifest.yaml
      prover-results/
   paper/
   presentation/
  reproducibility.md
```

Fill in `data_description.md` from the registry entry before starting any research run.

## 6.2 Orchestrator Stage Preconditions

`omega-orchestrate` now enforces stage contracts:

1. `brief` can run without an existing workspace.
2. All later stages require `research/active/<problem-id>/`.
3. If baseline docs are missing, the orchestrator materializes placeholders automatically:
   - `README.md`
   - `input_files/data_description.md`
   - stage-specific: `literature.md`, `citation_evidence.md`, `proof_obligations.md`

Recommendation:

- initialize via `omega-scaffold-problem` + `omega-workflow triage` before running novelty/plan/experiment/prove stages.
- treat auto-created placeholders as blocking TODOs, not as completed research content.

## 6.3 Prompt Packet Traceability

Each non-dry orchestrator dispatch now writes:

- response artifact: `artifacts/<stage>_<timestamp>.md`
- prompt packet: `artifacts/prompts/<stage>_<timestamp>.prompt.json`

Manifest entries include `prompt_packet_sha256` and `prompt_packet_file_sha256`.
Use this to audit exact prompt + model-routing context for claim-bearing outputs.

## 6.1 Initializing Workflow Control State

After scaffolding a problem workspace, materialize the local control state from registry triage:

```bash
python scripts/omega_workflow.py triage <problem-id>
```

This writes `research/active/<problem-id>/control/workflow-state.yaml` and records:

- tier and amenability score when available
- recommended route (`experiment-first`, `proof-first`, `survey-first`)
- current stage and responsible owner
- restartable transition history
- room for runner lifecycle sync (`active_run_id`, latest verdict, latest proof result)

Use:

```bash
python scripts/omega_workflow.py status <problem-id>
python scripts/omega_workflow.py advance <problem-id> --outcome complete
```

Do not hand-edit the workflow state unless recovering from a broken run and the CLI cannot repair it.

## 7. Recording an Experiment Run

See `protocol/experiment-ledger-spec.md` for the full schema.

Quick steps:
1. Open the run with the bounded local runner:
   ```bash
   python scripts/omega_runner.py start <problem-id> --route experiment-first --agent experimentalist --description "bounded search"
   ```
2. Record the emitted `run_id`.
3. After the run completes, close it through the same CLI:
   ```bash
   python scripts/omega_runner.py finish <problem-id> <run-id> --status completed --verdict positive --artifact artifacts/search.log:log --notes "summary"
   ```
4. `start` and `finish` also synchronize `control/workflow-state.yaml`: opening a run moves the workflow into the route's execution stage, and closing it moves the workflow into `results` unless the operator has already advanced it further.
5. The runner computes artifact checksums and refreshes `artifacts/evidence-bundle.yaml` automatically.
6. Commit the updated ledger, workflow state, evidence bundle, and any listed artifacts.

Manual ledger editing is still possible for recovery, but the CLI is the preferred path because it also refreshes `research/active/experiment-index.yaml`.

## 8. Recording a Proof Result

See `protocol/prover-result-contract.md` for the full schema.

Quick steps:
1. Keep proof attempts in `experiments/ledger.yaml` like any other run.
2. When a proof-first run reaches a verifier-visible outcome, emit the prover result through the CLI:
   ```bash
   python scripts/omega_runner.py proof-result <problem-id> <run-id> --claim-label "candidate theorem" --claim-class theorem --status draft --verifier lean4 --toolchain leanprover/lean4:v4.29.0 --verifier-command "lake env lean artifacts/candidate.lean" --source-entry artifacts/candidate.lean --artifact artifacts/candidate.lean:source
   ```
3. The CLI writes `research/active/<problem-id>/artifacts/prover-results/<run-id>.yaml` and links that artifact back into the ledger entry.
4. The same command refreshes `artifacts/evidence-bundle.yaml` and stores the latest proof-result pointer in `control/workflow-state.yaml`.
5. Update `reproducibility.md` if the proof result is claim-bearing.

## 9. Regenerating the Registry Index

The index file `registry/index.yaml` is generated, not hand-edited.

```bash
python scripts/generate_index.py
```

Run this after any change to domain or collection files. The CI also runs it as a check.

## 9.1 Regenerating the Experiment Index

The active run-and-workflow summary file is generated, not hand-edited.

```bash
python scripts/generate_experiment_index.py
```

`scripts/omega_runner.py start|finish|proof-result` already refresh this index automatically, but the standalone command is useful for recovery or bulk edits.

The generated entries now include both run state and workflow state, so you can audit blocked workspaces or stage ownership without opening each folder manually. For example:

```bash
python scripts/experiment_query.py --global --blocked-only --format table
python scripts/experiment_query.py --global --stage plan --owner planner
```

## 9.2 Regenerating the Evidence Bundle

The per-problem evidence bundle is generated, not hand-edited.

```bash
python scripts/omega_runner.py evidence-bundle <problem-id>
```

Use this after manual artifact repair, after restoring missing files, or when checking whether a claim-bearing workspace still has a coherent checksum surface.

## 10. Pre-Publication Checklist

Before publishing any OMEGA result externally:

1. Confirm the claim language matches the evidence class (`verification-pipeline.md`).
2. Confirm the experiment ledger has at least one `completed` run with `positive` or `negative` verdict.
3. If the result is proof-first, confirm there is a paired prover result artifact under `artifacts/prover-results/`.
4. Confirm `artifacts/evidence-bundle.yaml` regenerates cleanly and that listed artifact checksums match current files.
5. Confirm `reproducibility.md` lists exact commands, versions, and artifact checksums.
6. Run the Reviewer agent or perform a manual review pass.
7. Fill in the publication template from `templates/` and narrow claims to stored evidence.
