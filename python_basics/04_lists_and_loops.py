# ==========================================
# LESSON 4: Lists, Iteration (for loops) & Batch Processing
# ==========================================



#Defining a list of pressure variables (in bar)

pressure_telemetry_bar = [120, 180, 210, 250, 190] # bar
material_yield_strength = 220 # MPa

print(f" Raw pressure telemetry (bar): {pressure_telemetry_bar}")

#iterating with for loop
# Python takes each item in 'pressure_telemetry_bar' one by one
# and assigns it to the temporary variable 'p_bar'

print(" Batch analysis Results:")
for p_bar in pressure_telemetry_bar:
    p_mpa = p_bar * 0.1  # Convert bar to MPa


    # safety limits

    if p_mpa > material_yield_strength:
        status = "Yielded"
    else:
        status = "Safe"


    print(f" Pressure: {p_mpa:.1f} MPa, Status: {status}")

#accumlating results in a list
# We can create an empty list and append processed values to it

overperformance_results = []  # Empty list to store results
for p_bar in pressure_telemetry_bar:
    p_mpa = p_bar * 0.1  # Convert bar to MPa

    if p_mpa > 20.0:  # MPa
        overperformance_results.append((p_mpa, "Overperformance"))  # Append a tuple of (pressure, status)

print(f"Captured Overpressure Events (>20 MPa): {overperformance_results}")
