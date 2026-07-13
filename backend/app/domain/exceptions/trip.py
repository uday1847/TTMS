import uuid

from app.domain.exceptions.base import DomainException


class TripNotFoundException(DomainException):
    """
    Raised when a requested trip is not found or is soft-deleted.
    """
    def __init__(self, trip_id: uuid.UUID) -> None:
        super().__init__(f"Trip with ID {trip_id} was not found.")


class TripAlreadyExistsException(DomainException):
    """
    Raised when a trip number collision occurs.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TripStatusException(DomainException):
    """
    Raised when attempting an invalid workflow status transition.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DriverBusyException(DomainException):
    """
    Raised when attempting to assign a driver who is already on an active trip.
    """
    def __init__(self, driver_id: uuid.UUID) -> None:
        super().__init__(f"Driver with ID {driver_id} is already busy on another active trip.")


class TractorBusyException(DomainException):
    """
    Raised when attempting to assign a tractor which is already on an active trip.
    """
    def __init__(self, tractor_id: uuid.UUID) -> None:
        super().__init__(f"Tractor with ID {tractor_id} is already busy on another active trip.")


class TripDeleteException(DomainException):
    """
    Raised when attempting to delete a trip that is not in PENDING status.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InactiveDriverException(DomainException):
    """
    Raised when attempting to assign a driver whose account is inactive.
    """
    def __init__(self, driver_id: uuid.UUID) -> None:
        super().__init__(f"Driver with ID {driver_id} is inactive and cannot be assigned to trips.")


class InactiveTractorException(DomainException):
    """
    Raised when attempting to assign a tractor which is inactive.
    """
    def __init__(self, tractor_id: uuid.UUID) -> None:
        super().__init__(f"Tractor with ID {tractor_id} is inactive and cannot be assigned to trips.")


class InactivePartyException(DomainException):
    """
    Raised when attempting to assign a party which is inactive.
    """
    def __init__(self, party_id: uuid.UUID) -> None:
        super().__init__(f"Party with ID {party_id} is inactive and cannot be assigned to trips.")


class InvalidTripDateException(DomainException):
    """
    Raised when date constraints are violated.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class AdvanceAmountException(DomainException):
    """
    Raised when financial/advance rules are violated.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TripAlreadyCompletedException(DomainException):
    """
    Raised when trying to edit a trip that is completed or cancelled.
    """
    def __init__(self, trip_id: uuid.UUID) -> None:
        super().__init__(f"Trip with ID {trip_id} is completed or cancelled and cannot be edited.")
