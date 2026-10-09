"""Generate a Markdown report of the workspace heuristic text scan."""

import pathlib
from datetime import datetime, timezone

if __package__:
    from .file_audit_agent import run_workspace_audit, WORKSPACE_ROOT
else:
    from file_audit_agent import run_workspace_audit, WORKSPACE_ROOT


def _table_text(value):
    """Escape text for a Markdown table cell."""
    return (
        str(value)
        .replace("|", r"\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def generate_markdown_report() -> pathlib.Path:
    """Run the text scan and write its scoped results to docs/."""
    audit_data = run_workspace_audit()
    docs_dir = WORKSPACE_ROOT / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_path = docs_dir / "week-14-audit.md"

    generated_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    md_content = f"""# Workspace Heuristic Text Scan Report

**Date Generated:** {generated_at}  
**Workspace:** `{WORKSPACE_ROOT.name}`  
**Overall Scan Status:** `{audit_data['status']}`  

## 1. Scope and Interpretation

This report records heuristic text checks performed by
`agents/file_audit_agent.py`.

The utility reads selected files and searches for domain references,
boolean-check tokens and numerical-handling markers. It does not
execute engineering tests or verify requirements traceability,
input rejection, numerical correctness or engineering compliance.

Comments and unrelated code can satisfy the text searches.
Numerical markers such as `float('inf')` do not establish that a
numerical safeguard exists.

PASS means the configured text check matched, or the selected files
were readable. QUERY means a reference or marker needs review.
FAIL means a required file could not be read or the boolean-token
check did not match.

The overall status uses FAIL before QUERY before PASS. It is a scan
result, not engineering acceptance or automatic sign-off.

## 2. Scan Results

| Rule ID | Status | Details |
| :--- | :---: | :--- |
"""

    for check in audit_data["checks"]:
        rule = _table_text(check["rule"])
        status = _table_text(check["status"])
        details = _table_text(check["details"])
        md_content += f"| {rule} | {status} | {details} |\n"

    md_content += "\n## 3. Files Scanned Successfully\n\n"
    scanned_files = audit_data["evidence"].get("scanned_files", [])

    if scanned_files:
        for path in scanned_files:
            md_content += f"- `{path}`\n"
    else:
        md_content += "No selected files were read successfully.\n"

    read_errors = audit_data["evidence"].get("read_errors", {})
    if read_errors:
        md_content += "\n## 4. File Read Failures\n\n"
        for path, error in read_errors.items():
            md_content += f"- `{path}`: {_table_text(error)}\n"

    md_content += """
---

Behavioural verification must be assessed separately using automated
tests and numerical validation evidence. No automatic sign-off is
provided by this report.
"""

    report_path.write_text(md_content, encoding="utf-8")
    print(f"Generated heuristic scan report at: {report_path}")
    return report_path


if __name__ == "__main__":
    generate_markdown_report()