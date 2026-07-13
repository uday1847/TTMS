from enum import StrEnum


class TractorStatus(StrEnum):
    """
    Represents the operational status of a tractor asset.
    """
    ACTIVE = "active"
    IN_MAINTENANCE = "in_maintenance"
    OUT_OF_SERVICE = "out_of_service"
