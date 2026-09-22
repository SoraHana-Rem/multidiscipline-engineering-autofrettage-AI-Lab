"""
Custom warnings and exception classes for pressure vessel analysis.
"""

class PressureVesselWarning(UserWarning):
    """Emitted when a thick-wall (Lamé) regime is selected (REQ-FUN-002)."""
    pass


class ValidationError(ValueError):
    """Base exception for validation failures in the pressure vessel module."""
    pass

"""
Input validation guardrails for pressure vessel analysis.
Enforces type, finiteness, positivity, and physical range limits (REQ-TYP, REQ-VAL, REQ-INP).
"""
import math

from src.config.limits import (
    PRESSURE_MAX,
    PRESSURE_MIN,
    RADIUS_MAX,
    RADIUS_MIN,
    THICKNESS_MAX,
    THICKNESS_MIN,
    YIELD_MAX,
    YIELD_MIN,
)
from src.errors import ValidationError


def validate_inputs(P: float, r_i: float, t: float, sigma_y: float) -> tuple[float, float, float, float]:
    """
    Validates input parameters against single-source-of-truth limits.
    Returns inputs converted to float upon successful validation.
    """
    params = [
        ("Pressure", P, PRESSURE_MIN, PRESSURE_MAX, "P"),
        ("Inner radius", r_i, RADIUS_MIN, RADIUS_MAX, "r_i"),
        ("Wall thickness", t, THICKNESS_MIN, THICKNESS_MAX, "t"),
        ("Yield strength", sigma_y, YIELD_MIN, YIELD_MAX, "sigma_y"),
    ]

    # 1. Type validation (REQ-TYP-001..004)
    for name, val, _, _, _ in params:
        if isinstance(val, bool):
            raise TypeError("must be a numeric float or int: got bool")
        if not isinstance(val, (int, float)):
            raise TypeError(f"Parameter '{name}' must be a numeric float or int.")

    # 2. Finiteness validation (REQ-VAL-001)
    for name, val, _, _, _ in params:
        if not math.isfinite(val):
            raise ValueError(f"{name} must be finite")

    # 3. Positivity check (REQ-VAL-002..005)
    for name, val, _, _, _ in params:
        if val <= 0:
            raise ValidationError(f"{name} must be positive")

    # 4. Range Limits Check (REQ-VAL-006, REQ-INP)
    for name, val, min_val, max_val, code in params:
        if val < min_val or val > max_val:
            if name == "Pressure":
                raise ValidationError("Pressure out of range")
            raise ValidationError(f"Parameter '{code}'={val} is out of valid range [{min_val}, {max_val}].")

    return float(P), float(r_i), float(t), float(sigma_y)