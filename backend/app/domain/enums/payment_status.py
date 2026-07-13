from enum import Enum


class PaymentStatus(str, Enum):
    # Existing for Trip Expense
    PAID = "PAID"
    UNPAID = "UNPAID"
    PARTIAL = "PARTIAL"
    
    # New for Invoice Payments
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
