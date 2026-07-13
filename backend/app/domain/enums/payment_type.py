from enum import StrEnum


class PaymentType(StrEnum):
    """
    Represents the direction of a financial transaction.
    """
    RECEIPT = "receipt"          # Cash inflow (e.g. client invoice payment)
    DISBURSEMENT = "disbursement"  # Cash outflow (e.g. driver payout, expense payment)
