"""
Shared Pytest fixtures and reference test vectors (TV-1, TV-2, TV-3).
Reference: docs/requirements.md & docs/design.md
"""
import pytest


@pytest.fixture
def tv1_thin():
    """
    TV-1: Thin-wall reference test vector (r_i / t = 100 >= 10).
    Expected values evaluated for thin-wall plane stress state.
    """
    return {
        "P": 2.0,
        "r_i": 500.0,
        "t": 5.0,
        "sigma_y": 500.0,
        "expected_model": "thin_wall",
        "sigma_hoop": 200.0000,
        "sigma_long": 100.0000,
        "sigma_radial": 0.0,
        "sigma_vm": 173.2051,
        "safety_factor": 2.8868,
        "yielded": False,
    }


@pytest.fixture
def tv2_thick():
    """
    TV-2: Thick-wall reference test vector (r_i / t = 1 < 10).
    Expected values evaluated using Lamé triaxial equations at inner radius r = a.
    """
    return {
        "P": 1.0,
        "r_i": 10.0,
        "t": 10.0,
        "sigma_y": 250.0,
        "expected_model": "lame_thick_wall",
        "sigma_hoop": 1.6667,
        "sigma_long": 0.3333,
        "sigma_radial": -1.0000,
        "sigma_vm": 2.3094,
        "safety_factor": 108.2532,
        "yielded": False,
    }


@pytest.fixture
def tv3_yield():
    """
    TV-3: High-pressure yielding reference test vector (r_i / t = 100 >= 10).
    Expected values result in von Mises stress exceeding yield limit.
    """
    return {
        "P": 10.0,
        "r_i": 500.0,
        "t": 5.0,
        "sigma_y": 500.0,
        "expected_model": "thin_wall",
        "sigma_hoop": 1000.0000,
        "sigma_long": 500.0000,
        "sigma_radial": 0.0,
        "sigma_vm": 866.0254,
        "safety_factor": 0.5774,
        "yielded": True,
    }