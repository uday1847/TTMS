import uuid
from app.domain.exceptions.base import DomainException


class InvoiceException(DomainException):
    """Base exception for Invoice module errors."""
    pass


class InvoiceNotFoundException(InvoiceException):
    def __init__(self, invoice_id: uuid.UUID) -> None:
        self.invoice_id = invoice_id
        super().__init__(f"Invoice with ID {invoice_id} not found.")


class InvoiceAlreadyExistsException(InvoiceException):
    def __init__(self, trip_id: uuid.UUID) -> None:
        self.trip_id = trip_id
        super().__init__(f"An active invoice already exists for Trip with ID {trip_id}.")


class InvoiceStatusException(InvoiceException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvoicePaymentException(InvoiceException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvoiceGenerationException(InvoiceException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
