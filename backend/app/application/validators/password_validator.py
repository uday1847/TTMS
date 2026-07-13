import re

from app.domain.exceptions.base import DomainException


class PasswordValidationError(DomainException):
    """
    Exception raised when a proposed password fails policy complexity checks.
    """
    pass


def validate_password_complexity(password: str) -> None:
    """
    Validates password complexity policy.
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    """
    if len(password) < 8:
        raise PasswordValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise PasswordValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise PasswordValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise PasswordValidationError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise PasswordValidationError("Password must contain at least one special character.")
