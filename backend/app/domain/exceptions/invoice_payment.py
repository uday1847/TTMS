from app.domain.exceptions.base import DomainException


class InvoicePaymentNotFoundException(DomainException):
    def __init__(self, message: str = "Invoice payment not found"):
        super().__init__(message=message, name="InvoicePaymentNotFoundException")


class InvoicePaymentExceededException(DomainException):
    def __init__(self, message: str = "Payment amount exceeds invoice balance"):
        super().__init__(message=message, name="InvoicePaymentExceededException")


class InvoiceDraftException(DomainException):
    def __init__(self, message: str = "Cannot add payment to a DRAFT invoice"):
        super().__init__(message=message, name="InvoiceDraftException")


class InvoiceCancelledException(DomainException):
    def __init__(self, message: str = "Cannot add payment to a CANCELLED invoice"):
        super().__init__(message=message, name="InvoiceCancelledException")


class InvoiceAlreadyPaidException(DomainException):
    def __init__(self, message: str = "Cannot add payment to an already PAID invoice"):
        super().__init__(message=message, name="InvoiceAlreadyPaidException")


class InvoicePaymentValidationException(DomainException):
    def __init__(self, message: str = "Invalid invoice payment data"):
        super().__init__(message=message, name="InvoicePaymentValidationException")


class ReceiptNotFoundException(DomainException):
    def __init__(self, message: str = "Receipt not found"):
        super().__init__(message=message, name="ReceiptNotFoundException")
