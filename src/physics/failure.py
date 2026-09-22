"""Failure criteria and safety factor evaluation."""
import math

def calculate_safety_factor(equivalent_stress: float, yield_strength: float) -> float:
    if equivalent_stress == 0.0:
        raise ZeroDivisionError("Equivalent stress cannot be zero when calculating safety factor.")
    return yield_strength / equivalent_stress

def safety_factor(sigma_y: float, sigma_vm: float) -> float:
    return calculate_safety_factor(equivalent_stress=sigma_vm, yield_strength=sigma_y)

def von_mises_plane(sigma_1: float, sigma_2: float) -> float:
    """Plane stress von Mises equivalent stress."""
    return math.sqrt(sigma_1**2 - sigma_1 * sigma_2 + sigma_2**2)

def von_mises_triaxial(sigma_1: float, sigma_2: float, sigma_3: float) -> float:
    """Triaxial von Mises equivalent stress."""
    return math.sqrt(0.5 * ((sigma_1 - sigma_2)**2 + (sigma_2 - sigma_3)**2 + (sigma_3 - sigma_1)**2))