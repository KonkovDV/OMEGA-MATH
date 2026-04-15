"""
Phase 3: Numerical Certification Scaffold for Thomson Problem
=============================================================
Re-evaluate persisted best configurations at higher precision, measure tangent
force residuals, and optionally build a finite-difference Hessian on the local
tangent space. This is a numerical certification scaffold, not a rigorous proof.

Usage:
    python phase3_certify.py --source-artifact ../artifacts/phase2_cpu_probe_7_10.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

try:
    import mpmath as mp
except ImportError as exc:
    raise SystemExit(
        "mpmath is required for Thomson certification scaffolding. Install research extras with: "
        "python -m pip install -e .[research]"
    ) from exc

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit(
        "numpy is required for Thomson certification scaffolding. Install research extras with: "
        "python -m pip install -e .[research]"
    ) from exc

from phase1_multistart import KNOWN_ENERGIES


def project_points(points: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(points, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return points / norms


def resolve_artifact_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (Path(__file__).parent / raw_path).resolve()


def load_source_runs(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["runs"]


def mp_point(point: list[float]) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    return tuple(mp.mpf(str(value)) for value in point)


def mp_dot(a: tuple[mp.mpf, mp.mpf, mp.mpf], b: tuple[mp.mpf, mp.mpf, mp.mpf]) -> mp.mpf:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def mp_sub(a: tuple[mp.mpf, mp.mpf, mp.mpf], b: tuple[mp.mpf, mp.mpf, mp.mpf]) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mp_scale(a: tuple[mp.mpf, mp.mpf, mp.mpf], scalar: mp.mpf) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    return (a[0] * scalar, a[1] * scalar, a[2] * scalar)


def mp_add(a: tuple[mp.mpf, mp.mpf, mp.mpf], b: tuple[mp.mpf, mp.mpf, mp.mpf]) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mp_norm(a: tuple[mp.mpf, mp.mpf, mp.mpf]) -> mp.mpf:
    return mp.sqrt(mp_dot(a, a))


def high_precision_energy(points: list[tuple[mp.mpf, mp.mpf, mp.mpf]]) -> mp.mpf:
    energy = mp.mpf("0")
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            dist = mp_norm(mp_sub(points[i], points[j]))
            energy += mp.mpf("1") / dist
    return energy


def tangent_force_norms(points: list[tuple[mp.mpf, mp.mpf, mp.mpf]]) -> list[mp.mpf]:
    norms: list[mp.mpf] = []
    n = len(points)
    for i in range(n):
        force = (mp.mpf("0"), mp.mpf("0"), mp.mpf("0"))
        for j in range(n):
            if i == j:
                continue
            diff = mp_sub(points[i], points[j])
            dist = mp_norm(diff)
            inv_cube = mp.mpf("1") / (dist**3)
            force = mp_sub(force, mp_scale(diff, inv_cube))
        radial_component = mp_dot(force, points[i])
        tangent_force = mp_sub(force, mp_scale(points[i], radial_component))
        norms.append(mp_norm(tangent_force))
    return norms


def tangent_basis(points: np.ndarray) -> list[np.ndarray]:
    basis: list[np.ndarray] = []
    n = len(points)
    for index, point in enumerate(points):
        seed = np.array([1.0, 0.0, 0.0])
        if abs(float(np.dot(point, seed))) > 0.9:
            seed = np.array([0.0, 1.0, 0.0])
        first = seed - np.dot(seed, point) * point
        first = first / np.linalg.norm(first)
        second = np.cross(point, first)
        second = second / np.linalg.norm(second)

        first_direction = np.zeros((n, 3), dtype=float)
        second_direction = np.zeros((n, 3), dtype=float)
        first_direction[index] = first
        second_direction[index] = second
        basis.append(first_direction.reshape(-1))
        basis.append(second_direction.reshape(-1))
    return basis


def energy_from_perturbation(base_points: np.ndarray, perturbation: np.ndarray, step: float) -> float:
    displaced = project_points(base_points + step * perturbation.reshape(base_points.shape))
    points_mp = [mp_point(point.tolist()) for point in displaced]
    return float(high_precision_energy(points_mp))


def finite_difference_hessian(base_points: np.ndarray, step: float) -> tuple[np.ndarray, np.ndarray]:
    basis = tangent_basis(base_points)
    dimension = len(basis)
    hessian = np.zeros((dimension, dimension), dtype=float)

    for i in range(dimension):
        for j in range(i, dimension):
            plus_plus = energy_from_perturbation(base_points, basis[i] + basis[j], step)
            plus_minus = energy_from_perturbation(base_points, basis[i] - basis[j], step)
            minus_plus = energy_from_perturbation(base_points, -basis[i] + basis[j], step)
            minus_minus = energy_from_perturbation(base_points, -basis[i] - basis[j], step)
            value = (plus_plus - plus_minus - minus_plus + minus_minus) / (4.0 * step * step)
            hessian[i, j] = value
            hessian[j, i] = value

    eigenvalues = np.linalg.eigvalsh(hessian)
    return hessian, eigenvalues


def classify_certification(
    max_force_norm: float,
    hessian_computed: bool,
    post_symmetry_min_eigenvalue: float | None,
    force_tolerance: float,
    eigen_tolerance: float,
) -> str:
    if max_force_norm > force_tolerance:
        return "numerical-review-needed"
    if not hessian_computed:
        return "numerical-stationary-candidate"
    if post_symmetry_min_eigenvalue is not None and post_symmetry_min_eigenvalue >= -eigen_tolerance:
        return "numerical-local-minimum-candidate"
    return "numerical-review-needed"


def certify_run(
    *,
    n: int,
    run_payload: dict[str, Any],
    source_artifact: Path,
    skip_hessian: bool,
    hessian_step: float,
    force_tolerance: float,
    eigen_tolerance: float,
    zero_tolerance: float,
) -> dict[str, Any]:
    base_points = np.asarray(run_payload["best_config"], dtype=float)
    base_points = project_points(base_points)
    points_mp = [mp_point(point.tolist()) for point in base_points]

    energy_mp = high_precision_energy(points_mp)
    force_norms = tangent_force_norms(points_mp)
    max_force = max(force_norms)
    mean_force = sum(force_norms, mp.mpf("0")) / len(force_norms)

    result: dict[str, Any] = {
        "N": n,
        "source_artifact": str(source_artifact),
        "source_best_energy": run_payload["best_energy"],
        "source_classification": run_payload.get("classification"),
        "known_energy": KNOWN_ENERGIES.get(n),
        "high_precision_energy_mp": mp.nstr(energy_mp, 40),
        "high_precision_energy_float": float(energy_mp),
        "delta_to_known": float(energy_mp - mp.mpf(str(KNOWN_ENERGIES[n]))) if n in KNOWN_ENERGIES else None,
        "max_tangent_force_norm_mp": mp.nstr(max_force, 20),
        "mean_tangent_force_norm_mp": mp.nstr(mean_force, 20),
        "tangent_dimension": 2 * n,
        "expected_rotational_zero_modes": 3,
        "hessian_computed": False,
        "smallest_eigenvalues": [],
        "zero_like_eigenvalues": None,
        "negative_eigenvalues_excluding_symmetry": None,
        "post_symmetry_min_eigenvalue": None,
    }

    if not skip_hessian:
        _, eigenvalues = finite_difference_hessian(base_points, hessian_step)
        smallest = sorted(float(value) for value in eigenvalues[: min(8, len(eigenvalues))])
        post_symmetry = eigenvalues[3:] if len(eigenvalues) > 3 else np.array([], dtype=float)
        post_symmetry_min = float(np.min(post_symmetry)) if post_symmetry.size else None
        negatives_excluding_symmetry = int(np.sum(post_symmetry < -eigen_tolerance)) if post_symmetry.size else 0
        zero_like = int(np.sum(np.abs(eigenvalues) <= zero_tolerance))
        result.update(
            {
                "hessian_computed": True,
                "smallest_eigenvalues": smallest,
                "zero_like_eigenvalues": zero_like,
                "negative_eigenvalues_excluding_symmetry": negatives_excluding_symmetry,
                "post_symmetry_min_eigenvalue": post_symmetry_min,
            }
        )

    result["certification_status"] = classify_certification(
        max_force_norm=float(max_force),
        hessian_computed=bool(result["hessian_computed"]),
        post_symmetry_min_eigenvalue=result["post_symmetry_min_eigenvalue"],
        force_tolerance=force_tolerance,
        eigen_tolerance=eigen_tolerance,
    )
    result["notes"] = [
        "Numerical certification scaffold only; this artifact is not a rigorous proof.",
        "The tangent-force residual is measured at higher precision using mpmath.",
        "When computed, the Hessian is a tangent-space finite-difference approximation with three rotational symmetry modes expected near zero.",
    ]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Thomson problem numerical certification scaffold")
    parser.add_argument("--source-artifact", required=True)
    parser.add_argument("--n-min", type=int, default=7)
    parser.add_argument("--n-max", type=int, default=10)
    parser.add_argument("--mp-dps", type=int, default=80)
    parser.add_argument("--hessian-step", type=float, default=1e-5)
    parser.add_argument("--force-tolerance", type=float, default=1e-5)
    parser.add_argument("--eigen-tolerance", type=float, default=1e-7)
    parser.add_argument("--zero-tolerance", type=float, default=5e-5)
    parser.add_argument("--skip-hessian", action="store_true")
    parser.add_argument("--output", type=str, default="../artifacts/phase3_certify_results.json")
    args = parser.parse_args()

    mp.mp.dps = args.mp_dps
    source_artifact = resolve_artifact_path(args.source_artifact)
    source_runs = load_source_runs(source_artifact)
    outpath = Path(__file__).parent / args.output
    outpath.parent.mkdir(parents=True, exist_ok=True)

    print("Thomson Problem — Numerical Certification Scaffold")
    print(f"source_artifact={source_artifact}")
    print(f"N range: {args.n_min} to {args.n_max}, mp.dps={args.mp_dps}, skip_hessian={args.skip_hessian}")
    print()

    payload: dict[str, Any] = {
        "meta": {
            "source_artifact": str(source_artifact),
            "n_min": args.n_min,
            "n_max": args.n_max,
            "mp_dps": args.mp_dps,
            "hessian_step": args.hessian_step,
            "force_tolerance": args.force_tolerance,
            "eigen_tolerance": args.eigen_tolerance,
            "zero_tolerance": args.zero_tolerance,
            "skip_hessian": args.skip_hessian,
        },
        "runs": {},
    }

    for n in range(args.n_min, args.n_max + 1):
        key = str(n)
        if key not in source_runs:
            raise SystemExit(f"Source artifact '{source_artifact}' does not contain run '{n}'.")
        started_at = time.time()
        run = certify_run(
            n=n,
            run_payload=source_runs[key],
            source_artifact=source_artifact,
            skip_hessian=args.skip_hessian,
            hessian_step=args.hessian_step,
            force_tolerance=args.force_tolerance,
            eigen_tolerance=args.eigen_tolerance,
            zero_tolerance=args.zero_tolerance,
        )
        elapsed = time.time() - started_at
        run["elapsed_sec"] = elapsed
        payload["runs"][key] = run

        print(
            f"  N={n:3d}: E_hp={run['high_precision_energy_float']:.12f}  "
            f"max_force={run['max_tangent_force_norm_mp']}  status={run['certification_status']}  [{elapsed:.1f}s]"
        )

    with outpath.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    main()