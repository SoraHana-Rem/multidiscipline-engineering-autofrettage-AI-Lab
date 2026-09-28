"""
Unit tests for configuration limit definitions.
"""

from src.config import limits


def test_range_limits_are_ordered():
    assert 0 <= limits.PRESSURE_MIN < limits.PRESSURE_MAX
    assert 0 < limits.RADIUS_MIN < limits.RADIUS_MAX
    assert 0 < limits.THICKNESS_MIN < limits.THICKNESS_MAX
    assert 0 < limits.YIELD_MIN < limits.YIELD_MAX


def test_thin_wall_ratio_threshold_is_ten():
    assert limits.THIN_WALL_RATIO_THRESHOLD == 10.0


def test_stress_zero_tolerance_is_small_and_positive():
    assert 0 < limits.STRESS_ZERO_TOLERANCE < 1e-6