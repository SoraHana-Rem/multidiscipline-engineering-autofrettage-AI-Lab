    # -*- coding: utf-8 -*-
"""Visualization helpers for autofrettage residual stress plots."""

import os

import matplotlib.pyplot as plt

from src.physics.autofrettage import calculate_autofrettage_stresses


def generate_residual_stress_plot(
    r_i: float,
    r_o: float,
    sigma_y: float,
    P_auto: float,
    output_path: str = "outputs/residual_stress.png",
) -> str:
    """REQ-AUT-001, REQ-AUT-003: Plot residual hoop stresses from the solver."""
    results = calculate_autofrettage_stresses(
        P_auto=P_auto,
        r_i=r_i,
        r_o=r_o,
        sigma_y=sigma_y,
        num_points=200,
    )

    radii = results["radius"]
    residual_hoop = results["sigma_theta_res"]
    r_p = results["r_p"]

    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(
        radii,
        residual_hoop,
        color="#1f77b4",
        linewidth=2.5,
        label="Residual Hoop Stress (MPa)",
    )

    ax.axvline(
        x=r_p,
        color="#d62728",
        linestyle="--",
        linewidth=1.5,
        label=f"Plastic Boundary (r_p = {r_p:.1f} mm)",
    )

    ax.axhline(0, color="gray", linestyle=":", linewidth=0.8)

    ax.set_title(
        "Autofrettage Residual Hoop Stress Profile",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Wall Radius r (mm)")
    ax.set_ylabel("Residual Stress (MPa)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="best")
    fig.tight_layout()

    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    return output_path


