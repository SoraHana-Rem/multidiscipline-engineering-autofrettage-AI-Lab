"""
Input validation utilities for pressure vessel analysis.
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


def validate_inputs(P, r_i, t, sigma_y):
    """Validates pressure vessel inputs, ensuring non-boolean positive floats in exact specification order."""
    params = [
        ("Pressure", P, PRESSURE_MIN, PRESSURE_MAX, "P", "Pressure must be positive"),
        ("Inner radius", r_i, RADIUS_MIN, RADIUS_MAX, "r_i", "Inner radius must be positive"),
        ("Wall thickness", t, THICKNESS_MIN, THICKNESS_MAX, "t", "Wall thickness must be positive"),
        ("Yield strength", sigma_y, YIELD_MIN, YIELD_MAX, "sigma_y", "Yield strength must be positive"),
    ]

    # 1. Type validation (REQ-TYP-001..004)
    # Check booleans first across all params
    for name, val, _, _, code, _ in params:
        if isinstance(val, bool):
            raise TypeError(f"Invalid type for {code}: must be a numeric float or int: got bool")

    # Check non-numeric types
    for name, val, _, _, code, _ in params:
        if not isinstance(val, (int, float)):
            raise TypeError("must be a numeric float or int")

    # 2. Finiteness validation (REQ-VAL-001)
    for name, val, _, _, code, _ in params:
        if not math.isfinite(val):
            raise ValueError("must be finite")

    # 3. Positivity check (REQ-VAL-002..005)
    for name, val, _, _, code, pos_msg in params:
        if val <= 0:
            raise ValueError(pos_msg)

    # 4. Range Limits Check (REQ-VAL-006, REQ-INP)
    for name, val, min_val, max_val, code, _ in params:
        if val < min_val or val > max_val:
            if name == "Pressure":
                raise ValueError("Pressure out of range")
            if code == "sigma_y":
                raise ValidationError("sigma_y value out of allowable range or unit slip detected")
            raise ValidationError(f"Parameter '{code}'={val} is out of valid range [{min_val}, {max_val}].")

    return float(P), float(r_i), float(t), float(sigma_y)