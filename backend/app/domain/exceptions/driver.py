import uuid

from app.domain.exceptions.base import DomainException


class DriverNotFoundException(DomainException):
    """
    Raised when a requested driver is not found or is soft-deleted.
    """
    def __init__(self, driver_id: uuid.UUID) -> None:
        super().__init__(f"Driver with ID {driver_id} was not found.")


class DriverAlreadyExistsException(DomainException):
    """
    Raised when employee code or license number registration collisions occur.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)
