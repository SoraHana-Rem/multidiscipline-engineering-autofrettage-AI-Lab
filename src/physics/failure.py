"""
Failure criteria and safety factor evaluation modules.
"""

import math

from src.config.limits import STRESS_ZERO_TOLERANCE


def safety_factor(sigma_y: float, sigma_vm: float) -> float:
    """
    Safety factor against yield: sigma_y / sigma_vm (REQ-FUN-004, REQ-PRC-002).

    Raises
    ------
    TypeError
        If either input is a bool.
    ValueError
        If the equivalent stress is negative.
    ZeroDivisionError
        If the equivalent stress is zero or effectively zero.
    """
    # bool inherits from int in Python, so True/False must be rejected explicitly
    if isinstance(sigma_y, bool) or isinstance(sigma_vm, bool):
        raise TypeError("Inputs must be numeric floats or ints, not booleans.")

    if sigma_vm < 0:
        raise ValueError("Equivalent stress cannot be negative.")

    if sigma_vm < STRESS_ZERO_TOLERANCE:
        raise ZeroDivisionError("Equivalent stress cannot be zero or near zero.")

    return float(sigma_y) / float(sigma_vm)


def von_mises_plane(sigma_1: float, sigma_2: float) -> float:
    """Plane stress von Mises equivalent stress."""
    if isinstance(sigma_1, bool) or isinstance(sigma_2, bool):
        raise TypeError("Inputs must be numeric floats or ints, not booleans.")
    return math.sqrt(sigma_1**2 - sigma_1 * sigma_2 + sigma_2**2)


def von_mises_triaxial(sigma_1: float, sigma_2: float, sigma_3: float) -> float:
    """Triaxial von Mises equivalent stress."""
    if isinstance(sigma_1, bool) or isinstance(sigma_2, bool) or isinstance(sigma_3, bool):
        raise TypeError("Inputs must be numeric floats or ints, not booleans.")
    return math.sqrt(
        0.5
        * (
            (sigma_1 - sigma_2) ** 2
            + (sigma_2 - sigma_3) ** 2
            + (sigma_3 - sigma_1) ** 2
        )
    )