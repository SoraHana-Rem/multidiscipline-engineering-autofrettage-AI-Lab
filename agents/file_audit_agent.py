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


class AuditResults:
    """Collect audit checks and derive a JSON-serializable overall result."""

    def __init__(self) -> None:
        self.status = "PASS"
        self.checks: List[Dict[str, str]] = []
        self.evidence: Dict[str, Any] = {}

    def add_check(self, rule: str, status: str, details: str) -> None:
        """Add a check and immediately refresh the aggregate status."""
        self.checks.append({"rule": rule, "status": status, "details": details})
        self.finalize()

    def finalize(self) -> str:
        """Set and return FAIL, QUERY, or PASS based on recorded checks."""
        statuses = {check["status"] for check in self.checks}
        self.status = (
            "FAIL" if "FAIL" in statuses
            else "QUERY" if "QUERY" in statuses
            else "PASS"
        )
        return self.status

    def to_dict(self) -> Dict[str, Any]:
        """Return the complete report in the format used by this agent."""
        self.finalize()
        return {
            "status": self.status,
            "checks": self.checks,
            "evidence": self.evidence,
        }


def run_workspace_audit() -> Dict[str, Any]:
    """Run heuristic text checks, not behavioural or compliance verification."""
    results = AuditResults()
    results.evidence["method"] = "heuristic_text_scan"
    results.evidence["limitations"] = (
        "Text matches may occur in comments or unrelated code. "
        "This scan does not execute tests or establish traceability, "
        "input rejection, numerical correctness or engineering compliance."
    )

    paths = [
        DOCS_DIR / "requirements.md",
        SRC_DIR / "errors.py",
        SRC_DIR / "analysis.py",
        SRC_DIR / "validation" / "inputs.py",
        SRC_DIR / "physics" / "failure.py",
        SRC_DIR / "physics" / "thick_wall.py",
    ]

    # Keep failed reads separate from searchable file content.
    contents = {}
    read_errors = {}

    for path in paths:
        relative_path = path.relative_to(WORKSPACE_ROOT).as_posix()
        try:
            contents[relative_path] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            read_errors[relative_path] = (
                f"{type(exc).__name__}: {exc}"
            )

    results.evidence["scanned_files"] = list(contents)
    results.evidence["read_errors"] = read_errors

    if read_errors:
        results.add_check(
            "FILE-READ",
            "FAIL",
            "Required files could not be read: "
            + ", ".join(read_errors),
        )
    else:
        results.add_check(
            "FILE-READ",
            "PASS",
            "All selected files were readable.",
        )

    req_content = contents.get("docs/requirements.md", "")
    if (
        "CR-01" in req_content
        or "Lamé" in req_content
        or "autofrettage" in req_content.lower()
    ):
        results.add_check(
            "DOC-TRACEABILITY",
            "PASS",
            "Expected domain-reference text found in requirements.md; "
            "traceability is not verified.",
        )
    else:
        results.add_check(
            "DOC-TRACEABILITY",
            "QUERY",
            "Expected domain-reference text not found in requirements.md; "
            "review required.",
        )

    combined_src_content = "\n".join(
        content
        for path, content in contents.items()
        if path.startswith("src/")
    )

    if (
        "isinstance(" in combined_src_content
        and "bool" in combined_src_content
    ):
        results.add_check(
            "TYPE-GUARD-BOOL",
            "PASS",
            "Both 'isinstance(' and 'bool' tokens found in source text; "
            "boolean rejection is not verified.",
        )
    else:
        results.add_check(
            "TYPE-GUARD-BOOL",
            "FAIL",
            "Expected boolean-check tokens not found in source text; "
            "this heuristic check failed.",
        )

    numerical_tokens = [
        "1e-12",
        "1e-9",
        "ZeroDivisionError",
        "float('inf')",
    ]
    matched_tokens = [
        token
        for token in numerical_tokens
        if token in combined_src_content
    ]
    results.evidence["numerical_tokens_found"] = matched_tokens

    if matched_tokens:
        results.add_check(
            "NUMERICAL-GUARD-DIV0",
            "PASS",
            "Numerical-marker text found in source; "
            "numerical handling is not verified.",
        )
    else:
        results.add_check(
            "NUMERICAL-GUARD-DIV0",
            "QUERY",
            "Expected numerical-marker text not found in source; "
            "review required.",
        )

    return results.to_dict()


if __name__ == "__main__":
    results = run_workspace_audit()
    print("=== WORKSPACE HEURISTIC TEXT SCAN ===")
    print(json.dumps(results, indent=2))