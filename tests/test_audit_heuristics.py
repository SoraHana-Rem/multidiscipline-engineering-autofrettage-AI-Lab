"""Verify the audit's text-scan scope and generated report wording."""

import pytest

from agents import file_audit_agent as audit
from agents import generate_audit_doc as generator


@pytest.fixture
def audit_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "WORKSPACE_ROOT", tmp_path)
    monkeypatch.setattr(audit, "DOCS_DIR", tmp_path / "docs")
    monkeypatch.setattr(audit, "SRC_DIR", tmp_path / "src")

    files = {
        "docs/requirements.md": "Lamé",
        "src/errors.py": "",
        "src/analysis.py": "",
        "src/validation/inputs.py": "# isinstance(value, bool)",
        "src/physics/failure.py": "# ZeroDivisionError",
        "src/physics/thick_wall.py": "",
    }

    for relative_path, content in files.items():
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return tmp_path


def checks_by_rule(report):
    return {
        check["rule"]: check
        for check in report["checks"]
    }


def test_comments_can_match_without_verifying_behaviour(audit_workspace):
    # Only comments contain the source markers: this is deliberately
    # enough to match a text scan, but provides no working guards.
    report = audit.run_workspace_audit()
    checks = checks_by_rule(report)

    assert report["status"] == "PASS"
    assert report["evidence"]["method"] == "heuristic_text_scan"
    assert "comments" in report["evidence"]["limitations"]
    assert "not verified" in checks["DOC-TRACEABILITY"]["details"]
    assert "not verified" in checks["TYPE-GUARD-BOOL"]["details"]
    assert "not verified" in checks["NUMERICAL-GUARD-DIV0"]["details"]


def test_missing_file_prevents_overall_pass(audit_workspace):
    (audit_workspace / "src/errors.py").unlink()

    report = audit.run_workspace_audit()

    assert report["status"] == "FAIL"
    assert checks_by_rule(report)["FILE-READ"]["status"] == "FAIL"
    assert "src/errors.py" in report["evidence"]["read_errors"]
    assert "src/errors.py" not in report["evidence"]["scanned_files"]


def test_failed_read_path_is_not_scanned(audit_workspace):
    # A marker in a missing filename must not satisfy a source check.
    (audit_workspace / "src/physics/failure.py").write_text(
        "", encoding="utf-8"
    )
    (audit_workspace / "src/errors.py").unlink()

    report = audit.run_workspace_audit()

    assert report["status"] == "FAIL"
    assert report["evidence"]["numerical_tokens_found"] == []


def test_decode_error_is_reported(audit_workspace):
    (audit_workspace / "src/errors.py").write_bytes(b"\xff")

    report = audit.run_workspace_audit()

    assert report["status"] == "FAIL"
    assert "UnicodeDecodeError" in (
        report["evidence"]["read_errors"]["src/errors.py"]
    )


def test_missing_domain_reference_requests_review(audit_workspace):
    (audit_workspace / "docs/requirements.md").write_text(
        "No domain references here.", encoding="utf-8"
    )

    report = audit.run_workspace_audit()

    assert report["status"] == "QUERY"
    assert checks_by_rule(report)["DOC-TRACEABILITY"]["status"] == "QUERY"


def test_missing_boolean_tokens_fails_text_check(audit_workspace):
    (audit_workspace / "src/validation/inputs.py").write_text(
        "", encoding="utf-8"
    )

    report = audit.run_workspace_audit()

    assert report["status"] == "FAIL"
    assert checks_by_rule(report)["TYPE-GUARD-BOOL"]["status"] == "FAIL"


def test_missing_numerical_marker_requests_review(audit_workspace):
    (audit_workspace / "src/physics/failure.py").write_text(
        "", encoding="utf-8"
    )

    report = audit.run_workspace_audit()

    assert report["status"] == "QUERY"
    assert checks_by_rule(report)["NUMERICAL-GUARD-DIV0"]["status"] == "QUERY"


def test_generated_report_explains_scope(audit_workspace, monkeypatch):
    monkeypatch.setattr(generator, "WORKSPACE_ROOT", audit_workspace)

    report_path = generator.generate_markdown_report()
    content = report_path.read_text(encoding="utf-8")

    assert report_path == audit_workspace / "docs/week-14-audit.md"
    assert "Workspace Heuristic Text Scan Report" in content
    assert "Overall Scan Status" in content
    assert "not engineering acceptance" in content
    assert "No automatic sign-off" in content
    assert "Compliance Checklist" not in content
    assert "Verified that" not in content
    assert "automatically signed off" not in content