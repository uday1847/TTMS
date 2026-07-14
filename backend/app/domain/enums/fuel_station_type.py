from enum import Enum


class FuelStationType(str, Enum):
    COMPANY = "COMPANY"
    PRIVATE = "PRIVATE"
    MOBILE = "MOBILE"
    OTHER = "OTHER"
