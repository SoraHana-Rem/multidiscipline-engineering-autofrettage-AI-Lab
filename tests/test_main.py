import sys
import json
import pytest
from unittest.mock import patch
import src.main as main_module
from src.main import parse_arguments, run_pipeline


def test_parse_arguments():
    """Executes argument parser definition and flag evaluation."""
    test_args = [
        "main.py",
        "--pressure", "20.0",
        "--radius", "100.0",
        "--thickness", "20.0",
        "--yield-strength", "300.0",
        "--autofrettage-pressure", "58.0",
        "--json"
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
    """Executes terminal text printing with autofrettage summary using valid physical pressure."""
    run_pipeline(
        P=20.0,
        r_i=100.0,
        t=20.0,
        sigma_y=300.0,
        P_auto=58.0,
        json_output=False
    )
    captured = capsys.readouterr().out
    assert "PRESSURE VESSEL ANALYSIS SUMMARY" in captured
    assert "AUTOFRETTAGE CAPSTONE SUMMARY" in captured
    assert "Hoop Stress" in captured
    assert "Autofrettage Press" in captured


def test_run_pipeline_missing_autofrettage_flag_raise(capsys):
    """Executes raising ImportError when HAS_AUTOFRETTAGE is False."""
    with patch.object(main_module, "HAS_AUTOFRETTAGE", False):
        with pytest.raises(SystemExit) as exc_info:
            run_pipeline(
                P=20.0,
                r_i=100.0,
                t=20.0,
                sigma_y=300.0,
                P_auto=58.0,
                json_output=False
            )
        assert exc_info.value.code == 1
        err_msg = capsys.readouterr().err
        assert "Autofrettage module is requested but missing" in err_msg


def test_main_execution_block():
    """Executes __main__ entrypoint execution directly."""
    test_args = [
        "main.py",
        "-P", "20.0",
        "-r", "100.0",
        "-t", "20.0",
        "-sy", "300.0"
    ]
    with patch("sys.argv", test_args):
        exec(open("src/main.py").read(), {"__name__": "__main__"})