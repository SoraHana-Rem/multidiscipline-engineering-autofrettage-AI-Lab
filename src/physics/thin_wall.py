"""
Thin-wall pressure vessel calculations (r/t >= 10).
Hoop stress: sigma_h = (P * r) / t
Longitudinal stress: sigma_l = (P * r) / (2 * t)
"""

def calculate_thin_wall_stress(pressure: float, radius: float, thickness: float) -> float:
    """Calculates hoop stress for thin-walled pressure vessels."""
    return (pressure * radius) / thickness