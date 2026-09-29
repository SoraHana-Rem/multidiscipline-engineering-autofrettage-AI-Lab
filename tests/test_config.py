"""
Unit tests for configuration limit definitions.
"""

from src.config import limits


def test_limits_exist():
    assert hasattr(limits, "PRESSURE_MIN")
    assert hasattr(limits, "PRESSURE_MAX")
    assert hasattr(limits, "THIN_WALL_RATIO_THRESHOLD")