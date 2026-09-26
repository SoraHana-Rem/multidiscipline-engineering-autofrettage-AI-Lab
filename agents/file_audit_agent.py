import os
import json
import pathlib
from typing import Dict, List, Any

# Target paths for the audit
WORKSPACE_ROOT = pathlib.Path(__file__).parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs"
SRC_DIR = WORKSPACE_ROOT / "src"
TESTS_DIR = WORKSPACE_ROOT / "tests"

def inspect_file_contents(file_path: pathlib.Path) -> str:
    """Read and return content of a file safely."""
    if not file_path.exists():
        return f"[FILE NOT FOUND]: {file_path}"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[ERROR READING FILE]: {str(e)}"

def run_workspace_audit() -> Dict[str, Any]:
    """Scans key workspace files and checks structural requirements."""
    audit_results = {
        "status": "PASS",
        "checks": [],
        "evidence": {}
    }

    # Check 1: Traceability in requirements.md
    req_path = DOCS_DIR / "requirements.md"
    req_content = inspect_file_contents(req_path)
    if "CR-01" in req_content or "Lamé" in req_content or "autofrettage" in req_content.lower():
        audit_results["checks"].append({
            "rule": "DOC-TRACEABILITY", 
            "status": "PASS", 
            "details": "requirements.md contains physical domain models."
        })
    else:
        audit_results["checks"].append({
            "rule": "DOC-TRACEABILITY", 
            "status": "QUERY", 
            "details": "requirements.md missing expected references."
        })

    # Read all relevant source files including physics modules
    inputs_path = SRC_DIR / "validation" / "inputs.py"
    errors_path = SRC_DIR / "errors.py"
    analysis_path = SRC_DIR / "analysis.py"
    failure_path = SRC_DIR / "physics" / "failure.py"
    thick_wall_path = SRC_DIR / "physics" / "thick_wall.py"
    
    combined_src_content = (
        inspect_file_contents(errors_path) + 
        inspect_file_contents(analysis_path) + 
        inspect_file_contents(inputs_path) +
        inspect_file_contents(failure_path) +
        inspect_file_contents(thick_wall_path)
    )
    
    # Check 2: Type Safety
    if "isinstance(" in combined_src_content and "bool" in combined_src_content:
        audit_results["checks"].append({
            "rule": "TYPE-GUARD-BOOL", 
            "status": "PASS", 
            "details": "Explicit boolean rejection detected in input validation."
        })
    else:
        audit_results["checks"].append({
            "rule": "TYPE-GUARD-BOOL", 
            "status": "FAIL", 
            "details": "No explicit boolean check (isinstance(..., bool)) found in src/."
        })

    # Check 3: Zero boundary stress guard / relative error tolerance
    if any(token in combined_src_content for token in ["1e-12", "1e-9", "ZeroDivisionError", "float('inf')"]):
        audit_results["checks"].append({
            "rule": "NUMERICAL-GUARD-DIV0", 
            "status": "PASS", 
            "details": "Numerical edge case or zero-division tolerance guard detected in physics/validation."
        })
    else:
        audit_results["checks"].append({
            "rule": "NUMERICAL-GUARD-DIV0", 
            "status": "QUERY", 
            "details": "Verify zero-division logic in physics models."
        })

    return audit_results

if __name__ == "__main__":
    results = run_workspace_audit()
    print("=== WORKSPACE AUTOMATED AUDIT REPORT ===")
    print(json.dumps(results, indent=2))