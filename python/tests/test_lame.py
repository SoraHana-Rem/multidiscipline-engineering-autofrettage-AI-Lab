import pytest
import numpy as np
from python.lame_stress import calculate_lame_stresses

def test_lame_ground_truth_values():
    """Verify against MATLAB baseline: r_i=0.1m, r_o=0.15m, P_i=100MPa."""
    r, sigma_r, sigma_t = calculate_lame_stresses(r_i=0.10, r_o=0.15, P_i=100e6, P_o=0.0)
    
    # Inner wall boundary checks (r = r_i)
    assert np.isclose(sigma_r[0] / 1e6, -100.0, atol=1e-2)
    assert np.isclose(sigma_t[0] / 1e6, 260.0, atol=1e-2)
    
    # Outer wall boundary checks (r = r_o)
    assert np.isclose(sigma_r[-1] / 1e6, 0.0, atol=1e-2)
    assert np.isclose(sigma_t[-1] / 1e6, 160.0, atol=1e-2)

def test_invalid_geometry_guardrails():
    """Verify negative testing / parameter input boundaries."""
    with pytest.raises(ValueError, match="Inner radius .* must be smaller"):
        calculate_lame_stresses(r_i=0.20, r_o=0.15, P_i=100e6)