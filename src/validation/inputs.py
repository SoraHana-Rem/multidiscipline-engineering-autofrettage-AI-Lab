import math
from src.errors import ValidationError

def validate_inputs(P, r_i, t, sigma_y):
    """
    Validates pressure vessel input parameters according to REQ-TYP and REQ-VAL specs.
    """
    params = [("Pressure", P), ("Inner radius", r_i), ("Wall thickness", t), ("Yield strength", sigma_y)]
    
    # 1. Type validation (REQ-TYP-001..004)
    for name, val in params:
        if isinstance(val, bool):
            raise TypeError("must be a numeric float or int: got bool")
        if not isinstance(val, (int, float)):
            raise TypeError("must be a numeric float or int")
            
    # 2. Finiteness validation (REQ-VAL-001)
    for name, val in params:
        if not math.isfinite(val):
            raise ValueError(f"{name} must be finite")
            
    # 3. Positive value checks (REQ-VAL-002..005)
    for name, val in params:
        if val <= 0:
            raise ValueError(f"{name} must be positive")
            
    # 4. Maximum parameter limits (REQ-VAL-006)
    if P > 100.0:
        raise ValueError("Pressure out of range")
        
    return float(P), float(r_i), float(t), float(sigma_y)

