from enum import StrEnum


class PaymentMode(StrEnum):
    """
    Defines modes of payment accepted or made by the system.
    """
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    CHEQUE = "cheque"
    CREDIT_CARD = "credit_card"
