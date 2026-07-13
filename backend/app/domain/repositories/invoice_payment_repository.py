import uuid
from abc import ABC, abstractmethod
from typing import Any, Tuple

from app.domain.entities.invoice_payment import InvoicePayment
from app.domain.repositories.base_repository import BaseRepository


class InvoicePaymentRepository(BaseRepository[InvoicePayment], ABC):
    """
    Contract for Invoice Payment data access operations.
    Extends the BaseRepository with methods specific to InvoicePayments.
    """

    @abstractmethod
    async def get_by_receipt_number(self, receipt_number: str) -> InvoicePayment | None:
        """Find a payment by its unique receipt number."""
        pass

    @abstractmethod
    async def get_invoice_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        invoice_id: uuid.UUID | None = None,
        party_id: uuid.UUID | None = None,
        payment_status: str | None = None,
        payment_source: str | None = None,
        sort_by: str | None = None,
        sort_desc: bool = True,
    ) -> Tuple[list[InvoicePayment], int]:
        """
        Get a paginated list of invoice payments with filtering, search, and dynamic sorting.
        """
        pass

    @abstractmethod
    async def get_dashboard_metrics(self) -> dict[str, Any]:
        """
        Get aggregated dashboard metrics (todays_collection, monthly, yearly, pending, etc.)
        """
        pass

    @abstractmethod
    async def get_payment_source_breakdown(self) -> dict[str, Any]:
        """
        Get a breakdown of collections by payment source for charting.
        """
        pass
