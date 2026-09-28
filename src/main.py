"""
Main Entry Point / CLI Orchestrator for Pressure Vessel & Autofrettage Analysis.
"""

import sys
import json
import argparse
from typing import Any, Dict, Optional

from src.analysis import analyze_vessel
from src.physics.autofrettage import calculate_autofrettage


def parse_arguments() -> argparse.Namespace:
    """Configures command-line arguments for interactive or automated execution."""
    parser = argparse.ArgumentParser(
        description="Run multidisciplinary pressure vessel stress, autofrettage, and failure analysis."
    )
    parser.add_argument(
        "--pressure",
        "-P",
        type=float,
        required=True,
        help="Operating internal pressure P (MPa)",
    )
    parser.add_argument(
        "--radius", "-r", type=float, required=True, help="Inner radius r_i (mm)"
    )
    parser.add_argument(
        "--thickness", "-t", type=float, required=True, help="Wall thickness t (mm)"
    )
    parser.add_argument(
        "--yield-strength",
        "-sy",
        type=float,
        required=True,
        help="Material yield strength sigma_y (MPa)",
    )
    parser.add_argument(
        "--autofrettage-pressure",
        "-Pauto",
        type=float,
        default=None,
        help="Optional autofrettage processing pressure (MPa)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results as raw JSON"
    )

    return parser.parse_args()


def run_pipeline(
    P: float,
    r_i: float,
    t: float,
    sigma_y: float,
    P_auto: Optional[float] = None,
    json_output: bool = False,
) -> None:
    """Orchestrates validation, elastic/plastic physics calculations, and result formatting."""
    try:
        # Standard elastic analysis
        result = analyze_vessel(P=P, r_i=r_i, t=t, sigma_y=sigma_y)
        r_o = r_i + t

        output_data: Dict[str, Any] = {
            "model_used": result.model,
            "stresses_MPa": {
                "hoop": round(result.sigma_hoop, 3),
                "longitudinal": round(result.sigma_long, 3),
                "radial": round(result.sigma_radial, 3),
                "von_mises": round(result.sigma_vm, 3),
            },
            "safety_factor": round(result.safety_factor, 3),
            "yielded": result.yielded,
        }

        # Optional autofrettage analysis
        if P_auto is not None:
            auto_res = calculate_autofrettage(
                P_auto=P_auto, r_i=r_i, r_o=r_o, sigma_y=sigma_y, P_working=P
            )
            output_data["autofrettage"] = {
                "P_auto_MPa": P_auto,
                "plastic_radius_mm": round(auto_res.r_p, 3),
                "residual_hoop_inner_MPa": round(auto_res.residual_hoop_inner, 3),
                "autofrettage_safety_factor": round(auto_res.safety_factor, 3),
            }

        if json_output:
            print(json.dumps(output_data, indent=2))
        else:
            print_summary(output_data)

    except (ValueError, TypeError, ArithmeticError) as e:
        # Covers ValidationError (a ValueError), bad types, and non-finite/zero-division results.
        print(f"\n[EXECUTION ERROR]: {e}", file=sys.stderr)
        sys.exit(1)


def print_summary(output_data: Dict[str, Any]) -> None:
    """Prints a human-readable summary of the analysis results."""
    stresses = output_data["stresses_MPa"]

    print("\n==================================================")
    print("      PRESSURE VESSEL ANALYSIS SUMMARY")
    print("==================================================")
    print(f"  Model Selected     : {output_data['model_used']}")
    print(f"  Hoop Stress        : {stresses['hoop']} MPa")
    print(f"  Longitudinal       : {stresses['longitudinal']} MPa")
    print(f"  Radial Stress      : {stresses['radial']} MPa")
    print(f"  Von Mises Stress   : {stresses['von_mises']} MPa")
    print(f"  Safety Factor      : {output_data['safety_factor']}")
    print(
        f"  Yield Status       : {'YIELDED' if output_data['yielded'] else 'SAFE (Elastic)'}"
    )

    if "autofrettage" in output_data:
        auto = output_data["autofrettage"]
        print("--------------------------------------------------")
        print("      AUTOFRETTAGE CAPSTONE SUMMARY")
        print("--------------------------------------------------")
        print(f"  Autofrettage Press : {auto['P_auto_MPa']} MPa")
        print(f"  Plastic Radius r_p : {auto['plastic_radius_mm']} mm")
        print(f"  Residual Hoop Bore : {auto['residual_hoop_inner_MPa']} MPa")
        print(f"  Enhanced SF        : {auto['autofrettage_safety_factor']}")

    print("==================================================\n")


if __name__ == "__main__":
    args = parse_arguments()
    run_pipeline(
        P=args.pressure,
        r_i=args.radius,
        t=args.thickness,
        sigma_y=args.yield_strength,
        P_auto=args.autofrettage_pressure,
        json_output=args.json,
    )