import uuid


class TripExpenseException(Exception):
    """Base exception for Trip Expense module errors."""
    pass


class TripExpenseNotFoundException(TripExpenseException):
    def __init__(self, expense_id: uuid.UUID) -> None:
        self.expense_id = expense_id
        super().__init__(f"Trip expense with ID {expense_id} not found.")


class TripCompletedException(TripExpenseException):
    def __init__(self, trip_id: uuid.UUID) -> None:
        self.trip_id = trip_id
        super().__init__(f"Cannot add/modify/delete expenses on a COMPLETED trip (Trip ID: {trip_id}).")


class TripCancelledException(TripExpenseException):
    def __init__(self, trip_id: uuid.UUID) -> None:
        self.trip_id = trip_id
        super().__init__(f"Cannot add/modify/delete expenses on a CANCELLED trip (Trip ID: {trip_id}).")


class TripExpenseValidationException(TripExpenseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
