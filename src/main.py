"""
Main Entry Point / CLI Orchestrator for Pressure Vessel & Autofrettage Analysis.
"""
import sys
import json
import argparse
from typing import Dict, Any

from src.analysis import analyze_vessel

def parse_arguments() -> argparse.Namespace:
    """Configures command-line arguments for interactive or automated execution."""
    parser = argparse.ArgumentParser(
        description="Run multidisciplinary pressure vessel stress and failure analysis."
    )
    parser.add_argument("--pressure", "-P", type=float, required=True, help="Internal pressure P (MPa)")
    parser.add_argument("--radius", "-r", type=float, required=True, help="Inner radius r_i (mm)")
    parser.add_argument("--thickness", "-t", type=float, required=True, help="Wall thickness t (mm)")
    parser.add_argument("--yield-strength", "-sy", type=float, required=True, help="Material yield strength sigma_y (MPa)")
    parser.add_argument("--json", action="store_true", help="Output results as raw JSON")

    return parser.parse_args()

def run_pipeline(P: float, r_i: float, t: float, sigma_y: float, json_output: bool = False):
    """Orchestrates validation, physics calculations, and result formatting."""
    try:
        result = analyze_vessel(P=P, r_i=r_i, t=t, sigma_y=sigma_y)
        
        output_data = {
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

        if json_output:
            print(json.dumps(output_data, indent=2))
        else:
            print("\n==================================================")
            print("      PRESSURE VESSEL ANALYSIS SUMMARY")
            print("==================================================")
            print(f"  Model Selected    : {output_data['model_used']}")
            print(f"  Hoop Stress       : {output_data['stresses_MPa']['hoop']} MPa")
            print(f"  Longitudinal      : {output_data['stresses_MPa']['longitudinal']} MPa")
            print(f"  Radial Stress     : {output_data['stresses_MPa']['radial']} MPa")
            print(f"  Von Mises Stress  : {output_data['stresses_MPa']['von_mises']} MPa")
            print(f"  Safety Factor     : {output_data['safety_factor']}")
            print(f"  Yield Status      : {'YIELDED' if output_data['yielded'] else 'SAFE (Elastic)'}")
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
        json_output=args.json
    )