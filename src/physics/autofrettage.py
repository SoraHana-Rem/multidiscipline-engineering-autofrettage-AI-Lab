"""
Autofrettage loading and residual-stress calculations.

Units:
    Pressure and stress: MPa
    Radii: mm

Safety factor is None when working pressure is not supplied.
"""

import math
from numbers import Real

import numpy as np
from scipy.optimize import brentq

from src.errors import ValidationError


def _positive_real(name, value, unit):
    """REQ-AUT-001, REQ-AUT-004: Validate an extension scalar."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise TypeError(
            f"{name} must be a real number, not {type(value).__name__}"
        )

    value = float(value)

    if not math.isfinite(value) or value <= 0:
        raise ValidationError(
            f"{name} must be finite and positive: got {value} {unit}"
        )

    return value


def _validate_autofrettage_inputs(P_auto, r_i, r_o, sigma_y):
    """REQ-AUT-001, REQ-AUT-002: Validate pressure, geometry and strength."""
    P_auto = _positive_real("P_auto", P_auto, "MPa")
    r_i = _positive_real("r_i", r_i, "mm")
    r_o = _positive_real("r_o", r_o, "mm")
    sigma_y = _positive_real("sigma_y", sigma_y, "MPa")

    if r_o <= r_i:
        raise ValidationError(
            f"r_o must exceed r_i: got r_o={r_o} mm, r_i={r_i} mm"
        )

    return P_auto, r_i, r_o, sigma_y


class AutofrettageResult:
    """Result container; safety factor is None when not calculated."""

    def __init__(
        self,
        r_p: float,
        residual_hoop_inner: float,
        safety_factor: float | None = None,
    ):
        self.r_p = r_p
        self.residual_hoop_inner = residual_hoop_inner
        self.safety_factor = safety_factor


def calculate_plastic_radius(
    P_auto: float,
    r_i: float,
    r_o: float,
    sigma_y: float,
) -> float:
    """
    REQ-AUT-001, REQ-AUT-002: Solve the elastic-plastic boundary radius.

    Autofrettage pressure must be strictly above initial yield
    and strictly below full yield.
    """
    P_auto, r_i, r_o, sigma_y = _validate_autofrettage_inputs(
        P_auto, r_i, r_o, sigma_y
    )

    P_yield_start = (
        sigma_y / math.sqrt(3)
    ) * (1.0 - (r_i / r_o) ** 2)

    P_full_yield = (
        2.0 * sigma_y / math.sqrt(3)
    ) * math.log(r_o / r_i)

    if P_auto <= P_yield_start:
        raise ValidationError(
            f"Autofrettage pressure ({P_auto:.2f} MPa) "
            f"is below initial yield pressure or equal to it "
            f"({P_yield_start:.2f} MPa). No finite plastic zone is formed."
        )

    if P_auto >= P_full_yield:
        raise ValidationError(
            f"Autofrettage pressure ({P_auto:.2f} MPa) "
            f"exceeds or equals full yield pressure "
            f"({P_full_yield:.2f} MPa). Risk of plastic collapse."
        )

    def objective(r_p):
        term1 = 1.0 - (r_p / r_o) ** 2
        term2 = 2.0 * math.log(r_p / r_i)
        return (
            sigma_y / math.sqrt(3)
        ) * (term1 + term2) - P_auto

    r_p_sol = brentq(objective, r_i, r_o, xtol=1e-6)
    return float(r_p_sol)


def calculate_autofrettage_stresses(
    P_auto: float,
    r_i: float,
    r_o: float,
    sigma_y: float,
    num_points: int = 100,
) -> dict:
    """
    REQ-AUT-001, REQ-AUT-003: Compute loading and residual stress profiles.

    Unloading is assumed purely elastic.
    Profile point count must be an integer of at least two.
    """
    P_auto, r_i, r_o, sigma_y = _validate_autofrettage_inputs(
        P_auto, r_i, r_o, sigma_y
    )

    if isinstance(num_points, (bool, np.bool_)) or not isinstance(
        num_points, (int, np.integer)
    ):
        raise TypeError("num_points must be an integer")

    if num_points < 2:
        raise ValidationError("num_points must be at least 2")

    num_points = int(num_points)

    r_p = calculate_plastic_radius(P_auto, r_i, r_o, sigma_y)
    r_grid = np.linspace(r_i, r_o, num_points)

    sigma_r_load = np.zeros(num_points)
    sigma_theta_load = np.zeros(num_points)

    k = sigma_y / math.sqrt(3)

    for idx, r in enumerate(r_grid):
        if r <= r_p:
            # Plastic inner zone.
            sigma_r_load[idx] = -k * (
                1.0
                - (r_p / r_o) ** 2
                + 2.0 * math.log(r_p / r)
            )
            sigma_theta_load[idx] = k * (
                1.0
                + (r_p / r_o) ** 2
                - 2.0 * math.log(r_p / r)
            )
        else:
            # Elastic outer zone.
            sigma_r_load[idx] = -k * (r_p / r_o) ** 2 * (
                (r_o / r) ** 2 - 1.0
            )
            sigma_theta_load[idx] = k * (r_p / r_o) ** 2 * (
                (r_o / r) ** 2 + 1.0
            )

    # Elastic Lamé unloading.
    k_geo = (P_auto * r_i**2) / (r_o**2 - r_i**2)

    sigma_r_unload = k_geo * (
        1.0 - (r_o / r_grid) ** 2
    )
    sigma_theta_unload = k_geo * (
        1.0 + (r_o / r_grid) ** 2
    )

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


def calculate_autofrettage(
    P_auto: float,
    r_i: float,
    r_o: float,
    sigma_y: float,
    P_working: float | None = None,
) -> AutofrettageResult:
    """
    REQ-AUT-001, REQ-AUT-003, REQ-AUT-004: Return autofrettage results.

    When working pressure is supplied, return a bore-only von Mises
    yield safety-factor estimate using residual-hoop superposition.

    Working radial and closed-end axial stresses are included.
    Residual axial stress is omitted. Elastic reloading is assumed.

    This calculation does not establish the minimum safety factor
    across the wall or guarantee improvement over the baseline.

    When working pressure is omitted, safety_factor is None.
    """
    P_auto, r_i, r_o, sigma_y = _validate_autofrettage_inputs(
        P_auto, r_i, r_o, sigma_y
    )

    if P_working is not None:
        P_working = _positive_real("P_working", P_working, "MPa")

    res = calculate_autofrettage_stresses(
        P_auto=P_auto,
        r_i=r_i,
        r_o=r_o,
        sigma_y=sigma_y,
        num_points=100,
    )

    r_p = float(res["r_p"])
    residual_hoop_inner = float(res["sigma_theta_res"][0])

    if P_working is not None:
        denom = r_o**2 - r_i**2

        sigma_r_work = -P_working
        sigma_theta_work = (
            P_working * (r_o**2 + r_i**2) / denom
        )
        sigma_z_work = P_working * r_i**2 / denom

        sigma_theta_net = sigma_theta_work + residual_hoop_inner
        sigma_r_net = sigma_r_work
        sigma_z_net = sigma_z_work

        sigma_vm_net = math.sqrt(
            0.5 * (
                (sigma_r_net - sigma_theta_net) ** 2
                + (sigma_theta_net - sigma_z_net) ** 2
                + (sigma_z_net - sigma_r_net) ** 2
            )
        )

        sf_enhanced = float(sigma_y / sigma_vm_net)
    else:
        sf_enhanced = None

    return AutofrettageResult(
        r_p=r_p,
        residual_hoop_inner=residual_hoop_inner,
        safety_factor=sf_enhanced,
    )