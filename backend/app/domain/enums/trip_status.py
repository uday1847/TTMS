from enum import StrEnum


class TripStatus(StrEnum):
    """
    Defines the states of a trip lifecycle.
    """
    PENDING = "pending"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    INVOICED = "invoiced"
    CANCELLED = "cancelled"
