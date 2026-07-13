from datetime import date
from app.domain.repositories.trip_repository import TripRepository


class TripNumberGenerator:
    """
    Auto-sequence generator for Trip identification numbers.
    Constructs sequence following the pattern: TRIP-YYYY-XXXXXX
    """

    def __init__(self, repository: TripRepository) -> None:
        self.repository = repository

    async def generate(self) -> str:
        """
        Generates a unique sequential trip number based on current year index counts.
        """
        current_year = date.today().year
        sequence_count = await self.repository.get_max_sequence_for_year(current_year)
        next_sequence = sequence_count + 1
        return f"TRIP-{current_year}-{next_sequence:06d}"
