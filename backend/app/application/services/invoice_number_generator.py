from datetime import date
from app.domain.repositories.invoice_repository import InvoiceRepository


class InvoiceNumberGenerator:
    """
    Auto-sequence generator for Invoice identification numbers.
    Constructs sequence following the pattern: INV-YYYY-XXXXXX
    """

    def __init__(self, repository: InvoiceRepository) -> None:
        self.repository = repository

    async def generate(self) -> str:
        """
        Generates a unique sequential invoice number based on current year index counts.
        """
        current_year = date.today().year
        sequence_count = await self.repository.get_max_sequence_for_year(current_year)
        next_sequence = sequence_count + 1
        return f"INV-{current_year}-{next_sequence:06d}"
