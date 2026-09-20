"""
Configuration module defining physical and operational boundary limits.

Centralizes all range validation parameters and model selection thresholds
to prevent hardcoding values in business logic.
"""

# Input parameter numeric range limits (inclusive)
PRESSURE_MIN: float = 0.0  # Exclusive lower bound (P > 0)
PRESSURE_MAX: float = 100.0  # MPa

RADIUS_MIN: float = 1.0  # mm
RADIUS_MAX: float = 5000.0  # mm

THICKNESS_MIN: float = 0.05  # mm
THICKNESS_MAX: float = 500.0  # mm

YIELD_STRESS_MIN: float = 10.0  # MPa
YIELD_STRESS_MAX: float = 3000.0  # MPa

# Model selection threshold ratio (r_i / t)
THIN_WALL_RATIO_THRESHOLD: float = 10.0