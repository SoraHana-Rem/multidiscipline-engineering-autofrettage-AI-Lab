import numpy as np

def calculate_lame_stresses(r_i: float, r_o: float, P_i: float, P_o: float = 0.0, num_points: int = 100):
    """
    Calculates radial (sigma_r) and tangential (sigma_t) stress distributions 
    across the wall thickness using Lamé equations.
    """
    if r_i <= 0 or r_o <= 0:
        raise ValueError("Radii must be strictly positive.")
    if r_i >= r_o:
        raise ValueError("Inner radius (r_i) must be smaller than outer radius (r_o).")
    if P_i < 0 or P_o < 0:
        raise ValueError("Pressures must be non-negative.")

    r = np.linspace(r_i, r_o, num_points)
    denom = r_o**2 - r_i**2
    
    # Lamé Equations
    sigma_r = ((P_i * r_i**2 - P_o * r_o**2) / denom) - (((P_i - P_o) * r_i**2 * r_o**2) / (r**2 * denom))
    sigma_t = ((P_i * r_i**2 - P_o * r_o**2) / denom) + (((P_i - P_o) * r_i**2 * r_o**2) / (r**2 * denom))
    
    return r, sigma_r, sigma_t