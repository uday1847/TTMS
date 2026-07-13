import re

from app.domain.exceptions.base import DomainException


class UserValidationError(DomainException):
    """
    Raised when user properties fail business constraints.
    """
    pass


def validate_username(username: str) -> None:
    """
    Ensures username follows strict business patterns (alphanumeric, hyphens, underscores).
    """
    if len(username) < 3 or len(username) > 100:
        raise UserValidationError("Username must be between 3 and 100 characters.")
    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        raise UserValidationError("Username must only contain letters, numbers, hyphens, and underscores.")
