"""
Failure criteria and safety factor evaluation modules.
"""
import math
from typing import Union, Optional

Numeric = Union[int, float]


def safety_factor(
    sigma_y: Optional[Numeric] = None, 
    sigma_vm: Optional[Numeric] = None, 
    yield_strength: Optional[Numeric] = None, 
    equivalent_stress: Optional[Numeric] = None, 
    eps: float = 1e-12
) -> float:
    """
    Calculates safety factor against yield strength with type guards,
    negative stress checks, and zero-division protection.

    Supports both positional arguments and keyword arguments:
    - (sigma_y, sigma_vm)
    - (yield_strength=..., equivalent_stress=...)
    """
    sy = yield_strength if yield_strength is not None else sigma_y
    seq = equivalent_stress if equivalent_stress is not None else sigma_vm

    if sy is None or seq is None:
        raise ValueError("Safety factor requires both yield strength and equivalent stress inputs.")

    # Guard against boolean inputs (since bool inherits from int in Python)
    if isinstance(sy, bool) or isinstance(seq, bool):
        raise TypeError("Inputs must be numeric floats or ints, not booleans.")

    # Convert to float for numeric evaluation
    sy_val = float(sy)
    seq_val = float(seq)

    if seq_val < 0:
        raise ValueError("Equivalent stress cannot be negative.")

    # Guard against division by zero or near-zero stress
    if abs(seq_val) < eps:
        raise ZeroDivisionError("Equivalent stress cannot be zero or near zero.")

    return float(sy_val / seq_val)


def von_mises_plane(sigma_1: float, sigma_2: float) -> float:
    """Plane stress von Mises equivalent stress."""
    if isinstance(sigma_1, bool) or isinstance(sigma_2, bool):
        raise TypeError("Inputs must be numeric floats or ints, not booleans.")
    return math.sqrt(sigma_1**2 - sigma_1 * sigma_2 + sigma_2**2)


def von_mises_triaxial(sigma_1: float, sigma_2: float, sigma_3: float) -> float:
    """Triaxial von Mises equivalent stress."""
    if isinstance(sigma_1, bool) or isinstance(sigma_2, bool) or isinstance(sigma_3, bool):
        raise TypeError("Inputs must be numeric floats or ints, not booleans.")
    return math.sqrt(0.5 * ((sigma_1 - sigma_2)**2 + (sigma_2 - sigma_3)**2 + (sigma_3 - sigma_1)**2))


# Backward compatibility alias
calculate_safety_factor = safety_factor