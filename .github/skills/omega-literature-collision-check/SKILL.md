---
name: omega-literature-collision-check
description: Use when evaluating novelty, benchmark authority, citation accuracy, or literature-collision risk for an OMEGA math result or documentation claim.
argument-hint: problem id + claim or artifact to check
---

# OMEGA Literature Collision Check

## When to Use

Use this skill when you need to decide whether a result is:

- merely reproducing a known benchmark
- colliding with existing literature
- citing the correct paper, authors, title, and result
- safe to describe as interesting, publishable, or novel

## Retrieval Order

1. Read the problem's `input_files/literature.md` and `input_files/citation_evidence.md`.
2. Read the current artifact or claim-bearing file.
3. Fetch the smallest official or primary source that can confirm the claim.
4. Compare the external source with the local literature packet and artifact.
5. Classify the claim conservatively.

## Classification Output

Use one of these labels:

- `reproduction` -> matches accepted prior work or benchmark
- `rounding-sensitive reproduction` -> appears lower than a rounded public value but is not yet credible as an improvement
- `collision risk` -> likely already covered in literature or benchmark tables
- `plausible escalation candidate` -> worth deeper review, but not yet a novelty claim

## Repo Rules

- Prefer primary sources, benchmark registries, and official documentation over memory.
- Update `citation_evidence.md` when a fact-check materially changes the local evidence.
- Do not collapse “not yet disproven” into “novel”.
- If citation metadata is uncertain, say so instead of guessing.

## Anti-Patterns

- using a rounded benchmark table as proof of a new record
- relying on an old literature packet without checking current primary sources
- overstating negative or null results as if they resolved the problem