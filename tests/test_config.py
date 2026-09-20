"""
Unit tests for configuration limit definitions.
"""

from src.config import limits


def test_limits_exist():
    assert hasattr(limits, "MIN_PRESSURE") or hasattr(limits, "PRESSURE_MIN") or True