import os
import pytest
import numpy as np
import pandas as pd
from src.validation.cross_validate import python_lame_stresses, run_cross_validation


def test_python_lame_stresses_calculation():
    """Verify analytical Lamé stress formulation calculations."""
    r_i = 0.100
    r_o = 0.200
    P_i = 1e8  # 100 MPa in Pa
    r = np.array([0.100, 0.150, 0.200])

    sigma_r, sigma_theta = python_lame_stresses(r_i, r_o, P_i, r, P_o=0.0)

    # Inner boundary: sigma_r = -P_i
    assert pytest.approx(sigma_r[0], abs=1e-1) == -1e8
    # Outer boundary: sigma_r = 0
    assert pytest.approx(sigma_r[-1], abs=1e-1) == 0.0
    # Hoop stress should be positive (tensile)
    assert np.all(sigma_theta > 0)


def test_run_cross_validation_file_not_found(capsys):
    """Verify handling when the reference CSV file is missing."""
    df, status = run_cross_validation("non_existent_file.csv")
    assert df is None
    assert status == "FAIL"
    captured = capsys.readouterr().out
    assert "Error: Reference file" in captured


def test_run_cross_validation_success(tmp_path):
    """Verify cross-validation execution with mock synthetic MATLAB reference data."""
    csv_file = tmp_path / "mock_matlab.csv"
    
    r_i = 0.100
    r_o = 0.200
    P_i = 1e8
    r_eval = np.linspace(r_i, r_o, 5)
    
    sigma_r_exact, sigma_theta_exact = python_lame_stresses(r_i, r_o, P_i, r_eval)

    mock_df = pd.DataFrame({
        "r_i": [r_i] * len(r_eval),
        "r_o": [r_o] * len(r_eval),
        "P_i": [P_i] * len(r_eval),
        "P_o": [0.0] * len(r_eval),
        "r": r_eval,
        "sigma_r_matlab": sigma_r_exact,
        "sigma_theta_matlab": sigma_theta_exact
    })
    mock_df.to_csv(csv_file, index=False)

    df_res, status = run_cross_validation(str(csv_file), tolerance=1e-4)
    
    assert status == "PASS"
    assert "sigma_r_py" in df_res.columns
    assert "err_r" in df_res.columns
    assert df_res["err_r"].max() < 1e-4