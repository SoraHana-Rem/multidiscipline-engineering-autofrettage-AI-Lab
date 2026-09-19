import pytest
import numpy as np
from python.lame_stress import calculate_lame_stresses

def test_lame_stress_inner_wall():
    data = calculate_lame_stresses(r_i=0.050, r_o=0.100, P_i=100e6, P_o=0.0)
    
    # Check inner wall values against MATLAB hand-calc baseline
    assert np.isclose(data["s_r"][0], -100e6, rtol=1e-4)        # -100.000 MPa
    assert np.isclose(data["s_t"][0], 166.667e6, rtol=1e-4)     # 166.667 MPa
    assert np.isclose(data["s_z"], 33.333e6, rtol=1e-4)         # 33.333 MPa
    assert np.isclose(data["u_r"][0], 46.667e-6, rtol=1e-4)     # 46.667 um
    assert np.isclose(data["vm"][0], 230.940e6, rtol=1e-4)      # 230.940 MPa

def test_lame_stress_outer_wall():
    data = calculate_lame_stresses(r_i=0.050, r_o=0.100, P_i=100e6, P_o=0.0)
    
    # Check outer wall values against MATLAB hand-calc baseline
    assert np.isclose(data["s_r"][-1], 0.0, atol=1e-3)          # 0 MPa boundary
    assert np.isclose(data["s_t"][-1], 66.667e6, rtol=1e-4)      # 66.667 MPa
    assert np.isclose(data["u_r"][-1], 28.333e-6, rtol=1e-4)     # 28.333 um
    assert np.isclose(data["vm"][-1], 57.735e6, rtol=1e-4)      # 57.735 MPa