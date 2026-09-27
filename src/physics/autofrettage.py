"""
Autofrettage and elastic-plastic stress calculation module.
Computes plastic zone expansion, loading stress fields, and residual stresses post-unloading.
"""
import math
import numpy as np
from scipy.optimize import brentq
from src.errors import ValidationError


class AutofrettageResult:
    """Data transfer object for orchestrator results."""
    def __init__(self, r_p: float, residual_hoop_inner: float, safety_factor: float = 1.0):
        self.r_p = r_p
        self.residual_hoop_inner = residual_hoop_inner
        self.safety_factor = safety_factor


def calculate_plastic_radius(P_auto: float, r_i: float, r_o: float, sigma_y: float) -> float:
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


def calculate_autofrettage_stresses(P_auto: float, r_i: float, r_o: float, sigma_y: float, num_points: int = 100) -> dict:
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
    k_geo = (P_auto * r_i ** 2) / (r_o ** 2 - r_i ** 2)
    sigma_r_unload = k_geo * (1.0 - (r_o / r_grid) ** 2)
    sigma_theta_unload = k_geo * (1.0 + (r_o / r_grid) ** 2)

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


def calculate_autofrettage(P_auto: float, r_i: float, r_o: float, sigma_y: float, P_working: float = None) -> AutofrettageResult:
    """
    Orchestrator entry point called by src.main.
    Computes plastic radius, inner bore residual hoop stress, and enhanced working safety factor.
    """
    res = calculate_autofrettage_stresses(P_auto=P_auto, r_i=r_i, r_o=r_o, sigma_y=sigma_y, num_points=100)
    r_p = float(res["r_p"])
    residual_hoop_inner = float(res["sigma_theta_res"][0])
    
    # Enhanced Safety Factor Calculation under working pressure
    if P_working is not None and P_working > 0:
        # Working elastic Lamé stresses at inner bore
        denom = r_o ** 2 - r_i ** 2
        sigma_r_work = -P_working
        sigma_theta_work = P_working * (r_o ** 2 + r_i ** 2) / denom
        sigma_z_work = P_working * (r_i ** 2) / denom

        # Superimpose compressive residual hoop stress
        sigma_theta_net = sigma_theta_work + residual_hoop_inner
        sigma_r_net = sigma_r_work
        sigma_z_net = sigma_z_work

        # Net Equivalent von Mises Stress
        sigma_vm_net = math.sqrt(
            0.5 * (
                (sigma_r_net - sigma_theta_net) ** 2 +
                (sigma_theta_net - sigma_z_net) ** 2 +
                (sigma_z_net - sigma_r_net) ** 2
            )
        )
        sf_enhanced = float(sigma_y / sigma_vm_net)
    else:
        sf_enhanced = 1.0

    return AutofrettageResult(
        r_p=r_p,
        residual_hoop_inner=residual_hoop_inner,
        safety_factor=sf_enhanced
    )