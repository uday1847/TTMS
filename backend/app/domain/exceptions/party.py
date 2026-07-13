import uuid

from app.domain.exceptions.base import DomainException


class PartyNotFoundException(DomainException):
    """
    Raised when a requested party is not found or is soft-deleted.
    """
    def __init__(self, party_id: uuid.UUID) -> None:
        super().__init__(f"Party with ID {party_id} was not found.")


class PartyAlreadyExistsException(DomainException):
    """
    Raised when mobile_number, gst_number, or pan_number collisions occur.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PartyHasActiveTripsException(DomainException):
    """
    Raised when attempting to delete a party assigned to active trips.
    """
    def __init__(self, party_id: uuid.UUID) -> None:
        super().__init__(f"Party with ID {party_id} cannot be deleted because they are assigned to active trips.")
