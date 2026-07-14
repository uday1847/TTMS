class DomainException(Exception):
    """
    Base exception for all business/domain errors.
    Decoupled from HTTP or transport logic.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

class ResourceNotFoundException(DomainException):
    pass

class ValidationException(DomainException):
    pass

class UnauthorizedException(DomainException):
    pass

