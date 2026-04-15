"""
Phase 1: Multi-Start Gradient Optimization for Thomson Problem
==============================================================
Minimize Coulomb energy U(N) = sum_{i<j} 1/|r_i - r_j| for N charges on S².

Usage:
    python phase1_multistart.py [--n-min 2] [--n-max 50] [--restarts 500]
"""

# pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false

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
    from scipy.optimize import minimize as scipy_minimize
except ImportError as exc:
    raise SystemExit(
        "scipy is required for Thomson experiment runs. Install research extras with: "
        "python -m pip install -e .[all]"
    ) from exc

minimize: Any = scipy_minimize
IMPROVEMENT_EPSILON = 1e-6


# Known best energies from the public Cambridge Cluster Database table.
# These are rounded benchmark values, not a full-precision oracle, so sub-micro deltas
# must be treated as reproductions unless corroborated by stronger evidence.
KNOWN_ENERGIES = {
    2: 0.500000000, 3: 1.732050808, 4: 3.674234614,
    5: 6.474691495, 6: 9.985281374, 7: 14.452977414,
    8: 19.675287861, 9: 25.759986531, 10: 32.716949460,
    11: 40.596450510, 12: 49.165253058, 13: 58.853230612,
    14: 69.306363297, 15: 80.670244114, 16: 92.911655302,
    17: 106.050404829, 18: 120.084467447, 19: 135.089467557,
    20: 150.881568334, 24: 223.347074052, 32: 412.261274651,
    48: 968.713455344, 72: 2255.001190975, 100: 4448.350634331,
}

# Known symmetry types
KNOWN_SYMMETRY = {
    2: "D∞h", 3: "D3h", 4: "Td", 5: "D3h", 6: "Oh",
    7: "D5h", 8: "D4d", 9: "D3h", 10: "D4d", 11: "C2v",
    12: "Ih", 24: "O",
}


def classify_run(delta: float | None) -> str:
    if delta is None:
        return "unbenchmarked"
    if delta < -IMPROVEMENT_EPSILON:
        return "plausible-escalation-candidate"
    if abs(delta) <= IMPROVEMENT_EPSILON:
        return "reproduction"
    return "gap"


def random_sphere_points(n: int) -> np.ndarray:
    """Generate n uniformly random points on S²."""
    points = np.random.randn(n, 3)
    norms = np.linalg.norm(points, axis=1, keepdims=True)
    return points / norms


def fibonacci_sphere(n: int) -> np.ndarray:
    """Generate n approximately uniform points on S² using Fibonacci lattice."""
    golden_ratio = (1 + np.sqrt(5)) / 2
    indices = np.arange(n)
    theta = 2 * np.pi * indices / golden_ratio
    phi = np.arccos(1 - 2 * (indices + 0.5) / n)
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(phi)
    return np.column_stack([x, y, z])


