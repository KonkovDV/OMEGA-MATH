"""Hessian checks for the Thomson certification script.

The regular tetrahedron is the known minimum for N=4. A square on the equator
is also a critical point (every force is radial by symmetry), but it is a
saddle: tilting it towards a tetrahedron lowers the energy.
"""

import importlib
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
mp_module = pytest.importorskip("mpmath")

EXPERIMENTS = Path(__file__).resolve().parents[1] / "research" / "active" / "thomson-problem" / "experiments"


@pytest.fixture(scope="module")
def certify():
    sys.path.insert(0, str(EXPERIMENTS))
    try:
        module = importlib.import_module("phase3_certify")
    finally:
        sys.path.remove(str(EXPERIMENTS))
    mp_module.mp.dps = 60
    return module


def _run(certify, points):
    return certify.certify_run(
        n=len(points),
        run_payload={"best_config": points, "best_energy": 0.0},
        source_artifact=Path("inline"),
        skip_hessian=False,
        hessian_step=1e-4,
        force_tolerance=1e-8,
        eigen_tolerance=1e-7,
        zero_tolerance=1e-6,
    )


def test_tetrahedron_is_local_minimum_with_three_rotation_modes(certify):
    s = 1 / np.sqrt(3)
    points = [[s, s, s], [s, -s, -s], [-s, s, -s], [-s, -s, s]]
    result = _run(certify, points)
    assert result["certification_status"] == "numerical-local-minimum-candidate"
    assert result["zero_like_eigenvalues"] == 3
    assert abs(result["high_precision_energy_float"] - 3.674234614174767) < 1e-12


def test_equatorial_square_is_flagged_as_saddle(certify):
    points = [[1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0]]
    result = _run(certify, points)
    assert float(result["max_tangent_force_norm_mp"]) < 1e-20
    assert result["negative_eigenvalues_excluding_symmetry"] >= 1
    assert result["certification_status"] == "numerical-review-needed"


def test_mpmath_hessian_is_symmetric_and_free_of_double_rounding_noise(certify):
    s = 1 / np.sqrt(3)
    points = np.array([[s, s, s], [s, -s, -s], [-s, s, -s], [-s, -s, s]])
    hessian, eigenvalues = certify.finite_difference_hessian(points, 1e-4)
    assert np.allclose(hessian, hessian.T)
    near_zero = sorted(abs(value) for value in eigenvalues)[:3]
    assert max(near_zero) < 1e-6