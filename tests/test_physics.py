"""Tests for pressure-vessel physics and the safety-factor interface."""

import math

import pytest

from src.physics.thin_wall import hoop_stress
from src.physics.thick_wall import lame_stresses_inner
from src.physics.failure import safety_factor


def test_thin_wall_stress_valid():
    """REQ-FUN-004: Verify thin-wall hoop stress."""
    stress = hoop_stress(10.0, 500.0, 50.0)
    assert math.isclose(stress, 100.0, rel_tol=1e-5)


def test_thick_wall_lame_valid():
    """REQ-FUN-004: Verify thick-wall inner hoop stress."""
    s_hoop, _, _ = lame_stresses_inner(100.0, 100.0, 50.0)
    assert math.isclose(s_hoop, 260.0, rel_tol=1e-5)


def test_safety_factor_valid():
    """REQ-FUN-004, REQ-FUN-005: Verify positional safety-factor inputs."""
    sf = safety_factor(500.0, 200.0)
    assert math.isclose(sf, 2.5, rel_tol=1e-5)


def test_safety_factor_canonical_keywords():
    """REQ-FUN-004: Verify the single supported keyword interface."""
    sf = safety_factor(sigma_y=500.0, sigma_vm=200.0)
    assert math.isclose(sf, 2.5, rel_tol=1e-5)


def test_safety_factor_legacy_keywords_rejected():
    """REQ-FUN-004: Unsupported argument names must not override inputs."""
    with pytest.raises(TypeError):
        safety_factor(
            sigma_y=500.0,
            sigma_vm=200.0,
            yield_strength=1000.0,
            equivalent_stress=100.0,
        )


def test_safety_factor_zero_stress():
    """REQ-FUN-004: Zero equivalent stress raises a numerical error."""
    with pytest.raises(ZeroDivisionError):
        safety_factor(500.0, 0.0)


def test_lame_inner_outer_boundary_conditions():
    """REQ-FUN-004: Verify the Lamé inner radial boundary condition."""
    _, _, s_radial = lame_stresses_inner(100.0, 50.0, 50.0)
    assert math.isclose(s_radial, -100.0, abs_tol=1e-3)


@pytest.mark.parametrize("field", ["sigma_y", "sigma_vm"])
@pytest.mark.parametrize("value", [True, "50", None, 1 + 2j])
def test_safety_factor_rejects_invalid_types(field, value):
    """REQ-TYP-002..004: Reject unsupported helper inputs."""
    inputs = {
        "sigma_y": 250.0,
        "sigma_vm": 50.0,
    }
    inputs[field] = value

    with pytest.raises(TypeError, match=field):
        safety_factor(**inputs)


@pytest.mark.parametrize("field", ["sigma_y", "sigma_vm"])
@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), float("-inf")],
)
def test_safety_factor_rejects_non_finite(field, value):
    """REQ-VAL-001: Reject non-finite helper inputs."""
    inputs = {
        "sigma_y": 250.0,
        "sigma_vm": 50.0,
    }
    inputs[field] = value

    with pytest.raises(ValueError, match=field):
        safety_factor(**inputs)


@pytest.mark.parametrize("strength", [0.0, -250.0])
def test_safety_factor_rejects_non_positive_strength(strength):
    """REQ-VAL-005: Yield strength must be positive."""
    with pytest.raises(ValueError, match="sigma_y"):
        safety_factor(strength, 50.0)


def test_safety_factor_rejects_negative_equivalent_stress():
    """REQ-FUN-004: Equivalent stress cannot be negative."""
    with pytest.raises(ValueError, match="sigma_vm"):
        safety_factor(250.0, -50.0)


def test_safety_factor_accepts_tiny_positive_stress():
    """REQ-FUN-004: No arbitrary near-zero cutoff."""
    assert safety_factor(250.0, 1e-14) == pytest.approx(2.5e16)


def test_safety_factor_rejects_result_overflow():
    """REQ-ERR-005: SF overflow raises instead of returning infinity."""
    with pytest.raises(ArithmeticError):
        safety_factor(1e308, 1e-308)


@pytest.mark.parametrize(
    "pressure,thickness",
    [
        (1e-14, 5.0),
        (1e-200, 5.0),
        (1e-200, 20.0),
    ],
)
def test_analysis_accepts_tiny_positive_pressure(pressure, thickness):
    """REQ-INP-001, REQ-ERR-005: Accept finite tiny-pressure results."""
    from src.analysis import analyze_vessel

    result = analyze_vessel(
        pressure,
        50.0,
        thickness,
        250.0,
    )

    assert result.sigma_vm > 0
    assert math.isfinite(result.safety_factor)
    assert result.safety_factor == pytest.approx(
        250.0 / result.sigma_vm
    )