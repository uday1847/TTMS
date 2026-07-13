import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Tuple

from sqlalchemy import func, or_, select, desc, asc, cast, String
from sqlalchemy.orm import selectinload

from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_payment import InvoicePayment
from app.domain.entities.party import Party
from app.domain.entities.trip import Trip
from app.domain.repositories.invoice_payment_repository import InvoicePaymentRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyInvoicePaymentRepository(SQLAlchemyBaseRepository[InvoicePayment], InvoicePaymentRepository):
    """
    SQLAlchemy implementation of the Invoice Payment Repository.
    """

    def __init__(self, session):
        super().__init__(InvoicePayment, session)

    async def get_by_receipt_number(self, receipt_number: str) -> InvoicePayment | None:
        """Find a payment by its unique receipt number."""
        stmt = (
            select(InvoicePayment)
            .options(
                selectinload(InvoicePayment.invoice).selectinload(Invoice.party),
                selectinload(InvoicePayment.invoice).selectinload(Invoice.trip),
            )
            .where(
                InvoicePayment.receipt_number == receipt_number,
                InvoicePayment.deleted_at.is_(None)
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

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
        stmt = (
            select(InvoicePayment)
            .join(InvoicePayment.invoice)
            .join(Invoice.party)
            .join(Invoice.trip)
            .options(
                selectinload(InvoicePayment.invoice).selectinload(Invoice.party),
                selectinload(InvoicePayment.invoice).selectinload(Invoice.trip),
            )
            .where(InvoicePayment.deleted_at.is_(None))
        )

        if invoice_id:
            stmt = stmt.where(InvoicePayment.invoice_id == invoice_id)

        if party_id:
            stmt = stmt.where(Invoice.party_id == party_id)

        if payment_status:
            stmt = stmt.where(cast(InvoicePayment.payment_status, String) == payment_status)

        if payment_source:
            stmt = stmt.where(cast(InvoicePayment.payment_source, String) == payment_source)

        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    InvoicePayment.receipt_number.ilike(search_term),
                    Invoice.invoice_number.ilike(search_term),
                    Trip.trip_number.ilike(search_term),
                    Party.name.ilike(search_term),
                    InvoicePayment.transaction_number.ilike(search_term),
                )
            )

        # Count total records before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self._session.execute(count_stmt)
        total_count = total.scalar_one()

        # Dynamic Sorting
        sort_column = InvoicePayment.payment_date
        if sort_by == "amount":
            sort_column = InvoicePayment.amount
        elif sort_by == "created_at":
            sort_column = InvoicePayment.created_at
        elif sort_by == "receipt_number":
            sort_column = InvoicePayment.receipt_number

        if sort_desc:
            stmt = stmt.order_by(desc(sort_column), desc(InvoicePayment.created_at))
        else:
            stmt = stmt.order_by(asc(sort_column), asc(InvoicePayment.created_at))

        # Pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total_count

    async def get_dashboard_metrics(self) -> dict[str, Any]:
        """
        Get aggregated dashboard metrics for invoice payments.
        """
        today = date.today()
        first_day_of_month = today.replace(day=1)
        first_day_of_year = today.replace(month=4, day=1) if today.month >= 4 else today.replace(year=today.year - 1, month=4, day=1)

        # Todays Collection
        stmt_today = select(func.sum(InvoicePayment.amount)).where(
            InvoicePayment.payment_date == today,
            InvoicePayment.deleted_at.is_(None)
        )
        
        # Monthly Collection
        stmt_month = select(func.sum(InvoicePayment.amount)).where(
            InvoicePayment.payment_date >= first_day_of_month,
            InvoicePayment.deleted_at.is_(None)
        )
        
        # Yearly Collection
        stmt_year = select(func.sum(InvoicePayment.amount)).where(
            InvoicePayment.payment_date >= first_day_of_year,
            InvoicePayment.deleted_at.is_(None)
        )

        # Total Outstanding / Pending Receivables
        stmt_pending = select(func.sum(Invoice.balance_amount)).where(
            Invoice.deleted_at.is_(None),
            Invoice.balance_amount > 0
        )

        # Total Collected
        stmt_total_collected = select(func.sum(InvoicePayment.amount)).where(
            InvoicePayment.deleted_at.is_(None)
        )

        # Total Count
        stmt_count = select(func.count(InvoicePayment.id)).where(
            InvoicePayment.deleted_at.is_(None)
        )

        todays_collection = (await self._session.execute(stmt_today)).scalar() or Decimal("0.00")
        monthly_collection = (await self._session.execute(stmt_month)).scalar() or Decimal("0.00")
        yearly_collection = (await self._session.execute(stmt_year)).scalar() or Decimal("0.00")
        pending_receivables = (await self._session.execute(stmt_pending)).scalar() or Decimal("0.00")
        collected_amount = (await self._session.execute(stmt_total_collected)).scalar() or Decimal("0.00")
        collection_count = (await self._session.execute(stmt_count)).scalar() or 0

        return {
            "todays_collection": todays_collection,
            "monthly_collection": monthly_collection,
            "yearly_collection": yearly_collection,
            "pending_receivables": pending_receivables,
            "collected_amount": collected_amount,
            "outstanding_amount": pending_receivables,
            "collection_count": collection_count,
        }

    async def get_payment_source_breakdown(self) -> dict[str, Any]:
        """
        Get a breakdown of collections by payment source for charting.
        """
        stmt = (
            select(
                InvoicePayment.payment_source, 
                func.sum(InvoicePayment.amount).label("total_amount")
            )
            .where(InvoicePayment.deleted_at.is_(None))
            .group_by(InvoicePayment.payment_source)
        )
        
        result = await self._session.execute(stmt)
        
        breakdown = {}
        for row in result.all():
            source = row[0].value if hasattr(row[0], 'value') else str(row[0])
            amount = row[1]
            breakdown[source] = amount

        return breakdown
