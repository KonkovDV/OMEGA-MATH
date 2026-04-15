"""
Phase 1: Pseudoline Arrangement Enumerator for Kobon Triangles
===============================================================
Enumerate line arrangements and count non-overlapping triangles.

Usage:
    python phase1_pseudoline_enum.py [--k-min 3] [--k-max 12]
"""

import argparse
import json
import time
from math import atan2
from itertools import combinations
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit(
        "numpy is required for Kobon experiment runs. Install research extras with: "
        "python -m pip install -e .[all]"
    ) from exc


# Known optimal values (OEIS A006066)
KNOWN_OPTIMAL = {
    3: 1, 4: 2, 5: 5, 6: 7, 7: 11, 8: 15, 9: 21, 10: 25,
    11: 32, 12: 38, 13: 47, 14: 54, 15: 65, 16: 72, 17: 85,
    18: 93,  # best known, upper bound = 94
    19: 107, 20: 116,  # best known, upper bound = 117
    21: 133,
}


def tamura_bound(k: int) -> int:
    """Tamura's upper bound: floor(k(k-2)/3)."""
    return k * (k - 2) // 3


def improved_bound(k: int) -> int:
    """Clément–Bader improved bound for even k."""
    if k % 2 == 0:
        return int(k * (k - 7/3) / 3)
    return tamura_bound(k)


def random_line_arrangement(k: int) -> list[tuple[float, float]]:
    """Generate k random lines as (slope, intercept) pairs.
    Ensures general position (no three concurrent, no parallel)."""
    max_attempts = 1000
    for _ in range(max_attempts):
        slopes = np.random.uniform(-5, 5, k)
        intercepts = np.random.uniform(-5, 5, k)

        # Check: no two slopes equal (no parallel lines)
        if len(set(np.round(slopes, 10))) < k:
            continue

        # Check: no three concurrent
        lines = list(zip(slopes, intercepts))
        valid = True
        for i, j, l in combinations(range(k), 3):
            # Intersection of line i and j
            si, bi = lines[i]
            sj, bj = lines[j]
            sl, bl = lines[l]
            x_ij = (bj - bi) / (si - sj)
            y_ij = si * x_ij + bi
            # Check if line l passes through this point
            if abs(sl * x_ij + bl - y_ij) < 1e-8:
                valid = False
                break

        if valid:
            return lines

    # Fallback: use rotated equally-spaced lines
    lines: list[tuple[float, float]] = []
    for i in range(k):
        angle = np.pi * i / k + np.random.uniform(-0.01, 0.01)
        slope = np.tan(angle) if abs(np.cos(angle)) > 1e-10 else 1000
        intercept = np.random.uniform(-0.1, 0.1)
        lines.append((slope, intercept))
    return lines


def compute_intersections(lines: list[tuple[float, float]]) -> dict[tuple[int, int], tuple[float, float]]:
    """Compute all pairwise intersection points."""
    k = len(lines)
    intersections: dict[tuple[int, int], tuple[float, float]] = {}
    for i in range(k):
        for j in range(i + 1, k):
            si, bi = lines[i]
            sj, bj = lines[j]
            if abs(si - sj) < 1e-12:
                continue  # parallel
            x = (bj - bi) / (si - sj)
            y = si * x + bi
            intersections[(i, j)] = (x, y)
    return intersections


def normalize_point(point: tuple[float, float], digits: int = 10) -> tuple[float, float]:
    return (round(point[0], digits), round(point[1], digits))


