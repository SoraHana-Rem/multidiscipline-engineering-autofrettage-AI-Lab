"""
Failure criteria and safety factor calculations.
Von Mises / Tresca yield checks.
"""

def calculate_safety_factor(equivalent_stress: float, yield_strength: float) -> float:
    """Calculates yield safety factor (SF = yield_strength / equivalent_stress)."""
    if equivalent_stress <= 0:
        raise ZeroDivisionError("Equivalent stress must be greater than zero to calculate safety factor.")
    return yield_strength / equivalent_stress