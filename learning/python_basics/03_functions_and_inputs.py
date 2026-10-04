#defining a function

def calculate_hoop_stress(internal_pressure_bar, inner_radius, wall_thickness):
    """Calculates the hoop stress in a thin-walled pressure vessel."""

    if wall_thickness <= 0:
        raise ValueError("Wall thickness must be greater than zero.")

    hoop_stress = (internal_pressure_bar * inner_radius) / wall_thickness  # MPa
    return hoop_stress


#calling a function

pressure = 20.0 #Mpa
radius = 50.0 #mm


#call 1 

thickness_1 = 5.0 #mm
hoop_stress_1 = calculate_hoop_stress(pressure, radius, thickness_1)
print(f"Test 1: Hoop stress for wall thickness {thickness_1} mm is {hoop_stress_1:.2f} MPa")

#call 2 

thickness_2 = 2.5 #mm
hoop_stress_2 = calculate_hoop_stress(pressure, radius, thickness_2)
print(f"Test 2: Hoop stress for wall thickness {thickness_2} mm is {hoop_stress_2:.2f} MPa")

thickness_3 = 0.0 #mm
stress_3 = calculate_hoop_stress(pressure, radius, thickness_3)
print(f"Test 3: Hoop stress for wall thickness {thickness_3} mm is {stress_3:.2f} MPa")

