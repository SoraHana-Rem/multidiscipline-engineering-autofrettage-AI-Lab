"""
Custom warnings and exception classes for pressure vessel analysis.
"""

class PressureVesselWarning(UserWarning):
    """Emitted when a thick-wall (Lamé) regime is selected (REQ-FUN-002)."""
    pass


class ValidationError(ValueError):
    """Base exception for validation failures in the pressure vessel module."""
    pass