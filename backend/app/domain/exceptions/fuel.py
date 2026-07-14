from app.domain.exceptions.base import DomainException


class FuelTransactionNotFoundException(DomainException):
    def __init__(self, message: str = "Fuel transaction record not found"):
        super().__init__(message=message)


class FuelValidationException(DomainException):
    def __init__(self, message: str = "Invalid fuel data"):
        super().__init__(message=message)


class FuelCapacityExceededException(DomainException):
    def __init__(self, message: str = "Liters entered exceed tractor fuel capacity"):
        super().__init__(message=message)


class FuelMileageException(DomainException):
    def __init__(self, message: str = "Calculated mileage is out of expected bounds"):
        super().__init__(message=message)


class FuelOdometerException(DomainException):
    def __init__(self, message: str = "Current odometer must be greater than previous odometer"):
        super().__init__(message=message)


class FuelVendorNotFoundException(DomainException):
    def __init__(self, message: str = "Fuel vendor not found"):
        super().__init__(message=message)


class FuelDuplicateException(DomainException):
    def __init__(self, message: str = "Duplicate fuel transaction detected"):
        super().__init__(message=message)
