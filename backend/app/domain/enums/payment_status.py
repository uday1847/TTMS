from enum import Enum


class PaymentStatus(str, Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    PARTIAL = "PARTIAL"
