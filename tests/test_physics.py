"""Unit tests for thin-wall, thick-wall Lamé, and failure safety factor calculations."""

import math
import pytest
import numpy as np
from src.physics.thin_wall import hoop_stress, longitudinal_stress
from src.physics.thick_wall import calculate_thick_wall_stress, lame_stresses_inner
from src.physics.failure import von_mises_plane, von_mises_triaxial, safety_factor


def test_thin_wall_stress_valid():
    """REQ-FUN-001: Thin-wall stress verification."""
    stress = hoop_stress(10.0, 500.0, 50.0)
    assert math.isclose(stress, 100.0, rel_tol=1e-5)


def test_thick_wall_lame_valid():
    """REQ-FUN-004: Thick-wall Lamé inner hoop stress verification."""
    s_hoop, _, _ = lame_stresses_inner(100.0, 100.0, 50.0)
    assert math.isclose(s_hoop, 260.0, rel_tol=1e-5)


def test_safety_factor_valid():
    """REQ-FUN-005: Yield safety factor calculation."""
    sf = safety_factor(500.0, 200.0)
    assert math.isclose(sf, 2.5, rel_tol=1e-5)


def test_safety_factor_zero_stress():
    """REQ-VAL-002: Zero stress handling in safety factor."""
    with pytest.raises(ZeroDivisionError):
        safety_factor(500.0, 0.0)


def test_lame_inner_outer_boundary_conditions():
    """REQ-FUN-006: Boundary conditions for Lamé inner stresses."""
    s_h, s_l, s_r = lame_stresses_inner(100.0, 50.0, 50.0)
    assert math.isclose(s_r, -100.0, abs_tol=1e-3)