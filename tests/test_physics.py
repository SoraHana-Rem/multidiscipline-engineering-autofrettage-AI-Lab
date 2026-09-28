"""
Unit tests for thin-wall, thick-wall Lamé, and failure safety factor calculations.
"""

import math

import numpy as np
import pytest

from python.lame_stress import calculate_lame_stresses
from src.physics.failure import safety_factor
from src.physics.thick_wall import calculate_thick_wall_stress
from src.physics.thin_wall import calculate_thin_wall_stress


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
    sf = safety_factor(sigma_y=500e6, sigma_vm=200e6)
    assert math.isclose(sf, 2.5, rel_tol=1e-5)


def test_safety_factor_zero_stress():
    with pytest.raises(ZeroDivisionError):
        safety_factor(sigma_y=500e6, sigma_vm=0.0)


def test_safety_factor_negative_stress():
    with pytest.raises(ValueError):
        safety_factor(sigma_y=500e6, sigma_vm=-1.0)


def test_safety_factor_rejects_bool():
    with pytest.raises(TypeError):
        safety_factor(sigma_y=True, sigma_vm=200e6)


def test_lame_inner_outer_boundary_conditions():
    # Setup test case: r_i = 50mm, r_o = 100mm, P_i = 100 MPa
    data = calculate_lame_stresses(r_i=0.050, r_o=0.100, P_i=100e6)

    # 1. Inner boundary check: radial stress must match -P_i (-100 MPa)
    assert np.isclose(data["s_r"][0], -100e6, atol=1e-3)

    # 2. Outer boundary check: radial stress must equal 0 MPa
    assert np.isclose(data["s_r"][-1], 0.0, atol=1e-3)

    # 3. Inner hoop stress check: 166.667 MPa
    assert np.isclose(data["s_t"][0], 166.6667e6, rtol=1e-4)


def test_invalid_radius_guardrail():
    # Verify ValueError is raised when inner radius >= outer radius
    with pytest.raises(ValueError, match="Inner radius"):
        calculate_lame_stresses(r_i=0.100, r_o=0.050, P_i=100e6)