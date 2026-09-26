"""
Autofrettage and elastic-plastic stress calculation module.
Computes plastic zone expansion, loading stress fields, and residual stresses post-unloading.
"""
import math
from scipy.optimize import brentq
from src.errors import ValidationError


def calculate_plastic_radius(P_auto, r_i, r_o, sigma_y):
    """
    Solves for the elastic-plastic interface boundary r_p given an autofrettage pressure.

    Parameters:
        P_auto (float): Applied autofrettage pressure (MPa).
        r_i (float): Inner radius (mm).
        r_o (float): Outer radius (mm).
        sigma_y (float): Material yield strength (MPa).

    Returns:
        float: Plastic zone boundary radius r_p (mm).
    """
    # 1. Yield Pressure Bounds
    # Pressure required for initial yielding at inner bore (r_p = r_i)
    P_yield_start = (sigma_y / math.sqrt(3)) * (1.0 - (r_i / r_o) ** 2)
    
    # Pressure required for full wall yield / burst limit (r_p = r_o)
    P_full_yield = (2.0 * sigma_y / math.sqrt(3)) * math.log(r_o / r_i)

    if P_auto < P_yield_start:
        raise ValidationError(
            f"Autofrettage pressure ({P_auto:.2f} MPa) is below initial yield pressure ({P_yield_start:.2f} MPa). Vessel remains purely elastic."
        )
    
    if P_auto >= P_full_yield:
        raise ValidationError(
            f"Autofrettage pressure ({P_auto:.2f} MPa) exceeds or equals full yield pressure ({P_full_yield:.2f} MPa). Risk of plastic collapse."
        )

    # 2. Objective Function f(r_p) = 0
    def objective(r_p):
        term1 = 1.0 - (r_p / r_o) ** 2
        term2 = 2.0 * math.log(r_p / r_i)
        return (sigma_y / math.sqrt(3)) * (term1 + term2) - P_auto

    # 3. Solve using Brent's method on the bracket (r_i, r_o)
    r_p_sol = brentq(objective, r_i, r_o, xtol=1e-6)
    return float(r_p_sol)


import numpy as np


def calculate_autofrettage_stresses(P_auto, r_i, r_o, sigma_y, num_points=100):
    """
    Computes loading, unloading, and residual stress profiles across the wall thickness.

    Returns:
        dict: Arrays for radius, loading stresses, unloading stresses, and residual stresses (MPa).
    """
    r_p = calculate_plastic_radius(P_auto, r_i, r_o, sigma_y)
    r_grid = np.linspace(r_i, r_o, num_points)

    sigma_r_load = np.zeros(num_points)
    sigma_theta_load = np.zeros(num_points)

    k = sigma_y / math.sqrt(3)

    # 1. Loading Stresses Across Radial Grid
    for idx, r in enumerate(r_grid):
        if r <= r_p:
            # Plastic inner zone
            sigma_r_load[idx] = -k * (1.0 - (r_p / r_o) ** 2 + 2.0 * math.log(r_p / r))
            sigma_theta_load[idx] = k * (1.0 + (r_p / r_o) ** 2 - 2.0 * math.log(r_p / r))
        else:
            # Elastic outer zone
            sigma_r_load[idx] = -k * ((r_p / r_o) ** 2) * ((r_o / r) ** 2 - 1.0)
            sigma_theta_load[idx] = k * ((r_p / r_o) ** 2) * ((r_o / r) ** 2 + 1.0)

    # 2. Elastic Unloading Stresses (Lamé)
    k_geo = (r_i ** 2) / (r_o ** 2 - r_i ** 2)
    sigma_r_unload = -P_auto * k_geo * (1.0 - (r_o / r_grid) ** 2)
    sigma_theta_unload = P_auto * k_geo * (1.0 + (r_o / r_grid) ** 2)

    # 3. Residual Stresses
    sigma_r_res = sigma_r_load - sigma_r_unload
    sigma_theta_res = sigma_theta_load - sigma_theta_unload

    return {
        "r_p": r_p,
        "radius": r_grid,
        "sigma_r_res": sigma_r_res,
        "sigma_theta_res": sigma_theta_res,
        "sigma_r_load": sigma_r_load,
        "sigma_theta_load": sigma_theta_load,
    }