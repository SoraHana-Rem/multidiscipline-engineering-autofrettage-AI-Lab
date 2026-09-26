"""
Orchestrates pressure vessel analysis by linking validation, model selection, physics calculations, and yielding evaluation.
"""
import math
import warnings
from dataclasses import dataclass

from src.config.limits import THIN_WALL_RATIO_THRESHOLD
from src.errors import PressureVesselWarning, ValidationError
from src.physics import failure, thick_wall, thin_wall
from src.validation.inputs import validate_inputs


@dataclass(frozen=True)
class VesselResult:
    sigma_hoop: float
    sigma_long: float
    sigma_radial: float
    sigma_vm: float
    safety_factor: float
    yielded: bool
    model: str


def analyze_vessel(P: float, r_i: float, t: float, sigma_y: float) -> VesselResult:
    """Executes validation, selects model, calculates stresses, and evaluates yielding."""
    P_val, r_i_val, t_val, sigma_y_val = validate_inputs(P, r_i, t, sigma_y)
    ratio = r_i_val / t_val

    if ratio >= THIN_WALL_RATIO_THRESHOLD:
        model = "thin_wall"
        s_hoop = thin_wall.calculate_thin_wall_stress(P_val, r_i_val, t_val)
        s_long = thin_wall.longitudinal_stress(P_val, r_i_val, t_val)
        s_radial = 0.0
        s_vm = failure.von_mises_plane(s_hoop, s_long)
    else:
        model = "lame_thick_wall"
        warnings.warn(
            f"Using Lamé thick-wall model. Ratio r_i/t={ratio:.2f} < {THIN_WALL_RATIO_THRESHOLD}.",
            category=PressureVesselWarning,
            stacklevel=2,
        )
        s_hoop, s_long, s_radial = thick_wall.lame_stresses_inner(P_val, r_i_val, t_val)
        s_vm = failure.von_mises_triaxial(s_hoop, s_long, s_radial)

    sf_val = failure.safety_factor(sigma_y_val, s_vm)
    is_yielded = bool(s_vm >= sigma_y_val)

    outputs = (s_hoop, s_long, s_radial, s_vm, sf_val)
    if not all(math.isfinite(val) for val in outputs):
        raise ArithmeticError("Non-finite numerical result encountered during computation.")

    return VesselResult(
        sigma_hoop=s_hoop,
        sigma_long=s_long,
        sigma_radial=s_radial,
        sigma_vm=s_vm,
        safety_factor=sf_val,
        yielded=is_yielded,
        model=model,
    )