"""
Failure criteria and safety factor evaluation modules.
"""
import math

def safety_factor(
    sigma_y: float = None, 
    sigma_vm: float = None, 
    yield_strength: float = None, 
    equivalent_stress: float = None, 
    eps: float = 1e-12
) -> float:
    """
    Calculates safety factor against yield strength with a zero-division guard.
    Supports both positional arguments and keyword arguments:
    - (sigma_y, sigma_vm)
    - (yield_strength=..., equivalent_stress=...)
    """
    sy = yield_strength if yield_strength is not None else sigma_y
    seq = equivalent_stress if equivalent_stress is not None else sigma_vm

    if sy is None or seq is None:
        raise ValueError("Safety factor requires both yield strength and equivalent stress inputs.")

    # Guard against division by zero if von Mises stress is zero or near zero
    if abs(seq) < eps:
        return float('inf')

    return float(sy / seq)


def von_mises_plane(sigma_1: float, sigma_2: float) -> float:
    """Plane stress von Mises equivalent stress."""
    return math.sqrt(sigma_1**2 - sigma_1 * sigma_2 + sigma_2**2)


def von_mises_triaxial(sigma_1: float, sigma_2: float, sigma_3: float) -> float:
    """Triaxial von Mises equivalent stress."""
    return math.sqrt(0.5 * ((sigma_1 - sigma_2)**2 + (sigma_2 - sigma_3)**2 + (sigma_3 - sigma_1)**2))


# Backward compatibility alias
calculate_safety_factor = safety_factor

