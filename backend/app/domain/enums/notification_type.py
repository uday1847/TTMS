from enum import StrEnum


class NotificationType(StrEnum):
    """
    Classifies system notifications by purpose and context.
    """
    ALERT = "alert"
    SYSTEM = "system"
    INFO = "info"
    EXPIRY_REMINDER = "expiry_reminder"
    PAYMENT_REMINDER = "payment_reminder"
