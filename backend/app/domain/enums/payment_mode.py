from enum import Enum


class PaymentMode(str, Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD = "CARD"
    CHEQUE = "CHEQUE"
    CREDIT = "CREDIT"
    OTHER = "OTHER"
