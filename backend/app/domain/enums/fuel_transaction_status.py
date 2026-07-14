from enum import Enum


class FuelTransactionStatus(str, Enum):
    DRAFT = "DRAFT"
    VERIFIED = "VERIFIED"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"
