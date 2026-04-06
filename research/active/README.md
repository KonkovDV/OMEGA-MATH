# Active Research

Use this directory for in-progress OMEGA investigations.

Recommended per-problem layout (Denario-compatible, OMEGA-adapted):

- input_files/data_description.md
- input_files/literature.md
- input_files/literature_graph.md
- input_files/citation_evidence.md
- input_files/idea.md
- input_files/methods.md
- input_files/proof_obligations.md
- input_files/results.md
- input_files/referee.md
- input_files/plots/
- planning/
- control/
- paper/
- presentation/
- experiments/ledger.yaml
- reproducibility.md
- artifacts/evidence-bundle.yaml
- artifacts/run-manifest.yaml
- artifacts/prover-results/

Bootstrap a new folder with:

- `python scripts/scaffold-problem.py <problem-id> --title "..."`

For proof-first work, copy `templates/lean-starter/` into a problem-local Lean workspace such as `research/active/<problem-id>/proof/lean/`, then follow `protocol/lean-bootstrap.md`.

Use `data_description.md` as the canonical problem brief. Do not open a research cycle without a registry ID, literature packet, graph-aware literature and citation notes when novelty matters, a bounded stop condition, and a reproducibility stub that names the active ledger, evidence-bundle, and prover-result surfaces.
