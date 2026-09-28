import pytest
from src.main import run_pipeline


def test_run_pipeline_execution(capsys):
    # Tests end-to-end CLI pipeline execution with autofrettage
    run_pipeline(P=50.0, r_i=50.0, t=20.0, sigma_y=250.0, P_auto=80.0, json_output=True)
    captured = capsys.readouterr()
    assert "autofrettage" in captured.out
    assert "autofrettage_safety_factor" in captured.out
