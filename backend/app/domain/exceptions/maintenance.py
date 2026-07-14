from app.domain.exceptions.base import DomainException


class MaintenanceNotFoundException(DomainException):
    def __init__(self, message: str = "Maintenance record not found"):
        super().__init__(message=message)


class MaintenanceAlreadyScheduledException(DomainException):
    def __init__(self, message: str = "Tractor already has an active maintenance scheduled or in progress"):
        super().__init__(message=message)


class MaintenanceStatusException(DomainException):
    def __init__(self, message: str = "Invalid maintenance status transition"):
        super().__init__(message=message)


class MaintenanceValidationException(DomainException):
    def __init__(self, message: str = "Invalid maintenance data"):
        super().__init__(message=message)


class MaintenanceDeleteException(DomainException):
    def __init__(self, message: str = "Cannot delete a maintenance record that is not in SCHEDULED status"):
        super().__init__(message=message)
