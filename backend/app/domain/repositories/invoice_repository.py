import uuid
from abc import abstractmethod
from datetime import date
from typing import Sequence, Any

from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_status_history import InvoiceStatusHistory
from app.domain.repositories.base_repository import BaseRepository
from app.domain.enums.invoice_status import InvoiceStatus


class InvoiceRepository(BaseRepository[Invoice]):
    """
    Contract specifying retrieval logic for Invoice billing and collections.
    """

    @abstractmethod
    async def get_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        """
        Retrieves a single active invoice matching the unique invoice number.
        """
        pass

    @abstractmethod
    async def get_by_trip(self, trip_id: uuid.UUID) -> Invoice | None:
        """
        Retrieves the active invoice generated against the specified trip.
        """
        pass

    @abstractmethod
    async def get_max_sequence_for_year(self, year: int) -> int:
        """
        Extracts the maximum sequence number allocated in the specified financial year.
        """
        pass

    @abstractmethod
    async def get_invoice_status_history(self, invoice_id: uuid.UUID) -> Sequence[InvoiceStatusHistory]:
        """
        Returns history logs containing status changes for a given invoice.
        """
        pass

    @abstractmethod
    async def get_invoice_dashboard_summary(self) -> dict[str, Any]:
        """
        Retrieves fully consolidated dashboard aggregates for counts, collections, and revenues.
        """
        pass

    @abstractmethod
    async def get_overdue_invoices(self) -> Sequence[Invoice]:
        """
        Retrieves invoices where due_date < current_date and status is not PAID or CANCELLED.
        """
        pass

    @abstractmethod
    async def get_pending_invoices(self) -> Sequence[Invoice]:
        """
        Retrieves invoices which are either DRAFT, ISSUED, or PARTIALLY_PAID.
        """
        pass

    @abstractmethod
    async def get_paid_invoices(self) -> Sequence[Invoice]:
        """
        Retrieves fully settled invoices (status PAID).
        """
        pass

    @abstractmethod
    async def get_invoices(
        self,
        *,
        search_query: str | None = None,
        status: InvoiceStatus | None = None,
        party_id: uuid.UUID | None = None,
        trip_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        balance_min: float | None = None,
        balance_max: float | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        size: int = 10,
    ) -> tuple[Sequence[Invoice], int]:
        """
        Paginated listing supporting multi-faceted filters, dynamic sorting, and unified search.
        """
        pass
