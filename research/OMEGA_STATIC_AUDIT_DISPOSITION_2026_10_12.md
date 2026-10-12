---
title: "Disposition of the 12 October 2026 static audit"
status: active
version: "1.0.0"
last_updated: "2026-10-12"
date: "2026-10-12"
role: evidence
audience: internal+academic
tags: [omega, audit, evidence, orchestrator]
evidence_class: E1
confidence: C2
---

# Disposition of the 12 October 2026 static audit

The audit was a read of public pages. It said those pages could be about
five months behind `main`, and it did not run the tests. This note records
what the current tree confirmed, what changed, and what was not adopted.
No amenability score moved. No registry entry was closed.

## Confirmed and changed

- The orchestrator prompt used a second evidence vocabulary, and a missing
  model label was stored as E2/C2. The prompt now uses
  `protocol/evidence-governance.md`. A dispatch stores H/C1. The model's
  label is kept as `model_asserted_evidence_class` and does not become the
  class. A stronger class requires `evidence_assignment: checked` and an
  `evidence_anchor` file inside the workspace. The function records that
  file's hash. It does not rerun a checker, and a dispatch does not set
  `checked`.
- The novelty stage checked that literature files existed and could create
  them from empty templates. It did not put their text in the prompt, and
  it did not call `omega-literature`. The prompt now includes the local
  files and a saved `input_files/novelty-packet.yaml` when one is present.
  Otherwise `literature_retrieval` is `not_run`. Workspace prose is
  `local_files`. A packet counts only when its `candidates` list contains
  a paper title or id. An empty file, a blank template, a non-list, and
  a YAML error stay `not_run`. The novelty status stays `preliminary`
  for every retrieval value. The orchestrator still does not open a
  network search by itself.
- `problem_id`, `role`, and `stage` were path components. They now have to
  be lowercase identifiers, and the resolved path has to stay inside
  `agents/` or `research/active/`. `stage` has to be one of the known
  stages.
- Artifact names used the stage and a UTC timestamp to the second. A name
  now also carries a random token. The manifest is written under a lock,
  by replacing a temporary file.
- PROTOCOL.md said the catalog covered every known open problem, and it
  called an orchestrator output E2 in the sense "LLM-assisted". The
  registry is described as curated. Orchestrator output starts at H.
- The FrontierMath sentence "under 2%" was written as the current rate.
  It is now the rate reported in arXiv:2411.04872. A later percentage was
  not copied in, because this pass did not read that report.
- `validate.yml` installed optional extras with `|| true`. A failed extra
  install now fails the job.
- The README states that the supported install is an editable checkout.
  `agents/`, `registry/`, and `research/` are not in the wheel.

## Already true, and left as stated

- The amenability rubric already says the scores are one rater's April
  2026 estimates, with no inter-rater study. The October passes did not
  rescore them. This audit does not create that study, and it does not
  move a tier.
- README's 241 passed and the April runtime report's 233 passed are two
  dated runs. They were not rewritten into one commit.
- The repository already says it does not promise autonomous publication,
  complete literature coverage, or a proof from model text alone.

## Not adopted

- An inter-rater reliability study was not run.
- A clean-environment wheel execution was not run. The install boundary
  is documented instead.
- A Stanford AI Index percentage for a later FrontierMath slice was not
  added. The audit named it. This tree has not read that page.

## What the second pass removed

The first repair still let three weak readings through.

- `evidence_assignment: checked` with no file was enough to store R0.
  The class now stays H unless `evidence_anchor` names a file inside the
  workspace. The stored hash binds the class to that file. The function
  still does not rerun the checker.
- A `manifest.lock` left by a dead process was never removed, so later
  saves waited and then failed. A lock older than 30 seconds is removed.
- Any truthy `candidates` value counted as a search packet, and a blank
  literature file counted as local prose. A packet now needs a list item
  with a title or a paper id. Blank text stays `not_run`.
- `con`, `nul`, `aux`, `prn`, `com1` through `com9`, and `lpt1` through
  `lpt9` are refused as identifiers. On Windows those names are devices,
  not directories.
