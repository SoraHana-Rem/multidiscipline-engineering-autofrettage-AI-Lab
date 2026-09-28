import os
import numpy as np
import matplotlib.pyplot as plt


def generate_residual_stress_plot(
    r_i: float, 
    r_o: float, 
    r_p: float, 
    sigma_y: float, 
    P_auto: float, 
    output_path: str = "outputs/residual_stress.png"
) -> str:
    """Generates and saves a residual hoop stress distribution plot across the wall thickness."""
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    radii = np.linspace(r_i, r_o, 200)
    residual_hoop = []

    for r in radii:
        if r <= r_p:
            stress = sigma_y * (1 - np.log(r_p / r) - (r_p**2 / (r_o**2 - r_i**2)) * (1 + (r_o**2 / r**2)))
        else:
            stress = sigma_y * (r_p**2 / (r_o**2 - r_i**2)) * (1 - (r_o**2 / r**2))
        residual_hoop.append(stress)

    plt.figure(figsize=(9, 5))
    plt.plot(radii, residual_hoop, color="#1f77b4", linewidth=2.5, label="Residual Hoop Stress (MPa)")
    plt.axvline(x=r_p, color="#d62728", linestyle="--", linewidth=1.5, label=f"Plastic Boundary (r_p = {r_p:.1f} mm)")
    plt.axhline(0, color="gray", linestyle=":", linewidth=0.8)

    plt.title("Autofrettage Residual Hoop Stress Profile", fontsize=12, fontweight="bold")
    plt.xlabel("Wall Radius r (mm)")
    plt.ylabel("Residual Stress (MPa)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="best")
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()
    return output_path