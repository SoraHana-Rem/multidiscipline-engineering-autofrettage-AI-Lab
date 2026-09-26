"""Failure criteria and safety factor evaluation."""
import math

"""
Failure criteria and safety factor evaluation modules.
"""

def safety_factor(sigma_y: float, sigma_vm: float, eps: float = 1e-12) -> float:
    """
    Calculates safety factor against yield strength with a zero-division guard.
    """
    # Guard against division by zero if von Mises stress is zero or near zero
    if abs(sigma_vm) < eps:
        return float('inf')  # Infinite safety factor when there is no stress
    
    return float(sigma_y / sigma_vm)
def safety_factor(sigma_y: float, sigma_vm: float) -> float:
    return calculate_safety_factor(equivalent_stress=sigma_vm, yield_strength=sigma_y)

def von_mises_plane(sigma_1: float, sigma_2: float) -> float:
    """Plane stress von Mises equivalent stress."""
    return math.sqrt(sigma_1**2 - sigma_1 * sigma_2 + sigma_2**2)

def von_mises_triaxial(sigma_1: float, sigma_2: float, sigma_3: float) -> float:
    """Triaxial von Mises equivalent stress."""
    return math.sqrt(0.5 * ((sigma_1 - sigma_2)**2 + (sigma_2 - sigma_3)**2 + (sigma_3 - sigma_1)**2))

