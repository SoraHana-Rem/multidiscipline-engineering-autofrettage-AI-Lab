"""
Linear Elastic Fracture Mechanics (LEFM) and Paris Law Fatigue Module.
Models stress intensity factors, fatigue crack growth, and vessel life prediction.
"""
import math
from src.errors import ValidationError


def calculate_stress_intensity(sigma_hoop, a, Y=1.12):
    """
    Calculates Mode-I Stress Intensity Factor K_I (MPa*m^0.5).

    Parameters:
        sigma_hoop (float): Total effective hoop stress (MPa).
        a (float): Crack depth (mm).
        Y (float): Geometric correction factor (default 1.12 for inner bore crack).

    Returns:
        float: Stress intensity factor K_I (MPa*sqrt(m)).
    """
    if a <= 0:
        raise ValidationError(f"Crack depth 'a' must be positive. Got {a}.")
    
    # Convert crack depth 'a' from mm to meters for SI conversion
    a_m = a / 1000.0
    k_i = Y * sigma_hoop * math.sqrt(math.pi * a_m)
    return float(k_i)


def calculate_critical_crack_depth(sigma_max, K_ic, Y=1.12):
    """
    Calculates critical crack depth a_c (mm) where fast fracture occurs.
    """
    if sigma_max <= 0:
        raise ValidationError("Maximum hoop stress must be positive to evaluate fast fracture.")
    
    # K_ic = Y * sigma * sqrt(pi * a_c_m) -> solve for a_c_m
    a_c_m = (K_ic / (Y * sigma_max)) ** 2 / math.pi
    return float(a_c_m * 1000.0)  # Return in mm


def predict_fatigue_life(a_init, a_crit, delta_sigma, C, m, Y=1.12, num_steps=1000):
    """
    Integrates Paris Law (da/dN = C * (Delta K)^m) to predict cycle count to failure.

    Parameters:
        a_init (float): Initial crack depth (mm).
        a_crit (float): Critical crack depth at failure (mm).
        delta_sigma (float): Cyclic hoop stress range (MPa).
        C (float): Paris Law material constant.
        m (float): Paris Law exponent.
        Y (float): Geometry factor.
        num_steps (int): Numerical integration discretization steps.

    Returns:
        float: Total estimated fatigue life (cycles).
    """
    if a_init >= a_crit:
        raise ValidationError(f"Initial crack depth ({a_init:.2f} mm) already exceeds or equals critical depth ({a_crit:.2f} mm).")

    # Discretize crack growth path from a_init to a_crit (in meters)
    a_grid = [a_init + i * (a_crit - a_init) / num_steps for i in range(num_steps + 1)]
    total_cycles = 0.0

    for i in range(num_steps):
        a_mid = (a_grid[i] + a_grid[i + 1]) / 2.0  # Midpoint crack depth (mm)
        da_m = (a_grid[i + 1] - a_grid[i]) / 1000.0  # Delta a in meters
        
        # Calculate Delta K at midpoint
        delta_k = Y * delta_sigma * math.sqrt(math.pi * (a_mid / 1000.0))
        
        # Paris Law: dN = da / (C * (Delta K)^m)
        da_dn = C * (delta_k ** m)
        if da_dn <= 0:
            raise ValidationError("Non-positive crack growth rate encountered.")
            
        dn = da_m / da_dn
        total_cycles += dn

    return float(total_cycles)