"""
Unit tests for thin-wall, thick-wall Lamé, and failure safety factor calculations.
"""

import math
import pytest
from src.physics.thin_wall import calculate_thin_wall_stress
from src.physics.thick_wall import calculate_thick_wall_stress
from src.physics.failure import calculate_safety_factor


def test_thin_wall_stress_valid():
    # P = 10 MPa, r = 0.5 m, t = 0.05 m (r/t = 10 -> Thin wall)
    stress = calculate_thin_wall_stress(10e6, 0.5, 0.05)
    assert math.isclose(stress, 100e6, rel_tol=1e-5)


def test_thick_wall_lame_valid():
    # P = 100 MPa, r_i = 0.1 m, t = 0.05 m -> r_o = 0.15 m
    # sigma_h = 100e6 * (0.15^2 + 0.1^2) / (0.15^2 - 0.1^2) = 260 MPa
    stress = calculate_thick_wall_stress(100e6, 0.1, 0.05)
    assert math.isclose(stress, 260e6, rel_tol=1e-5)


def test_safety_factor_valid():
    sf = calculate_safety_factor(equivalent_stress=200e6, yield_strength=500e6)
    assert math.isclose(sf, 2.5, rel_tol=1e-5)


def test_safety_factor_zero_stress():
    with pytest.raises(ZeroDivisionError):
        calculate_safety_factor(equivalent_stress=0.0, yield_strength=500e6)