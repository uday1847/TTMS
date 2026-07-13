from enum import Enum


class PaymentSource(str, Enum):
    CASH = "CASH"
    BANK = "BANK"
    UPI = "UPI"
    CHEQUE = "CHEQUE"
    CARD = "CARD"
    ONLINE = "ONLINE"
    OTHER = "OTHER"
