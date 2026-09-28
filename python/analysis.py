import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Geometry and load parameters
# Units: radius in metres (m), pressure in MPa -> stresses come out in MPa
r_i = 0.100  # Inner radius (m)
r_o = 0.200  # Outer radius (m)
P_i = 100.0  # Internal pressure (MPa)
P_o = 0.0    # External pressure (MPa)

# 2. NumPy vectorization: radius array from inner to outer radius
r = np.linspace(r_i, r_o, 100)  # 100 points from inner to outer radius

# 3. Lamé's equations for thick-walled cylinder stresses
A = (P_i * r_i**2 - P_o * r_o**2) / (r_o**2 - r_i**2)
B = (P_i - P_o) * r_i**2 * r_o**2 / (r_o**2 - r_i**2)  # (P_i - P_o), matches MATLAB

sigma_theta = A + B / r**2  # Hoop stress
sigma_r = A - B / r**2      # Radial stress

# 4. Pandas data handling: export results to CSV
df = pd.DataFrame({
    "radius_mm": r * 1000,  # metres -> mm for the plot axis
    "hoop_stress_MPa": sigma_theta,
    "radial_stress_MPa": sigma_r,
})

# Ensure output directory exists
output_dir = Path("output")
plots_dir = output_dir / "plots"
output_dir.mkdir(exist_ok=True)
plots_dir.mkdir(exist_ok=True)

csv_path = output_dir / "lame_stress_profile.csv"
df.to_csv(csv_path, index=False)

# 5. Physics self-check (fails loudly if the equations are ever wrong)
assert np.isclose(sigma_r[0], -P_i), "Boundary condition failed: sigma_r(r_i) must equal -P_i"
assert np.isclose(sigma_r[-1], -P_o), "Boundary condition failed: sigma_r(r_o) must equal -P_o"
assert sigma_theta[0] > sigma_theta[-1], "Hoop stress must be highest at the bore"

# 6. Matplotlib visualization: plotting the stress distribution
plt.figure(figsize=(9, 5), dpi=300)

plt.plot(df["radius_mm"], df["hoop_stress_MPa"],
         label=r"Hoop Stress ($\sigma_\theta$)", color="#006E74", linewidth=2.5)   # Teal = Hoop
plt.plot(df["radius_mm"], df["radial_stress_MPa"],
         label=r"Radial Stress ($\sigma_r$)", color="#FC6A59", linewidth=2.5,
         linestyle="--")                                                           # Orange = Radial

plt.axhline(0, color="black", linewidth=0.8, linestyle=":")
plt.title("Thick-Walled Pressure Vessel: Lamé Stress Profile",
          fontsize=13, fontweight="bold", pad=12)
plt.xlabel("Radius $r$ (mm)", fontsize=11)
plt.ylabel("Stress (MPa)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(fontsize=11, frameon=True, facecolor="white", framealpha=0.9)
plt.tight_layout()

# Save image deliverable
plot_path = plots_dir / "lame_stress_profile.png"
plt.savefig(plot_path)
plt.close()

print(f"[SUCCESS] Stress profile plot saved to {plot_path}")
print(f"[SUCCESS] Stress data saved to {csv_path}")