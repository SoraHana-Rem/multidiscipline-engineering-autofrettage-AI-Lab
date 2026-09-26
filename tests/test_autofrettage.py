"""
Unit tests for Week 6 autofrettage plastic zone calculations.
"""

"""
Unit tests for Week 6 autofrettage plastic zone calculations.
"""
import pytest
from src.errors import ValidationError
from src.physics.autofrettage import (
    calculate_plastic_radius,
    calculate_autofrettage_stresses,
)

def test_plastic_radius_valid_range():
    r_i = 100.0
    r_o = 200.0
    sigma_y = 500.0
    P_auto = 250.0  # Pressure between initial yield (~216.5 MPa) and full plastic (~400.3 MPa)

    r_p = calculate_plastic_radius(P_auto, r_i, r_o, sigma_y)

    assert r_i < r_p < r_o
    assert pytest.approx(r_p, abs=1e-2) == 108.28


def test_plastic_radius_below_yield_raises_error():
    with pytest.raises(ValidationError, match="below initial yield pressure"):
        calculate_plastic_radius(P_auto=50.0, r_i=100.0, r_o=200.0, sigma_y=500.0)


def test_plastic_radius_exceeds_full_yield_raises_error():
    with pytest.raises(ValidationError, match="exceeds or equals full yield pressure"):
        calculate_plastic_radius(P_auto=500.0, r_i=100.0, r_o=200.0, sigma_y=500.0)


        from src.physics.autofrettage import calculate_autofrettage_stresses


def test_residual_hoop_stress_is_compressive_at_bore():
    r_i, r_o, sigma_y, P_auto = 100.0, 200.0, 500.0, 250.0
    results = calculate_autofrettage_stresses(P_auto, r_i, r_o, sigma_y)

    # Inner bore (index 0) must have negative (compressive) residual hoop stress
    hoop_res_inner = results["sigma_theta_res"][0]
    assert hoop_res_inner < 0.0
    
    # Outer wall (index -1) must have tensile residual hoop stress (reacting force)
    hoop_res_outer = results["sigma_theta_res"][-1]
    assert hoop_res_outer > 0.0