def compute_bounding_box(
    intersections: dict[tuple[int, int], tuple[float, float]], margin: float = 5.0
) -> tuple[float, float, float, float]:
    if not intersections:
        return (-10.0, 10.0, -10.0, 10.0)
    xs = [point[0] for point in intersections.values()]
    ys = [point[1] for point in intersections.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span = max(max_x - min_x, max_y - min_y, 1.0)
    extra = margin * span
    return (min_x - extra, max_x + extra, min_y - extra, max_y + extra)


def line_box_intersections(
    line: tuple[float, float], box: tuple[float, float, float, float]
) -> list[tuple[float, float]]:
    slope, intercept = line
    min_x, max_x, min_y, max_y = box
    candidates: list[tuple[float, float]] = []

    for x in (min_x, max_x):
        y = slope * x + intercept
        if min_y - 1e-9 <= y <= max_y + 1e-9:
            candidates.append((x, y))

    if abs(slope) > 1e-12:
        for y in (min_y, max_y):
            x = (y - intercept) / slope
            if min_x - 1e-9 <= x <= max_x + 1e-9:
                candidates.append((x, y))

    unique: list[tuple[float, float]] = []
    seen: set[tuple[float, float]] = set()
    for point in candidates:
        key = normalize_point(point)
        if key not in seen:
            seen.add(key)
            unique.append(point)
    return unique[:2]


def polygon_area(points: list[tuple[float, float]]) -> float:
    area = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return 0.5 * area


def build_arrangement_graph(
    lines: list[tuple[float, float]]
) -> tuple[
    dict[int, tuple[float, float]],
    dict[int, list[int]],
    set[int],
]:
    intersections = compute_intersections(lines)
    box = compute_bounding_box(intersections)

    point_to_id: dict[tuple[float, float], int] = {}
    id_to_point: dict[int, tuple[float, float]] = {}
    boundary_ids: set[int] = set()
    next_id = 0

    def ensure_vertex(point: tuple[float, float], boundary: bool) -> int:
        nonlocal next_id
        key = normalize_point(point)
        if key not in point_to_id:
            point_to_id[key] = next_id
            id_to_point[next_id] = point
            next_id += 1
        vertex_id = point_to_id[key]
        if boundary:
            boundary_ids.add(vertex_id)
        return vertex_id

    adjacency: dict[int, set[int]] = {}

    for index, line in enumerate(lines):
        points_on_line: list[tuple[float, float]] = []
        for other in range(len(lines)):
            if other == index:
                continue
            key = (min(index, other), max(index, other))
            if key in intersections:
                points_on_line.append(intersections[key])
        points_on_line.extend(line_box_intersections(line, box))

        unique_points: list[tuple[float, float]] = []
        seen_points: set[tuple[float, float]] = set()
        for point in points_on_line:
            key = normalize_point(point)
            if key not in seen_points:
                seen_points.add(key)
                unique_points.append(point)

        unique_points.sort(key=lambda point: (point[0], point[1]))

        for point in unique_points:
            is_boundary = point in line_box_intersections(line, box)
            ensure_vertex(point, boundary=is_boundary)

        for left, right in zip(unique_points, unique_points[1:]):
            left_id = ensure_vertex(left, boundary=left in line_box_intersections(line, box))
            right_id = ensure_vertex(right, boundary=right in line_box_intersections(line, box))
            adjacency.setdefault(left_id, set()).add(right_id)
            adjacency.setdefault(right_id, set()).add(left_id)

    ordered_adjacency: dict[int, list[int]] = {}
    for vertex_id, neighbors in adjacency.items():
        px, py = id_to_point[vertex_id]
        ordered_adjacency[vertex_id] = sorted(
            neighbors,
            key=lambda neighbor_id: atan2(
                id_to_point[neighbor_id][1] - py,
                id_to_point[neighbor_id][0] - px,
            ),
        )

    return id_to_point, ordered_adjacency, boundary_ids


def count_triangles(lines: list[tuple[float, float]]) -> int:
    """Count bounded triangular faces via planar face traversal.

    This counts actual triangular cells of the line arrangement, not arbitrary triples of lines.
    """
    id_to_point, adjacency, boundary_ids = build_arrangement_graph(lines)

    visited: set[tuple[int, int]] = set()
    triangles = 0
    seen_faces: set[tuple[int, ...]] = set()

    for start, neighbors in adjacency.items():
        for nxt in neighbors:
            half_edge = (start, nxt)
            if half_edge in visited:
                continue

            face: list[int] = []
            current = half_edge

            while current not in visited:
                visited.add(current)
                u, v = current
                face.append(u)

                ordered = adjacency[v]
                reverse_index = ordered.index(u)
                w = ordered[(reverse_index - 1) % len(ordered)]
                current = (v, w)

            if len(face) < 3:
                continue

            unique_cycle = tuple(face)
            normalized = min(
                tuple(unique_cycle[i:] + unique_cycle[:i])
                for i in range(len(unique_cycle))
            )
            if normalized in seen_faces:
                continue
            seen_faces.add(normalized)

            if any(vertex_id in boundary_ids for vertex_id in unique_cycle):
                continue

            polygon = [id_to_point[vertex_id] for vertex_id in unique_cycle]
            if abs(polygon_area(polygon)) < 1e-9:
                continue

            if len(unique_cycle) == 3:
                triangles += 1

    return triangles


def optimize_arrangement(
    k: int, iterations: int = 5000, temperature: float = 1.0
) -> tuple[int, list[tuple[float, float]]]:
    """Simulated annealing to find arrangement maximizing triangle count."""
    best_lines = random_line_arrangement(k)
    best_count = count_triangles(best_lines)

    current_lines = list(best_lines)
    current_count = best_count

    for step in range(iterations):
        T = temperature * (1 - step / iterations)

        # Perturb one random line
        new_lines = list(current_lines)
        idx = np.random.randint(k)
        s, b = new_lines[idx]
        new_lines[idx] = (s + np.random.normal(0, 0.3), b + np.random.normal(0, 0.3))

        new_count = count_triangles(new_lines)

        # Accept?
        delta = new_count - current_count
        if delta > 0 or (T > 0 and np.random.random() < np.exp(delta / max(T, 1e-10))):
            current_lines = new_lines
            current_count = new_count

            if current_count > best_count:
                best_count = current_count
                best_lines = list(current_lines)

    return best_count, best_lines


def main():
    parser = argparse.ArgumentParser(description="Kobon triangle enumeration")
    parser.add_argument("--k-min", type=int, default=3)
    parser.add_argument("--k-max", type=int, default=15)
    parser.add_argument("--sa-iterations", type=int, default=10000)
    parser.add_argument("--sa-restarts", type=int, default=50)
    parser.add_argument("--seed", type=int, default=1729, help="Random seed for reproducible search")
    parser.add_argument("--output", type=str, default="../artifacts/phase1_results.json")
    args = parser.parse_args()

    np.random.seed(args.seed)

    outpath = Path(__file__).parent / args.output
    outpath.parent.mkdir(parents=True, exist_ok=True)

    print(f"Kobon Triangles — Arrangement Search")
    print(f"k range: {args.k_min} to {args.k_max}")
    print(f"SA: {args.sa_iterations} iterations × {args.sa_restarts} restarts")
    print(f"Seed: {args.seed}")
    print()

    results: dict[str, Any] = {"meta": {"k_min": args.k_min, "k_max": args.k_max, "seed": args.seed}, "runs": {}}

    for k in range(args.k_min, args.k_max + 1):
        t0 = time.time()
        known = KNOWN_OPTIMAL.get(k, "?")
        bound = tamura_bound(k)
        imp_bound = improved_bound(k)

        best_count = 0
        best_lines: list[tuple[float, float]] | None = None

        for _ in range(args.sa_restarts):
            count, lines = optimize_arrangement(k, iterations=args.sa_iterations)
            if count > best_count:
                best_count = count
                best_lines = lines

        elapsed = time.time() - t0
        marker = "✓" if best_count == known else ("★" if isinstance(known, int) and best_count > known else "~")

        print(f"  k={k:2d}: found={best_count}  known={known}  bound={bound} (imp={imp_bound})  {marker}  [{elapsed:.1f}s]")

        results["runs"][str(k)] = {
            "k": k,
            "found_triangles": best_count,
            "known_optimal": known if isinstance(known, int) else None,
            "tamura_bound": bound,
            "improved_bound": imp_bound,
            "elapsed_sec": elapsed,
            "lines": best_lines,
        }

    with open(outpath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    main()
