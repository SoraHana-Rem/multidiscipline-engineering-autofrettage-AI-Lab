"""
Unit tests for Week 7 LEFM and Paris Law fatigue calculations.
"""
import pytest
from src.errors import ValidationError
from src.physics.fracture import (
    calculate_stress_intensity,
    calculate_critical_crack_depth,
    predict_fatigue_life,
)


def test_stress_intensity_factor():
    sigma_hoop = 300.0  # MPa
    a = 2.0  # mm
    k_i = calculate_stress_intensity(sigma_hoop, a)
    
    # Expected K_I ~ 26.60 MPa*sqrt(m)
    assert k_i > 0.0
    assert pytest.approx(k_i, abs=1e-1) == 26.60


def test_invalid_crack_depth_raises_error():
    with pytest.raises(ValidationError, match="must be positive"):
        calculate_stress_intensity(sigma_hoop=300.0, a=-1.0)


def test_critical_crack_depth():
    sigma_max = 400.0  # MPa
    K_ic = 80.0  # MPa*sqrt(m) - typical high-strength steel
    a_c = calculate_critical_crack_depth(sigma_max, K_ic)
    
    # Expected a_c ~ 10.13 mm
    assert pytest.approx(a_c, abs=1e-1) == 10.13


def test_fatigue_life_prediction():
    a_init = 1.0  # 1 mm initial flaw
    a_crit = 10.0  # 10 mm critical crack
    delta_sigma = 250.0  # MPa
    C = 1.5e-11  # Typical Paris constant (SI units)
    m = 3.0
    
    cycles = predict_fatigue_life(a_init, a_crit, delta_sigma, C, m)
    
    assert cycles > 0
    # Higher cyclic stress should strictly reduce fatigue life
    cycles_high_stress = predict_fatigue_life(a_init, a_crit, delta_sigma=350.0, C=C, m=m)
    assert cycles_high_stress < cycles