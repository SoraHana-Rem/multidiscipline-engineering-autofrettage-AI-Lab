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