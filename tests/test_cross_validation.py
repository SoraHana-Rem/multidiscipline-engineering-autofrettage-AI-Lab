import numpy as np
import pytest
from src.validation.cross_validate import python_lame_stresses


@pytest.mark.parametrize(
    "r_i, r_o, P_i, r_val, expected_sigma_r, expected_sigma_theta",
    [
        # Test Case 1: At inner radius (r = r_i), sigma_r must equal -P_i
        (0.10, 0.15, 10e6, 0.10, -10e6, 26e6),
        # Test Case 2: At outer radius (r = r_o), sigma_r must equal 0
        (0.10, 0.15, 10e6, 0.15, 0.0, 16e6),
    ],
)
def test_lame_boundary_conditions(
    r_i, r_o, P_i, r_val, expected_sigma_r, expected_sigma_theta
):
    r_arr = np.array([r_val])
    sig_r, sig_theta = python_lame_stresses(r_i, r_o, P_i, r_arr)

    np.testing.assert_allclose(sig_r[0], expected_sigma_r, atol=1e-3)
    np.testing.assert_allclose(sig_theta[0], expected_sigma_theta, rtol=1e-5)