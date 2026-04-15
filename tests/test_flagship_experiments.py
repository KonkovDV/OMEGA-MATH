import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_CANDIDATES = [
    REPO_ROOT.parent / ".venv" / "Scripts" / "python.exe",
    REPO_ROOT.parent / ".venv" / "bin" / "python",
    REPO_ROOT / ".venv" / "Scripts" / "python.exe",
    REPO_ROOT / ".venv" / "bin" / "python",
    Path(sys.executable),
]


def resolve_python() -> str:
    for candidate in PYTHON_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def run_script(script: Path, *args: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "artifact.json"
        command = [resolve_python(), str(script), *args, "--output", str(output_path)]
        subprocess.run(command, check=True, cwd=script.parent, capture_output=True, text=True)
        return json.loads(output_path.read_text(encoding="utf-8"))


def test_erdos_straus_phase1_smoke_metadata_and_barrier_behavior() -> None:
    script = REPO_ROOT / "research" / "active" / "erdos-straus" / "experiments" / "phase1_covering.py"
    payload = run_script(script, "--verify-count", "3", "--max-denom", "2000")

    assert payload["_meta"]["verify_count"] == 3
    assert payload["_meta"]["max_denom"] == 2000
    for residue in ("1", "121", "169", "289", "361", "529"):
        assert payload[residue]["successes"] == 0
        assert payload[residue]["coverage"] == 0


def test_erdos_straus_phase2_smoke_finds_known_small_solution() -> None:
    script = REPO_ROOT / "research" / "active" / "erdos-straus" / "experiments" / "phase2_parametric.py"
    payload = run_script(script, "--max-n", "200", "--max-denom", "2000")

    assert payload["primes"]["73"]["solution_count"] >= 1
    assert payload["meta"]["unsolved_primes"] == [97, 193]


def test_kobon_phase1_smoke_matches_known_small_values() -> None:
    script = REPO_ROOT / "research" / "active" / "kobon-triangles" / "experiments" / "phase1_pseudoline_enum.py"
    payload = run_script(
        script,
        "--k-min",
        "3",
        "--k-max",
        "5",
        "--sa-iterations",
        "100",
        "--sa-restarts",
        "2",
        "--seed",
        "1729",
    )

    assert payload["meta"]["seed"] == 1729
    assert payload["runs"]["3"]["found_triangles"] == 1
    assert payload["runs"]["4"]["found_triangles"] == 2
    assert payload["runs"]["5"]["found_triangles"] == 5


def test_thomson_phase1_smoke_reproduces_small_known_energies() -> None:
    script = REPO_ROOT / "research" / "active" / "thomson-problem" / "experiments" / "phase1_multistart.py"
    payload = run_script(
        script,
        "--n-min",
        "2",
        "--n-max",
        "4",
        "--restarts",
        "3",
        "--seed",
        "1729",
    )

    assert payload["meta"]["seed"] == 1729
    assert abs(payload["runs"]["2"]["delta"]) < 1e-6
    assert abs(payload["runs"]["3"]["delta"]) < 1e-6
    assert abs(payload["runs"]["4"]["delta"]) < 1e-6


def test_thomson_phase2_smoke_persists_best_config_and_reproduces_small_known_energies() -> None:
    script = REPO_ROOT / "research" / "active" / "thomson-problem" / "experiments" / "phase2_basin_hopping.py"
    payload = run_script(
        script,
        "--n-min",
        "2",
        "--n-max",
        "4",
        "--restarts",
        "2",
        "--niter",
        "3",
        "--local-maxiter",
        "100",
        "--top-k",
        "2",
        "--seed",
        "1729",
    )

    assert payload["meta"]["seed"] == 1729
    assert payload["meta"]["niter"] == 3

    for label in ("2", "3", "4"):
        run = payload["runs"][label]
        assert abs(run["delta"]) < 1e-6
        assert len(run["best_config"]) == int(label)
        assert run["distinct_minima"] >= 1
        assert run["top_minima"]


def test_thomson_phase3_smoke_emits_certification_scaffold_artifact() -> None:
    script = REPO_ROOT / "research" / "active" / "thomson-problem" / "experiments" / "phase3_certify.py"
    payload = run_script(
        script,
        "--source-artifact",
        "../artifacts/phase2_cpu_probe_7_10.json",
        "--n-min",
        "7",
        "--n-max",
        "7",
        "--mp-dps",
        "50",
        "--skip-hessian",
    )

    assert payload["meta"]["mp_dps"] == 50
    run = payload["runs"]["7"]
    assert run["source_artifact"].endswith("phase2_cpu_probe_7_10.json")
    assert run["tangent_dimension"] == 14
    assert run["hessian_computed"] is False
    assert run["max_tangent_force_norm_mp"]
    assert run["high_precision_energy_mp"]


def test_thomson_phase3_n11_regression_reaches_local_minimum_candidate() -> None:
    script = REPO_ROOT / "research" / "active" / "thomson-problem" / "experiments" / "phase3_certify.py"
    payload = run_script(
        script,
        "--source-artifact",
        "../artifacts/phase2_cpu_probe_11_13.json",
        "--n-min",
        "11",
        "--n-max",
        "11",
        "--mp-dps",
        "50",
    )

    run = payload["runs"]["11"]
    assert run["source_artifact"].endswith("phase2_cpu_probe_11_13.json")
    assert run["tangent_dimension"] == 22
    assert run["hessian_computed"] is True
    assert run["negative_eigenvalues_excluding_symmetry"] == 0
    assert run["post_symmetry_min_eigenvalue"] > 0
    assert run["certification_status"] == "numerical-local-minimum-candidate"