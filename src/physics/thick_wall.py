"""
Thick-wall pressure vessel Lamé equations (r/t < 10).
Hoop stress at inner boundary: sigma_h = P * (r_o^2 + r_i^2) / (r_o^2 - r_i^2)
"""

def calculate_thick_wall_stress(pressure: float, inner_radius: float, thickness: float) -> float:
    """Calculates maximum internal hoop stress using Lamé equations."""
    r_i = inner_radius
    r_o = inner_radius + thickness
    return pressure * (r_o**2 + r_i**2) / (r_o**2 - r_i**2)