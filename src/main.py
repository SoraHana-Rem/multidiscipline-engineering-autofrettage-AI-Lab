"""
Main Entry Point / CLI Orchestrator for Pressure Vessel & Autofrettage Analysis.
"""
import sys
import json
import argparse
from typing import Dict, Any

from src.analysis import analyze_vessel

# Robust import handling for autofrettage solver function name variations
try:
    import src.physics.autofrettage as auto_module
    
    if hasattr(auto_module, "calculate_autofrettage"):
        calculate_autofrettage = auto_module.calculate_autofrettage
    elif hasattr(auto_module, "solve_autofrettage"):
        calculate_autofrettage = auto_module.solve_autofrettage
    elif hasattr(auto_module, "autofrettage_analysis"):
        calculate_autofrettage = auto_module.autofrettage_analysis
    else:
        raise AttributeError("No recognized autofrettage solver function found in src.physics.autofrettage")
        
    HAS_AUTOFRETTAGE = True
except (ImportError, AttributeError):
    HAS_AUTOFRETTAGE = False


def parse_arguments() -> argparse.Namespace:
    """Configures command-line arguments for interactive or automated execution."""
    parser = argparse.ArgumentParser(
        description="Run multidisciplinary pressure vessel stress, autofrettage, and failure analysis."
    )
    parser.add_argument("--pressure", "-P", type=float, required=True, help="Operating internal pressure P (MPa)")
    parser.add_argument("--radius", "-r", type=float, required=True, help="Inner radius r_i (mm)")
    parser.add_argument("--thickness", "-t", type=float, required=True, help="Wall thickness t (mm)")
    parser.add_argument("--yield-strength", "-sy", type=float, required=True, help="Material yield strength sigma_y (MPa)")
    parser.add_argument("--autofrettage-pressure", "-Pauto", type=float, default=None, help="Optional autofrettage processing pressure (MPa)")
    parser.add_argument("--json", action="store_true", help="Output results as raw JSON")

    return parser.parse_args()


def run_pipeline(P: float, r_i: float, t: float, sigma_y: float, P_auto: float = None, json_output: bool = False):
    """Orchestrates validation, elastic/plastic physics calculations, and result formatting."""
    try:
        # Standard Elastic Analysis
        result = analyze_vessel(P=P, r_i=r_i, t=t, sigma_y=sigma_y)
        r_o = r_i + t

        output_data: Dict[str, Any] = {
            "model_used": result.model,
            "stresses_MPa": {
                "hoop": round(result.sigma_hoop, 3),
                "longitudinal": round(result.sigma_long, 3),
                "radial": round(result.sigma_radial, 3),
                "von_mises": round(result.sigma_vm, 3)
            },
            "safety_factor": round(result.safety_factor, 3),
            "yielded": result.yielded
        }

        # Optional Autofrettage Execution
        if P_auto is not None:
            if not HAS_AUTOFRETTAGE:
                raise ImportError("Autofrettage module is requested but missing or incorrectly imported from src.physics.autofrettage")

            auto_res = calculate_autofrettage(P_auto=P_auto, r_i=r_i, r_o=r_o, sigma_y=sigma_y, P_working=P)
            output_data["autofrettage"] = {
                "P_auto_MPa": P_auto,
                "plastic_radius_mm": round(getattr(auto_res, "r_p", getattr(auto_res, "plastic_radius", 0.0)), 3),
                "residual_hoop_inner_MPa": round(getattr(auto_res, "residual_hoop_inner", 0.0), 3),
                "autofrettage_safety_factor": round(getattr(auto_res, "safety_factor", result.safety_factor), 3)
            }

        if json_output:
            print(json.dumps(output_data, indent=2))
        else:
            print("\n==================================================")
            print("      PRESSURE VESSEL ANALYSIS SUMMARY")
            print("==================================================")
            print(f"  Model Selected     : {output_data['model_used']}")
            print(f"  Hoop Stress        : {output_data['stresses_MPa']['hoop']} MPa")
            print(f"  Longitudinal       : {output_data['stresses_MPa']['longitudinal']} MPa")
            print(f"  Radial Stress      : {output_data['stresses_MPa']['radial']} MPa")
            print(f"  Von Mises Stress   : {output_data['stresses_MPa']['von_mises']} MPa")
            print(f"  Safety Factor      : {output_data['safety_factor']}")
            print(f"  Yield Status       : {'YIELDED' if output_data['yielded'] else 'SAFE (Elastic)'}")
            
            if "autofrettage" in output_data:
                print("--------------------------------------------------")
                print("      AUTOFRETTAGE CAPSTONE SUMMARY")
                print("--------------------------------------------------")
                print(f"  Autofrettage Press : {output_data['autofrettage']['P_auto_MPa']} MPa")
                print(f"  Plastic Radius r_p : {output_data['autofrettage']['plastic_radius_mm']} mm")
                print(f"  Residual Hoop Bore : {output_data['autofrettage']['residual_hoop_inner_MPa']} MPa")
                print(f"  Bore SF estimate   : {output_data['autofrettage']['autofrettage_safety_factor']}")
                print("  Model limitation   : Residual axial stress omitted; wall minimum not assessed.")
            
            print("==================================================\n")

    except Exception as e:
        print(f"\n[EXECUTION ERROR]: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    args = parse_arguments()
    run_pipeline(
        P=args.pressure, 
        r_i=args.radius, 
        t=args.thickness, 
        sigma_y=args.yield_strength, 
        P_auto=args.autofrettage_pressure,
        json_output=args.json
    )