def coulomb_energy(coords_flat: np.ndarray, n: int) -> float:
    """Compute Coulomb energy from flattened coordinate array."""
    points = coords_flat.reshape(n, 3)
    # Project back to sphere
    norms = np.linalg.norm(points, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    points = points / norms

    energy = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.linalg.norm(points[i] - points[j])
            if dist > 1e-12:
                energy += 1.0 / dist
    return float(energy)


def coulomb_energy_vectorized(coords_flat: np.ndarray, n: int) -> float:
    """Vectorized Coulomb energy computation."""
    points = coords_flat.reshape(n, 3)
    norms = np.linalg.norm(points, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    points = points / norms

    # Pairwise distances
    diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    dists = np.sqrt(np.sum(diff**2, axis=2))
    # Upper triangle only
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    dists_upper = dists[mask]
    dists_upper = np.maximum(dists_upper, 1e-12)
    return float(np.sum(1.0 / dists_upper))


def coulomb_gradient(coords_flat: np.ndarray, n: int) -> np.ndarray:
    """Compute gradient of Coulomb energy with spherical projection."""
    points = coords_flat.reshape(n, 3)
    norms = np.linalg.norm(points, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    points = points / norms

    grad = np.zeros_like(points)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            diff = points[i] - points[j]
            dist = np.linalg.norm(diff)
            if dist > 1e-12:
                grad[i] -= diff / (dist ** 3)

    # Project gradient onto tangent plane of sphere at each point
    for i in range(n):
        p = points[i]
        grad[i] -= np.dot(grad[i], p) * p  # Remove radial component

    return grad.flatten()


def optimize_single(n: int, initial: np.ndarray, method: str = "L-BFGS-B") -> dict[str, Any]:
    """Run single optimization from given initial configuration."""
    x0 = initial.flatten()

    def objective(x: np.ndarray) -> float:
        return coulomb_energy_vectorized(x, n)

    def gradient(x: np.ndarray) -> np.ndarray:
        return coulomb_gradient(x, n)

    result: Any = minimize(
        objective,
        x0,
        jac=gradient,
        method=method,
        options={"maxiter": 5000, "ftol": 1e-15},
    )

    # Project final points to sphere
    final = result.x.reshape(n, 3)
    norms = np.linalg.norm(final, axis=1, keepdims=True)
    final = final / norms

    return {
        "energy": float(result.fun),
        "success": bool(result.success),
        "niter": int(result.nit),
        "config": final.tolist(),
    }


def run_multistart(n: int, restarts: int = 500) -> dict[str, Any]:
    """Multi-start optimization for N charges."""
    best_energy = float('inf')
    best_config: list[list[float]] | None = None
    all_energies: list[float] = []

    for r in range(restarts):
        if r == 0:
            initial = fibonacci_sphere(n)
        else:
            initial = random_sphere_points(n)

        result = optimize_single(n, initial)
        all_energies.append(result["energy"])

        if result["energy"] < best_energy:
            best_energy = result["energy"]
            best_config = result["config"]

    known = KNOWN_ENERGIES.get(n)
    delta = best_energy - known if known else None

    return {
        "N": n,
        "best_energy": best_energy,
        "known_energy": known,
        "delta": delta,
        "classification": classify_run(delta),
        "is_improvement": bool(delta is not None and delta < -IMPROVEMENT_EPSILON),
        "restarts": restarts,
        "energy_std": float(np.std(all_energies)),
        "energy_min": float(np.min(all_energies)),
        "distinct_minima": len(set(round(e, 6) for e in all_energies)),
        "best_config": best_config,
    }


def main():
    parser = argparse.ArgumentParser(description="Thomson problem multi-start optimizer")
    parser.add_argument("--n-min", type=int, default=2)
    parser.add_argument("--n-max", type=int, default=30)
    parser.add_argument("--restarts", type=int, default=200)
    parser.add_argument("--seed", type=int, default=1729, help="Random seed for reproducible multistart search")
    parser.add_argument("--output", type=str, default="../artifacts/phase1_results.json")
    args = parser.parse_args()

    np.random.seed(args.seed)

    outpath = Path(__file__).parent / args.output
    outpath.parent.mkdir(parents=True, exist_ok=True)

    print(f"Thomson Problem — Multi-Start Gradient Optimization")
    print(f"N range: {args.n_min} to {args.n_max}, restarts: {args.restarts}")
    print(f"Seed: {args.seed}")
    print()

    results: dict[str, Any] = {
        "meta": {"n_min": args.n_min, "n_max": args.n_max, "restarts": args.restarts, "seed": args.seed},
        "runs": {},
    }

    for n in range(args.n_min, args.n_max + 1):
        t0 = time.time()
        result = run_multistart(n, restarts=args.restarts)
        elapsed = time.time() - t0

        known_str = f"{result['known_energy']:.9f}" if result['known_energy'] else "?"
        delta_str = f"{result['delta']:+.2e}" if result['delta'] is not None else "N/A"
        marker = "★" if result["classification"] == "plausible-escalation-candidate" else ("✓" if result["classification"] == "reproduction" else "~")

        print(f"  N={n:3d}: E={result['best_energy']:.9f}  known={known_str}  Δ={delta_str}  "
              f"class={result['classification']}  minima={result['distinct_minima']}  {marker}  [{elapsed:.1f}s]")

        result["elapsed_sec"] = elapsed
        # Don't save full configs in summary (too large)
        result_summary = {k: v for k, v in result.items() if k != "best_config"}
        results["runs"][str(n)] = result_summary

    # Save best configs separately
    with open(outpath, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    main()
