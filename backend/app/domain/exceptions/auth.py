from app.domain.exceptions.base import DomainException


class AuthenticationException(DomainException):
    """
    Raised when authentication credentials fail validation.
    """
    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(message)


class AuthorizationException(DomainException):
    """
    Raised when authorization clearance fails.
    """
    def __init__(self, message: str = "Not authorized.") -> None:
        super().__init__(message)


class UserAlreadyExistsException(DomainException):
    """
    Raised when user registration email/username conflicts occur.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidCredentialsException(AuthenticationException):
    """
    Raised when user enters incorrect login credentials.
    """
    def __init__(self, message: str = "Invalid credentials.") -> None:
        super().__init__(message)


class RoleNotFoundException(DomainException):
    """
    Raised when a requested role cannot be found in the system catalog.
    """
    def __init__(self, role_name: str) -> None:
        super().__init__(f"Role '{role_name}' was not found.")


class PermissionDeniedException(AuthorizationException):
    """
    Raised when a user attempts an action for which they lack the required permissions or roles.
    """
    def __init__(self, message: str = "Permission denied.") -> None:
        super().__init__(message)


class TokenExpiredException(AuthenticationException):
    """
    Raised when a JWT access or refresh token has expired.
    """
    def __init__(self, message: str = "Token has expired.") -> None:
        super().__init__(message)
