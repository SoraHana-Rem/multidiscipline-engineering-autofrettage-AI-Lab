import os
import numpy as np
import pandas as pd


def python_lame_stresses(
    r_i: float, r_o: float, P_i: float, r: np.ndarray, P_o: float = 0.0
):
    """Calculates Lamé radial (sigma_r) and hoop (sigma_theta) stresses.

    Args:
        r_i: Inner radius (m)
        r_o: Outer radius (m)
        P_i: Internal pressure (Pa)
        r: Array of radial points (m)
        P_o: External pressure (Pa), defaults to 0.0

    Returns:
        sigma_r: Radial stress array (Pa)
        sigma_theta: Hoop stress array (Pa)
    """
    denominator = r_o**2 - r_i**2

    # Correct Lamé equation signs:
    # Radial stress uses MINUS for 1/r^2 term
    # Hoop stress uses PLUS for 1/r^2 term
    sigma_r = (P_i * r_i**2 - P_o * r_o**2) / denominator - (
        (P_i - P_o) * (r_i**2 * r_o**2) / (r**2 * denominator)
    )
    sigma_theta = (P_i * r_i**2 - P_o * r_o**2) / denominator + (
        (P_i - P_o) * (r_i**2 * r_o**2) / (r**2 * denominator)
    )

    return sigma_r, sigma_theta


def run_cross_validation(matlab_data_path: str, tolerance: float = 1e-5):
    """Compares MATLAB reference outputs against Python engine calculations."""
    if not os.path.exists(matlab_data_path):
        print(f"Error: Reference file '{matlab_data_path}' not found.")
        return None, "FAIL"

    df = pd.read_csv(matlab_data_path)

    r_i = df["r_i"].iloc[0]
    r_o = df["r_o"].iloc[0]
    P_i = df["P_i"].iloc[0]
    P_o = df["P_o"].iloc[0] if "P_o" in df.columns else 0.0
    r_eval = df["r"].to_numpy()

    sigma_r_py, sigma_theta_py = python_lame_stresses(r_i, r_o, P_i, r_eval, P_o)

    df["sigma_r_py"] = sigma_r_py
    df["sigma_theta_py"] = sigma_theta_py

    # Use max(abs(matlab), abs(P_i)) to avoid division by zero at outer boundary (sigma_r = 0)
    denom_r = np.maximum(np.abs(df["sigma_r_matlab"]), P_i)
    denom_theta = np.maximum(np.abs(df["sigma_theta_matlab"]), P_i)

    df["err_r"] = np.abs(df["sigma_r_py"] - df["sigma_r_matlab"]) / denom_r
    df["err_theta"] = (
        np.abs(df["sigma_theta_py"] - df["sigma_theta_matlab"]) / denom_theta
    )

    max_err = max(df["err_r"].max(), df["err_theta"].max())
    status = "PASS" if max_err < tolerance else "FAIL"

    print("--- Dual-Engine Cross-Validation Summary ---")
    print(f"Max Relative Error: {max_err:.4e}")
    print(f"Validation Status : {status}")

    return df, status


if __name__ == "__main__":
    run_cross_validation("src/validation/matlab_reference.csv")
