"""
Central configuration limits for pressure vessel parameters (REQ-INP series).
Single source of truth for numeric ranges and model selection thresholds.
"""

# Input Range Limits (Inclusive)
PRESSURE_MIN = 0.0      # Exclusive lower bound (P > 0)
PRESSURE_MAX = 100.0    # MPa

RADIUS_MIN = 1.0        # mm
RADIUS_MAX = 5000.0     # mm

THICKNESS_MIN = 0.05    # mm
THICKNESS_MAX = 500.0   # mm

YIELD_MIN = 10.0        # MPa
YIELD_MAX = 3000.0      # MPa

# Model Selection Threshold (r_i / t)
THIN_WALL_RATIO_THRESHOLD = 10.0