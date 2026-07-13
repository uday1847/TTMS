from datetime import date
from decimal import Decimal
import uuid
from typing import Sequence, Any

from sqlalchemy import select, func, and_, or_, desc, asc, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository
from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_status_history import InvoiceStatusHistory
from app.domain.entities.trip import Trip
from app.domain.entities.party import Party
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.enums.invoice_status import InvoiceStatus


class SQLAlchemyInvoiceRepository(SQLAlchemyBaseRepository[Invoice], InvoiceRepository):
    """
    SQLAlchemy 2.0 Async implementation of the InvoiceRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Invoice)

    async def get_by_id(self, id: uuid.UUID) -> Invoice | None:
        """
        Retrieves a single active invoice with all nested relations eager loaded.
        """
        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.party),
                selectinload(Invoice.trip).selectinload(Trip.driver),
                selectinload(Invoice.trip).selectinload(Trip.tractor),
            )
            .where(
                Invoice.id == id,
                Invoice.deleted_at.is_(None)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        """
        Retrieves a single active invoice matching the unique invoice number.
        """
        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.party),
                selectinload(Invoice.trip).selectinload(Trip.driver),
                selectinload(Invoice.trip).selectinload(Trip.tractor),
            )
            .where(
                Invoice.invoice_number == invoice_number,
                Invoice.deleted_at.is_(None)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_trip(self, trip_id: uuid.UUID) -> Invoice | None:
        """
        Retrieves the active invoice generated against the specified trip.
        """
        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.party),
                selectinload(Invoice.trip).selectinload(Trip.driver),
                selectinload(Invoice.trip).selectinload(Trip.tractor),
            )
            .where(
                Invoice.trip_id == trip_id,
                Invoice.deleted_at.is_(None)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_max_sequence_for_year(self, year: int) -> int:
        """
        Extracts the maximum sequence number allocated in the specified financial year.
        """
        stmt = (
            select(Invoice.invoice_number)
            .where(
                Invoice.invoice_number.like(f"INV-{year}-%"),
                Invoice.deleted_at.is_(None)
            )
        )
        res = await self.session.execute(stmt)
        invoice_numbers = res.scalars().all()

        max_seq = 0
        for num in invoice_numbers:
            try:
                parts = num.split("-")
                if len(parts) == 3:
                    seq_part = int(parts[2])
                    if seq_part > max_seq:
                        max_seq = seq_part
            except ValueError:
                continue

        return max_seq

    async def get_invoice_status_history(self, invoice_id: uuid.UUID) -> Sequence[InvoiceStatusHistory]:
        """
        Returns history logs containing status changes for a given invoice.
        """
        stmt = (
            select(InvoiceStatusHistory)
            .options(selectinload(InvoiceStatusHistory.user))
            .where(
                InvoiceStatusHistory.invoice_id == invoice_id,
                InvoiceStatusHistory.deleted_at.is_(None)
            )
            .order_by(InvoiceStatusHistory.changed_at.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_invoice_dashboard_summary(self) -> dict[str, Any]:
        """
        Retrieves fully consolidated dashboard aggregates for counts, collections, and revenues.
        """
        # Overall status counts
        count_stmt = (
            select(Invoice.status, func.count(Invoice.id))
            .where(Invoice.deleted_at.is_(None))
            .group_by(Invoice.status)
        )
        res_counts = await self.session.execute(count_stmt)
        counts_dict = {status.value: count for status, count in res_counts.all()}

        # Overall revenue, collected, outstanding
        overall_stmt = (
            select(
                func.coalesce(func.sum(Invoice.gross_amount), Decimal("0.00")),
                func.coalesce(func.sum(Invoice.received_amount), Decimal("0.00")),
                func.coalesce(func.sum(Invoice.balance_amount), Decimal("0.00"))
            )
            .where(Invoice.deleted_at.is_(None))
        )
        res_overall = await self.session.execute(overall_stmt)
        total_rev, total_coll, total_out = res_overall.one()

        # Overdue Invoices count (due_date < current_date and status not in PAID or CANCELLED)
        today_date = date.today()
        overdue_stmt = (
            select(func.count(Invoice.id))
            .where(
                Invoice.due_date < today_date,
                Invoice.status.notin_([InvoiceStatus.PAID, InvoiceStatus.CANCELLED]),
                Invoice.deleted_at.is_(None)
            )
        )
        res_overdue = await self.session.execute(overdue_stmt)
        overdue_count = res_overdue.scalar() or 0

        # Current Month metrics
        current_month = today_date.month
        current_year = today_date.year
        month_stmt = (
            select(
                func.coalesce(func.sum(Invoice.gross_amount), Decimal("0.00")),
                func.coalesce(func.sum(Invoice.received_amount), Decimal("0.00")),
                func.coalesce(func.sum(Invoice.balance_amount), Decimal("0.00"))
            )
            .where(
                extract('month', Invoice.invoice_date) == current_month,
                extract('year', Invoice.invoice_date) == current_year,
                Invoice.deleted_at.is_(None)
            )
        )
        res_month = await self.session.execute(month_stmt)
        m_rev, m_coll, m_out = res_month.one()

        # Year metrics
        year_stmt = (
            select(
                func.coalesce(func.sum(Invoice.gross_amount), Decimal("0.00")),
                func.coalesce(func.sum(Invoice.received_amount), Decimal("0.00")),
                func.coalesce(func.sum(Invoice.balance_amount), Decimal("0.00"))
            )
            .where(
                extract('year', Invoice.invoice_date) == current_year,
                Invoice.deleted_at.is_(None)
            )
        )
        res_year = await self.session.execute(year_stmt)
        y_rev, y_coll, y_out = res_year.one()

        return {
            "total_invoices": sum(counts_dict.values()),
            "draft_count": counts_dict.get("DRAFT", 0),
            "issued_count": counts_dict.get("ISSUED", 0),
            "partially_paid_count": counts_dict.get("PARTIALLY_PAID", 0),
            "paid_count": counts_dict.get("PAID", 0),
            "cancelled_count": counts_dict.get("CANCELLED", 0),
            "total_revenue": total_rev,
            "total_collected": total_coll,
            "total_outstanding": total_out,
            "overdue_count": overdue_count,
            "monthly_analytics": {
                "revenue": m_rev,
                "collection": m_coll,
                "outstanding": m_out
            },
            "yearly_analytics": {
                "revenue": y_rev,
                "collection": y_coll,
                "outstanding": y_out
            }
        }

    async def get_overdue_invoices(self) -> Sequence[Invoice]:
        """
        Retrieves invoices where due_date < current_date and status is not PAID or CANCELLED.
        """
        today_date = date.today()
        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.party),
                selectinload(Invoice.trip).selectinload(Trip.driver),
                selectinload(Invoice.trip).selectinload(Trip.tractor),
            )
            .where(
                Invoice.due_date < today_date,
                Invoice.status.notin_([InvoiceStatus.PAID, InvoiceStatus.CANCELLED]),
                Invoice.deleted_at.is_(None)
            )
            .order_by(Invoice.due_date.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_pending_invoices(self) -> Sequence[Invoice]:
        """
        Retrieves invoices which are either DRAFT, ISSUED, or PARTIALLY_PAID.
        """
        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.party),
                selectinload(Invoice.trip).selectinload(Trip.driver),
                selectinload(Invoice.trip).selectinload(Trip.tractor),
            )
            .where(
                Invoice.status.in_([InvoiceStatus.DRAFT, InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID]),
                Invoice.deleted_at.is_(None)
            )
            .order_by(Invoice.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_paid_invoices(self) -> Sequence[Invoice]:
        """
        Retrieves fully settled invoices (status PAID).
        """
        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.party),
                selectinload(Invoice.trip).selectinload(Trip.driver),
                selectinload(Invoice.trip).selectinload(Trip.tractor),
            )
            .where(
                Invoice.status == InvoiceStatus.PAID,
                Invoice.deleted_at.is_(None)
            )
            .order_by(Invoice.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

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
        # Start base statement with joins to satisfy joins-based search
        stmt = (
            select(Invoice)
            .join(Invoice.trip, isouter=True)
            .join(Invoice.party, isouter=True)
            .options(
                selectinload(Invoice.party),
                selectinload(Invoice.trip).selectinload(Trip.driver),
                selectinload(Invoice.trip).selectinload(Trip.tractor),
            )
            .where(Invoice.deleted_at.is_(None))
        )

        # Filters mapping
        if status:
            stmt = stmt.where(Invoice.status == status)
        if party_id:
            stmt = stmt.where(Invoice.party_id == party_id)
        if trip_id:
            stmt = stmt.where(Invoice.trip_id == trip_id)
        if date_from:
            stmt = stmt.where(Invoice.invoice_date >= date_from)
        if date_to:
            stmt = stmt.where(Invoice.invoice_date <= date_to)
        if balance_min is not None:
            stmt = stmt.where(Invoice.balance_amount >= balance_min)
        if balance_max is not None:
            stmt = stmt.where(Invoice.balance_amount <= balance_max)

        # Multi-faceted search: invoice_number, party name, party mobile, party GST, party PAN, trip_number
        if search_query:
            q = f"%{search_query}%"
            stmt = stmt.where(
                or_(
                    Invoice.invoice_number.ilike(q),
                    Party.name.ilike(q),
                    Party.mobile_number.ilike(q),
                    Party.gst_number.ilike(q),
                    Party.pan_number.ilike(q),
                    Trip.trip_number.ilike(q),
                )
            )

        # Count total matches matching criteria before paging
        count_stmt = select(func.count()).select_from(stmt.subquery())
        res_count = await self.session.execute(count_stmt)
        total = res_count.scalar() or 0

        # Apply Sort order
        sort_attr = getattr(Invoice, sort_by, Invoice.created_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_attr))
        else:
            stmt = stmt.order_by(desc(sort_attr))

        # Apply Pagination offset and limit
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)

        res = await self.session.execute(stmt)
        invoices = res.scalars().all()

        return invoices, total
