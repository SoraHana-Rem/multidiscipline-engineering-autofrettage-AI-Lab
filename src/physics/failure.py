"""Failure criteria and yield safety-factor calculations."""

import math


def safety_factor(
    sigma_y: float,
    sigma_vm: float,
    eps: float = 1e-12,
) -> float:
    """
    REQ-FUN-004, REQ-FUN-005: Calculate yield strength / equivalent stress.

    Supported calls:
        safety_factor(500.0, 200.0)
        safety_factor(sigma_y=500.0, sigma_vm=200.0)

    Equivalent stress must not be negative, zero or near zero.
    """
    if isinstance(sigma_y, bool) or isinstance(sigma_vm, bool):
        raise TypeError(
            "Inputs must be numeric floats or ints, not booleans."
        )

    sy_val = float(sigma_y)
    seq_val = float(sigma_vm)

    if seq_val < 0:
        raise ValueError("Equivalent stress cannot be negative.")

    if abs(seq_val) < eps:
        raise ZeroDivisionError(
            "Equivalent stress cannot be zero or near zero."
        )

    return float(sy_val / seq_val)


def von_mises_plane(sigma_1: float, sigma_2: float) -> float:
    """REQ-FUN-004: Calculate plane-stress von Mises equivalent stress."""
    if isinstance(sigma_1, bool) or isinstance(sigma_2, bool):
        raise TypeError(
            "Inputs must be numeric floats or ints, not booleans."
        )

    return math.sqrt(
        sigma_1**2 - sigma_1 * sigma_2 + sigma_2**2
    )


def von_mises_triaxial(
    sigma_1: float,
    sigma_2: float,
    sigma_3: float,
) -> float:
    """REQ-FUN-004: Calculate triaxial von Mises equivalent stress."""
    if any(isinstance(value, bool) for value in (
        sigma_1, sigma_2, sigma_3
    )):
        raise TypeError(
            "Inputs must be numeric floats or ints, not booleans."
        )

    return math.sqrt(
        0.5 * (
            (sigma_1 - sigma_2) ** 2
            + (sigma_2 - sigma_3) ** 2
            + (sigma_3 - sigma_1) ** 2
        )
    )