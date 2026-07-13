from datetime import date
from app.domain.repositories.trip_expense_repository import TripExpenseRepository


class ExpenseNumberGenerator:
    """
    Auto-sequence generator for Trip Expense identification numbers.
    Constructs sequence following the pattern: EXP-YYYY-XXXXXX
    """

    def __init__(self, repository: TripExpenseRepository) -> None:
        self.repository = repository

    async def generate(self) -> str:
        """
        Generates a unique sequential expense number based on current year index counts.
        """
        current_year = date.today().year
        sequence_count = await self.repository.get_max_sequence_for_year(current_year)
        next_sequence = sequence_count + 1
        return f"EXP-{current_year}-{next_sequence:06d}"
