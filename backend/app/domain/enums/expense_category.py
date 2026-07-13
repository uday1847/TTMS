from enum import StrEnum


class ExpenseCategory(StrEnum):
    """
    Defines default categories for operational expenses.
    """
    DIESEL = "diesel"
    TOLL = "toll"
    MAINTENANCE = "maintenance"
    DRIVER_ALLOWANCE = "driver_allowance"
    POLICE_RTO = "police_rto"
    SPARE_PARTS = "spare_parts"
    TYRE = "tyre"
    INSURANCE = "insurance"
    OTHER = "other"
