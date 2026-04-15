# Thomson problem

Registry ID: `thomson-problem`

Status: active

## Current executable surface

- Phase 1 multi-start local optimization via `experiments/phase1_multistart.py`
- Phase 2 bounded basin-hopping global search via `experiments/phase2_basin_hopping.py`
- Phase 3 bounded numerical certification scaffold via `experiments/phase3_certify.py`

## Current bounded evidence

- `artifacts/phase2_cpu_probe_19_20_deeper.json` sharpens the rugged-subrange picture and shows that `N=19` is materially more multi-basin than `N=20`
- `artifacts/phase3_certify_7_10.json` upgrades `N=7..10` to numerical local-minimum-candidate status under the current finite-precision scaffold
- `artifacts/phase3_certify_11_12.json` extends the same Phase 3 gate to `N=11..12`
- `artifacts/phase3_certify_13.json` extends the Phase 3 gate to `N=13`, completing the continuous certified range `N=7..13`
- `artifacts/evidence-bundle.yaml` and `experiments/ledger.yaml` track completed Thomson certification runs in the local OMEGA workflow substrate

## Current interpretation boundary

- all currently shipped Thomson artifacts remain reproductions of accepted benchmark values
- the Phase 3 surface is a numerical local-minimum-candidacy check, not a rigorous proof
- no current artifact supports a novelty claim or a publication-grade structural claim

## Next step

- extend the Phase 3 certification scaffold to `N=14..20` using existing Phase 2 probes
- then add selective structural analysis (Phase 4: spherical Voronoi defect counting) only for candidates that survive the current numerical gate
