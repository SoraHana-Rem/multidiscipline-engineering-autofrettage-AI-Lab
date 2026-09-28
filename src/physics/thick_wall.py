"""Thick-wall Lamé pressure vessel physics calculations."""


def calculate_thick_wall_stress(P: float, r_i: float, t: float) -> float:
    """Calculates inner hoop stress for thick-wall vessels using Lamé equations."""
    r_o = r_i + t
    return P * (r_o**2 + r_i**2) / (r_o**2 - r_i**2)


def lame_stresses_inner(P: float, r_i: float, t: float) -> tuple[float, float, float]:
    """
    Returns (sigma_hoop, sigma_longitudinal, sigma_radial) at inner boundary.
    """
    r_o = r_i + t
    s_hoop = calculate_thick_wall_stress(P, r_i, t)
    s_long = (P * r_i**2) / (r_o**2 - r_i**2)
    s_radial = -P
    return s_hoop, s_long, s_radial
