import numpy as np
import pandas as pd


def generate_matlab_reference_csv(
    filepath: str = "src/validation/matlab_reference.csv",
):
    r_i = 0.10  # Inner radius (m)
    r_o = 0.15  # Outer radius (m)
    P_i = 10e6  # Internal pressure (10 MPa)
    P_o = 0.0  # External pressure (0 Pa)

    r = np.linspace(r_i, r_o, 100)

    denominator = r_o**2 - r_i**2
    sigma_r_matlab = (P_i * r_i**2 / denominator) * (1 - (r_o**2 / r**2))
    sigma_theta_matlab = (P_i * r_i**2 / denominator) * (1 + (r_o**2 / r**2))

    df = pd.DataFrame(
        {
            "r": r,
            "r_i": r_i,
            "r_o": r_o,
            "P_i": P_i,
            "P_o": P_o,
            "sigma_r_matlab": sigma_r_matlab,
            "sigma_theta_matlab": sigma_theta_matlab,
        }
    )

    df.to_csv(filepath, index=False)
    print(f"Successfully generated reference CSV at: {filepath}")


if __name__ == "__main__":
    generate_matlab_reference_csv()