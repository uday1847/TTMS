from enum import Enum


class FuelPaymentMode(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    FUEL_CARD = "FUEL_CARD"
    CREDIT = "CREDIT"
    OTHER = "OTHER"
