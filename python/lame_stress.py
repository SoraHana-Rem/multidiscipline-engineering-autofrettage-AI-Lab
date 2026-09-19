import numpy as np

def calculate_lame_stresses(
    r_i: float, 
    r_o: float, 
    P_i: float, 
    P_o: float = 0.0, 
    E: float = 200e9, 
    nu: float = 0.30, 
    num_points: int = 2001
):
    """
    Calculates stress distribution (radial, tangential, axial, von Mises)
    and radial displacement across cylinder wall thickness using Lamé equations.
    """
    if r_i <= 0 or r_o <= 0:
        raise ValueError("Radii must be strictly positive.")
    if r_i >= r_o:
        raise ValueError("Inner radius (r_i) must be smaller than outer radius (r_o).")
    if P_i < 0 or P_o < 0:
        raise ValueError("Pressures must be non-negative.")

    r = np.linspace(r_i, r_o, num_points)
    denom = r_o**2 - r_i**2
    
    A = (P_i * r_i**2 - P_o * r_o**2) / denom
    B = (P_i - P_o) * r_i**2 * r_o**2 / denom
    s_z = A  # Closed-end axial stress (Pa)

    s_r = A - B / (r**2)
    s_t = A + B / (r**2)
    u_r = (r / E) * (s_t - nu * (s_r + s_z))
    vm = np.sqrt(0.5 * ((s_t - s_r)**2 + (s_r - s_z)**2 + (s_z - s_t)**2))
    
    return {
        "r": r,
        "s_r": s_r,
        "s_t": s_t,
        "s_z": s_z,
        "u_r": u_r,
        "vm": vm,
        "A": A,
        "B": B
    }

if __name__ == "__main__":
    data = calculate_lame_stresses(r_i=0.050, r_o=0.100, P_i=100e6)
    
    print("--- Python Lamé Verification Baseline ---")
    print(f"Inner Wall (r_i = {data['r'][0]*1e3:.0f} mm):")
    print(f"  sigma_r:   {data['s_r'][0]/1e6:10.3f} MPa")
    print(f"  sigma_t:   {data['s_t'][0]/1e6:10.3f} MPa")
    print(f"  sigma_z:   {data['s_z']/1e6:10.3f} MPa")
    print(f"  u_r:       {data['u_r'][0]*1e6:10.3f} um")
    print(f"  von Mises: {data['vm'][0]/1e6:10.3f} MPa")

    print(f"\nOuter Wall (r_o = {data['r'][-1]*1e3:.0f} mm):")
    print(f"  sigma_r:   {data['s_r'][-1]/1e6:10.3f} MPa")
    print(f"  sigma_t:   {data['s_t'][-1]/1e6:10.3f} MPa")
    print(f"  sigma_z:   {data['s_z']/1e6:10.3f} MPa")
    print(f"  u_r:       {data['u_r'][-1]*1e6:10.3f} um")
    print(f"  von Mises: {data['vm'][-1]/1e6:10.3f} MPa")