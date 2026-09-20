class AutofrettageError(Exception):
    """Base exception class for autofrettage engineering calculations."""
    pass

class ValidationError(AutofrettageError):
    """Raised when geometric, material, or pressure inputs violate domain bounds."""
    pass

