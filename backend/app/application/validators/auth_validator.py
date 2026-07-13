from typing import Any

from app.domain.exceptions.auth import InvalidCredentialsException


def validate_auth_token_payload(payload: dict[str, Any]) -> str:
    """
    Validates decoded token payload claims.
    Returns the subject (user ID) if valid.
    """
    sub = payload.get("sub")
    if not sub:
        raise InvalidCredentialsException("Invalid token payload: missing subject identifier.")
    return sub
