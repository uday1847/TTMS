import uuid

from app.domain.exceptions.base import DomainException


class TractorNotFoundException(DomainException):
    """
    Raised when a requested tractor is not found or is soft-deleted.
    """
    def __init__(self, tractor_id: uuid.UUID) -> None:
        super().__init__(f"Tractor with ID {tractor_id} was not found.")


class TractorAlreadyExistsException(DomainException):
    """
    Raised when tractor number or RC number registration collisions occur.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TractorHasActiveTripsException(DomainException):
    """
    Raised when attempting to delete a tractor assigned to active trips.
    """
    def __init__(self, tractor_id: uuid.UUID) -> None:
        super().__init__(f"Tractor with ID {tractor_id} cannot be deleted because it is assigned to active trips.")
