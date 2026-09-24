#parameter setup 

yield_strength_Mpa =    250  # Yield strength in MPa
hoop_stress_Mpa =  280

#safety factor calculation

safety_factor = yield_strength_Mpa / hoop_stress_Mpa
print(f"Calcualted stress : {hoop_stress_Mpa} MPa")
print(f"Safety factor: {safety_factor:.2f}")


#condtional descion tree

if hoop_stress_Mpa > yield_strength_Mpa:
    print("The vessel has yielded. Safety factor is less than 1.")
elif safety_factor < 1.5:
    print("The vessel is safe but has a low safety factor.")
else 
    print("The vessel is safe with an acceptable safety factor.")

#combing conditions with logical operators

is_pressurized = True
max_temp_celsius = 350

if is_pressurized and max_temp_celsius > 300:
    print("The vessel is pressurized and operating at high temperature. Check safety factor.")