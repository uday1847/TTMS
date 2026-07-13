from enum import StrEnum


class DriverStatus(StrEnum):
    """
    Tracks the current operational status of a driver.
    """
    AVAILABLE = "available"
    ON_TRIP = "on_trip"
    ON_LEAVE = "on_leave"
    INACTIVE = "inactive"
