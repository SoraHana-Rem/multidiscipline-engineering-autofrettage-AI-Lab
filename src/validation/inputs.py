"""
Input validation for pressure-vessel analysis.

Validation stages:
    Type -> Finiteness -> Positivity -> Range

Within each stage:
    P -> r_i -> t -> sigma_y
"""

import math
from numbers import Real

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
    """
    REQ-TYP-001..004, REQ-VAL-001..006, REQ-ERR-001..004:
    Validate all inputs and return a tuple of Python floats.
    """
    params = [
        ("Pressure", "P", P, "MPa", PRESSURE_MIN, PRESSURE_MAX),
        ("Inner radius", "r_i", r_i, "mm", RADIUS_MIN, RADIUS_MAX),
        ("Wall thickness", "t", t, "mm", THICKNESS_MIN, THICKNESS_MAX),
        ("Yield strength", "sigma_y", sigma_y, "MPa", YIELD_MIN, YIELD_MAX),
    ]

    # Check all types before performing any value validation.
    for name, code, value, unit, _, _ in params:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(
                f"{name} ({code}) must be a real numeric scalar: "
                f"got {value!r} {unit}; type={type(value).__name__}"
            )

    # Convert supported real scalars to Python floats and check finiteness.
    converted = []

    for name, code, value, unit, minimum, maximum in params:
        try:
            number = float(value)
        except (OverflowError, ValueError) as exc:
            raise ValueError(
                f"{name} ({code}) must be finite and representable "
                f"as a Python float: got {value!r} {unit}"
            ) from exc

        if not math.isfinite(number):
            raise ValueError(
                f"{name} ({code}) must be finite: "
                f"got {value!r} {unit}"
            )

        converted.append(
            (name, code, value, number, unit, minimum, maximum)
        )

    # Check positivity before checking configured ranges.
    for name, code, original, number, unit, _, _ in converted:
        if number <= 0:
            raise ValueError(
                f"{name} must be positive ({code}): "
                f"got {original!r} {unit}"
            )

    # Positive inputs must also lie within the configured bounds.
    for name, code, original, number, unit, minimum, maximum in converted:
        if number < minimum or number > maximum:
            raise ValidationError(
                f"{name} out of range ({code}): "
                f"expected [{minimum}, {maximum}] {unit}; "
                f"got {original!r} {unit}"
            )

    return tuple(item[3] for item in converted)