"""Tests for CLI arguments, output and error handling."""

import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import src.main as main_module
from src.main import parse_arguments, run_pipeline


def test_parse_arguments():
    """REQ-INP-001..004, REQ-AUT-001: Parse supported CLI inputs."""
    test_args = [
        "main.py",
        "--pressure", "20.0",
        "--radius", "100.0",
        "--thickness", "20.0",
        "--yield-strength", "300.0",
        "--autofrettage-pressure", "58.0",
        "--json",
    ]

    with patch("sys.argv", test_args):
        args = parse_arguments()

    assert args.pressure == 20.0
    assert args.radius == 100.0
    assert args.thickness == 20.0
    assert args.yield_strength == 300.0
    assert args.autofrettage_pressure == 58.0
    assert args.json is True


def test_run_pipeline_formatted_text_and_autofrettage_output(capsys):
    """REQ-FUN-004, REQ-AUT-004: Print results with scope limitations."""
    run_pipeline(
        P=50.0,
        r_i=50.0,
        t=20.0,
        sigma_y=250.0,
        P_auto=80.0,
    )

    output = capsys.readouterr().out

    assert "PRESSURE VESSEL ANALYSIS SUMMARY" in output
    assert "AUTOFRETTAGE CAPSTONE SUMMARY" in output
    assert "Bore SF estimate" in output
    assert "1.722" in output
    assert "Residual axial stress omitted" in output
    assert "wall minimum not assessed" in output


def test_run_pipeline_json_without_autofrettage(capsys):
    """REQ-FUN-004: Return baseline JSON without an autofrettage field."""
    run_pipeline(
        P=10.0,
        r_i=500.0,
        t=50.0,
        sigma_y=500.0,
        json_output=True,
    )

    data = json.loads(capsys.readouterr().out)

    assert data["model_used"] == "thin_wall"
    assert data["stresses_MPa"]["hoop"] == pytest.approx(100.0)
    assert data["yielded"] is False
    assert "autofrettage" not in data


def test_run_pipeline_json_with_autofrettage(capsys):
    """REQ-AUT-001, REQ-AUT-003, REQ-AUT-004: Preserve JSON results."""
    run_pipeline(
        P=50.0,
        r_i=50.0,
        t=20.0,
        sigma_y=250.0,
        P_auto=80.0,
        json_output=True,
    )

    data = json.loads(capsys.readouterr().out)
    auto = data["autofrettage"]

    assert auto["P_auto_MPa"] == 80.0
    assert auto["plastic_radius_mm"] == pytest.approx(53.699)
    assert auto["residual_hoop_inner_MPa"] == pytest.approx(-37.992)
    assert auto["autofrettage_safety_factor"] == pytest.approx(1.722)


def test_run_pipeline_invalid_input_exits(capsys):
    """REQ-VAL-002: Invalid pressure produces a CLI error and exit 1."""
    with pytest.raises(SystemExit) as exc_info:
        run_pipeline(
            P=-1.0,
            r_i=50.0,
            t=20.0,
            sigma_y=250.0,
        )

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "[EXECUTION ERROR]" in captured.err
    assert "Pressure must be positive" in captured.err
    assert captured.out == ""


def test_run_pipeline_missing_result_field_is_not_defaulted(capsys):
    """REQ-ERR-001: Missing solver fields must not produce default results."""
    malformed_result = SimpleNamespace(
        r_p=53.699,
        residual_hoop_inner=-37.992,
    )

    with patch.object(
        main_module,
        "calculate_autofrettage",
        return_value=malformed_result,
    ):
        with pytest.raises(AttributeError, match="safety_factor"):
            run_pipeline(
                P=50.0,
                r_i=50.0,
                t=20.0,
                sigma_y=250.0,
                P_auto=80.0,
            )

    assert capsys.readouterr().out == ""


def test_main_execution_block():
    """REQ-FUN-004: Execute the real module entry point."""
    repo_root = Path(main_module.__file__).resolve().parents[1]

    completed = subprocess.run(
        [
            sys.executable,
            "-m", "src.main",
            "-P", "10.0",
            "-r", "500.0",
            "-t", "50.0",
            "-sy", "500.0",
            "--json",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr

    data = json.loads(completed.stdout)
    assert data["model_used"] == "thin_wall"
    assert data["stresses_MPa"]["hoop"] == pytest.approx(100.0)