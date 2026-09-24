#variable assignment 

material_name = "Inconel 718"
inner_radius = 50   #mm
wall_thickness = 5.5  #mm
internal_pressure_bar = 200 #bar
is_active_model = True #bool


#basic math and unit conversion

internal_pressure_MPa = internal_pressure_bar * 0.1  # Convert bar to MPa

#calculate outer radius
outer_radius = inner_radius + wall_thickness  #mm


#type checking and printing variable types

print ("data types ")
print ("material_name: ", type(material_name))
print ("inner_radius: ", type(inner_radius))
print ("wall_thickness: ", type(wall_thickness))
print ("internal_pressure_bar: ", type(internal_pressure_bar))
print ("is_active_model: ", type(is_active_model))
print ("internal_pressure_MPa: ", type(internal_pressure_MPa))
print (type(outer_radius))

print ("/n--------------------------------------------------")


#output formatting and printing variable values

print(f"Material: {material_name}   ")
print(f"Inner Radius: {inner_radius} mm")
print(f"Wall Thickness: {wall_thickness} mm")
print(f"Outer Radius: {outer_radius} mm")
print(f"operating pressure:  {internal_pressure_bar} bar  ({internal_pressure_MPa} MPa)") 

print(f"Thickness ratio (outer/inner): ({outer_radius / inner_radius:.4f})")      