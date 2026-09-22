"""Thin-wall pressure vessel physics calculations."""

def calculate_thin_wall_stress(P: float, r_i: float, t: float) -> float:
    """Calculates thin-wall hoop stress: sigma_h = (P * r_i) / t."""
    return (P * r_i) / t

def hoop_stress(P: float, r_i: float, t: float) -> float:
    return calculate_thin_wall_stress(P, r_i, t)

def longitudinal_stress(P: float, r_i: float, t: float) -> float:
    """Calculates thin-wall longitudinal stress: sigma_l = (P * r_i) / (2 * t)."""
    return (P * r_i) / (2.0 * t)