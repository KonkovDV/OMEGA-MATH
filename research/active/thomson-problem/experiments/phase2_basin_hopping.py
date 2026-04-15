"""
Phase 2: Basin-Hopping Global Search for Thomson Problem
========================================================
Use SciPy basin-hopping with a custom subset-rotation step and L-BFGS-B local
minimization to explore rugged Thomson energy landscapes while persisting
geometry-level evidence for the best minima.

Usage:
    python phase2_basin_hopping.py [--n-min 2] [--n-max 30] [--restarts 8] [--niter 40]
"""

# pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit(
        "numpy is required for Thomson experiment runs. Install research extras with: "
        "python -m pip install -e .[all]"
    ) from exc

try:
    from scipy.optimize import basinhopping as scipy_basinhopping
except ImportError as exc:
    raise SystemExit(
        "scipy is required for Thomson experiment runs. Install research extras with: "
        "python -m pip install -e .[all]"
    ) from exc

from phase1_multistart import KNOWN_ENERGIES, coulomb_energy_vectorized, coulomb_gradient, fibonacci_sphere

basinhopping: Any = scipy_basinhopping
IMPROVEMENT_EPSILON = 1e-6
MIN_DISTANCE_EPSILON = 1e-9


def project_points(points: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(points, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return points / norms


def random_sphere_points_with_rng(n: int, rng: np.random.Generator) -> np.ndarray:
    return project_points(rng.normal(size=(n, 3)))


def rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    axis = axis / np.linalg.norm(axis)
    kx, ky, kz = axis
    skew = np.array(
        [
            [0.0, -kz, ky],
            [kz, 0.0, -kx],
            [-ky, kx, 0.0],
        ]
    )
    identity = np.eye(3)
    return identity + np.sin(angle) * skew + (1.0 - np.cos(angle)) * (skew @ skew)


def minimum_pair_distance(points: np.ndarray) -> float:
    diffs = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    dists = np.sqrt(np.sum(diffs**2, axis=2))
    upper = dists[np.triu_indices(len(points), k=1)]
    if upper.size == 0:
        return float("inf")
    return float(np.min(upper))


def objective(coords_flat: np.ndarray, n: int) -> float:
    return coulomb_energy_vectorized(coords_flat, n)


def gradient(coords_flat: np.ndarray, n: int) -> np.ndarray:
    return coulomb_gradient(coords_flat, n)


class RandomSubsetRotationStep:
    def __init__(self, n: int, rng: np.random.Generator, subset_size: int, stepsize: float) -> None:
        self.n = n
        self.rng = rng
        self.subset_size = max(1, min(n, subset_size))
        self.stepsize = stepsize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        points = project_points(np.asarray(x, dtype=float).reshape(self.n, 3).copy())
        subset = self.rng.choice(self.n, size=self.subset_size, replace=False)
        axis = self.rng.normal(size=3)
        axis_norm = np.linalg.norm(axis)
        if axis_norm < 1e-12:
            axis = np.array([1.0, 0.0, 0.0])
        else:
            axis = axis / axis_norm
        angle = float(self.rng.normal(loc=0.0, scale=max(self.stepsize, 1e-12)))
        rot = rotation_matrix(axis, angle)
        points[subset] = points[subset] @ rot.T

        jitter_scale = self.stepsize * 0.1
        if jitter_scale > 0:
            jitter_idx = self.rng.choice(self.n, size=1, replace=False)
            points[jitter_idx] += self.rng.normal(scale=jitter_scale, size=(1, 3))

        return project_points(points).reshape(-1)


class SphereSeparationAcceptTest:
    def __init__(self, n: int, minimum_distance: float = MIN_DISTANCE_EPSILON) -> None:
        self.n = n
        self.minimum_distance = minimum_distance

    def __call__(self, *, f_new: float, x_new: np.ndarray, f_old: float, x_old: np.ndarray) -> bool:  # noqa: ARG002
        if not np.isfinite(f_new):
            return False
        points = project_points(np.asarray(x_new, dtype=float).reshape(self.n, 3))
        return minimum_pair_distance(points) > self.minimum_distance


def classify_run(delta: float | None) -> str:
    if delta is None:
        return "unbenchmarked"
    if delta < -IMPROVEMENT_EPSILON:
        return "plausible-escalation-candidate"
    if abs(delta) <= IMPROVEMENT_EPSILON:
        return "reproduction"
    return "gap"


def basin_hopping_single_run(
    n: int,
    *,
    niter: int,
    stepsize: float,
    temperature: float,
    local_maxiter: int,
    top_k: int,
    subset_size: int,
    niter_success: int | None,
    initial: np.ndarray,
    rng_seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(rng_seed)
    stepper = RandomSubsetRotationStep(n=n, rng=rng, subset_size=subset_size, stepsize=stepsize)
    accept_test = SphereSeparationAcceptTest(n=n)
    known = KNOWN_ENERGIES.get(n)

    minima_seen: dict[float, dict[str, Any]] = {}
    accepted_count = 0
    callback_count = 0

    def callback(x: np.ndarray, f: float, accept: bool) -> None:
        nonlocal accepted_count, callback_count
        callback_count += 1
        if accept:
            accepted_count += 1
        points = project_points(np.asarray(x, dtype=float).reshape(n, 3))
        energy = float(f)
        key = round(energy, 9)
        current = minima_seen.get(key)
        candidate = {
            "energy": energy,
            "delta": (energy - known) if known is not None else None,
            "accepted": bool(accept),
            "min_pair_distance": minimum_pair_distance(points),
            "config": points.tolist(),
        }
        if current is None or candidate["energy"] < current["energy"]:
            minima_seen[key] = candidate

    result: Any = basinhopping(
        objective,
        initial.reshape(-1),
        niter=niter,
        T=temperature,
        take_step=stepper,
        accept_test=accept_test,
        callback=callback,
        minimizer_kwargs={
            "method": "L-BFGS-B",
            "jac": gradient,
            "args": (n,),
            "options": {"maxiter": local_maxiter, "ftol": 1e-15},
        },
        niter_success=niter_success,
        rng=rng,
    )

    best_points = project_points(np.asarray(result.x, dtype=float).reshape(n, 3))
    best_energy = float(result.fun)
    recomputed_energy = coulomb_energy_vectorized(best_points.reshape(-1), n)
    lowest_result = getattr(result, "lowest_optimization_result", None)
    top_minima = sorted(minima_seen.values(), key=lambda item: item["energy"])[:top_k]

    return {
        "best_energy": best_energy,
        "best_config": best_points.tolist(),
        "recomputed_best_energy": float(recomputed_energy),
        "recompute_delta": float(recomputed_energy - best_energy),
        "observed_minima": callback_count,
        "accepted_minima": accepted_count,
        "distinct_minima": len(minima_seen),
        "best_local_success": bool(getattr(lowest_result, "success", False)) if lowest_result is not None else None,
        "best_local_message": str(getattr(lowest_result, "message", "")) if lowest_result is not None else None,
        "best_local_iterations": int(getattr(lowest_result, "nit", 0)) if lowest_result is not None and getattr(lowest_result, "nit", None) is not None else None,
        "min_pair_distance": minimum_pair_distance(best_points),
        "top_minima": top_minima,
    }


def run_basin_hopping_restarts(
    n: int,
    *,
    restarts: int,
    niter: int,
    stepsize: float,
    temperature: float,
    seed: int,
    local_maxiter: int,
    top_k: int,
    subset_size: int,
    niter_success: int | None,
) -> dict[str, Any]:
    known = KNOWN_ENERGIES.get(n)
    best_energy = float("inf")
    best_payload: dict[str, Any] | None = None
    best_run_index = 0
    best_start_mode = "fibonacci"
    global_minima: dict[float, dict[str, Any]] = {}
    run_summaries: list[dict[str, Any]] = []

    for run_index in range(restarts):
        run_seed = seed + run_index
        start_mode = "fibonacci" if run_index == 0 else "random"
        rng = np.random.default_rng(run_seed)
        initial = fibonacci_sphere(n) if run_index == 0 else random_sphere_points_with_rng(n, rng)
        started_at = time.time()
        payload = basin_hopping_single_run(
            n,
            niter=niter,
            stepsize=stepsize,
            temperature=temperature,
            local_maxiter=local_maxiter,
            top_k=top_k,
            subset_size=subset_size,
            niter_success=niter_success,
            initial=initial,
            rng_seed=run_seed,
        )
        elapsed = time.time() - started_at

        for minimum in payload["top_minima"]:
            key = round(minimum["energy"], 9)
            current = global_minima.get(key)
            if current is None or minimum["energy"] < current["energy"]:
                global_minima[key] = minimum

        run_summaries.append(
            {
                "run_index": run_index,
                "seed": run_seed,
                "start_mode": start_mode,
                "best_energy": payload["best_energy"],
                "distinct_minima": payload["distinct_minima"],
                "accepted_minima": payload["accepted_minima"],
                "elapsed_sec": elapsed,
            }
        )

        if payload["best_energy"] < best_energy:
            best_energy = payload["best_energy"]
            best_payload = payload
            best_run_index = run_index
            best_start_mode = start_mode

    assert best_payload is not None
    delta = (best_energy - known) if known is not None else None
    return {
        "N": n,
        "known_energy": known,
        "best_energy": best_energy,
        "delta": delta,
        "classification": classify_run(delta),
        "is_improvement": bool(delta is not None and delta < -IMPROVEMENT_EPSILON),
        "restarts": restarts,
        "niter": niter,
        "best_run_index": best_run_index,
        "best_start_mode": best_start_mode,
        "best_config": best_payload["best_config"],
        "recomputed_best_energy": best_payload["recomputed_best_energy"],
        "recompute_delta": best_payload["recompute_delta"],
        "min_pair_distance": best_payload["min_pair_distance"],
        "accepted_minima": int(sum(run["accepted_minima"] for run in run_summaries)),
        "distinct_minima": len(global_minima),
        "top_minima": sorted(global_minima.values(), key=lambda item: item["energy"])[:top_k],
        "run_summaries": run_summaries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Thomson problem basin-hopping optimizer")
    parser.add_argument("--n-min", type=int, default=2)
    parser.add_argument("--n-max", type=int, default=20)
    parser.add_argument("--restarts", type=int, default=4)
    parser.add_argument("--niter", type=int, default=30)
    parser.add_argument("--temperature", type=float, default=1e-3)
    parser.add_argument("--stepsize", type=float, default=0.35)
    parser.add_argument("--subset-size", type=int, default=3)
    parser.add_argument("--local-maxiter", type=int, default=300)
    parser.add_argument("--niter-success", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--seed", type=int, default=1729, help="Random seed for reproducible basin-hopping search")
    parser.add_argument("--output", type=str, default="../artifacts/phase2_results.json")
    args = parser.parse_args()

    outpath = Path(__file__).parent / args.output
    outpath.parent.mkdir(parents=True, exist_ok=True)

    print("Thomson Problem — Basin-Hopping Global Search")
    print(f"N range: {args.n_min} to {args.n_max}")
    print(f"restarts={args.restarts}, niter={args.niter}, local_maxiter={args.local_maxiter}")
    print(f"stepsize={args.stepsize}, temperature={args.temperature}, subset_size={args.subset_size}")
    print(f"seed={args.seed}")
    print()

    results: dict[str, Any] = {
        "meta": {
            "n_min": args.n_min,
            "n_max": args.n_max,
            "restarts": args.restarts,
            "niter": args.niter,
            "temperature": args.temperature,
            "stepsize": args.stepsize,
            "subset_size": args.subset_size,
            "local_maxiter": args.local_maxiter,
            "niter_success": args.niter_success,
            "top_k": args.top_k,
            "seed": args.seed,
            "improvement_epsilon": IMPROVEMENT_EPSILON,
        },
        "runs": {},
    }

    for n in range(args.n_min, args.n_max + 1):
        started_at = time.time()
        run = run_basin_hopping_restarts(
            n,
            restarts=args.restarts,
            niter=args.niter,
            stepsize=args.stepsize,
            temperature=args.temperature,
            seed=args.seed,
            local_maxiter=args.local_maxiter,
            top_k=args.top_k,
            subset_size=args.subset_size,
            niter_success=args.niter_success,
        )
        elapsed = time.time() - started_at
        run["elapsed_sec"] = elapsed
        results["runs"][str(n)] = run

        known_str = f"{run['known_energy']:.9f}" if run["known_energy"] is not None else "?"
        delta = run["delta"]
        delta_str = f"{delta:+.2e}" if delta is not None else "N/A"
        marker = "★" if run["classification"] == "plausible-escalation-candidate" else ("✓" if run["classification"] == "reproduction" else "~")
        print(
            f"  N={n:3d}: E={run['best_energy']:.9f}  known={known_str}  Δ={delta_str}  "
            f"class={run['classification']}  minima={run['distinct_minima']}  {marker}  [{elapsed:.1f}s]"
        )

    with open(outpath, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    main()
