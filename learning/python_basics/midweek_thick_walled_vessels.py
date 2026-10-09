import math

def calculate_hoop_stress(
        internal_pressure_pa: float, inner_radius: float, outer_radius: float, radius_point: float) -> float:
    """
    Calculates hoop (tangential) stress at a specific radius within a 
    thick-walled cylinder subjected to internal pressure using Lamé's equation.
    
    sigma_theta = (P_i * r_i^2 / (r_o^2 - r_i^2)) * (1 + (r_o^2 / r^2))
    """

    # guard clauses for invalid inputs
    if inner_radius <= 0 or outer_radius <= 0:
        raise ValueError("Inner and outer radii must be greater than zero.")
        
    if inner_radius >= outer_radius:
        raise ValueError("Inner radius must be less than outer radius.")

    if not (inner_radius <= radius_point <= outer_radius):
        raise ValueError("Radius point must be between inner and outer radii.")

    if internal_pressure_pa < 0:
        raise ValueError("Internal pressure must be non-negative.")

    # core Lamé's equation for hoop stress in a thick-walled cylinder
    r_i_sq = inner_radius ** 2
    r_o_sq = outer_radius ** 2
    r_a_sq = radius_point ** 2

    geometric_factor = (r_i_sq * internal_pressure_pa) / (r_o_sq - r_i_sq)
    hoop_stress = geometric_factor * (1 + (r_o_sq / r_a_sq))

    return hoop_stress


def safe_autofrettage_parse(raw_pressuree_str: str) -> float| None:
    """
    Safely parses a string input for autofrettage pressure, ensuring it is a valid float.
    Raises ValueError if the input is invalid.
    """
    try:
        pressure = float(raw_pressuree_str)
        if pressure < 0:
            raise ValueError("Autofrettage pressure must be non-negative.")
            return None
        return pressure
    except ValueError as err:
        raise ValueError(f"Invalid autofrettage pressure input: {raw_pressuree_str}") from err
        return None



    if __name__ == "__main__":
        r_inner = 50  # mm
        r_outer = 10   # mm
        p_internal = 100  # Mpa

        print ("--- Valid hoop stress calculation ---")

        bore_stress = calculate_hoop_stress(p_internal, r_inner, r_outer, r_inner)
        print(f"Hoop stress at inner radius ({r_inner} mm): {bore_stress:.2f} MPa")

        print ("/n--- 2.Guard clause tests ---")
        try:
            calculate_lame_hoop_stress(p_internal, r_inner, r_outer, 0.15) 
        except ValueError as e:
            print(f"Guard clause triggered: {e}")

        print("n/---- 3. safe telemetry parse tests ---")
        print ("valid input test", safe_autofrettage_parse("15000000.0")) 
        print ("invalid input test", safe_autofrettage_parse("15000000.0_corrupt"))