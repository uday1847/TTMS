from datetime import date
from decimal import Decimal
import uuid
from typing import Any

from sqlalchemy import select, func, and_, desc, asc, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository
from app.domain.entities.trip_expense import TripExpense
from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.repositories.trip_expense_repository import TripExpenseRepository
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode
from app.domain.entities.trip_status_history import TripStatusHistory


class SQLAlchemyTripExpenseRepository(SQLAlchemyBaseRepository[TripExpense], TripExpenseRepository):
    """
    SQLAlchemy implementation of the TripExpenseRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TripExpense)

    async def get_by_id(self, id: uuid.UUID) -> TripExpense | None:
        """
        Retrieves a single Trip Expense by its ID, eager loading relations.
        """
        stmt = select(TripExpense).options(
            selectinload(TripExpense.trip),
            selectinload(TripExpense.party)
        ).where(
            TripExpense.id == id,
            TripExpense.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_trip_expenses(
        self,
        trip_id: uuid.UUID | None = None,
        expense_type: ExpenseType | None = None,
        payment_mode: PaymentMode | None = None,
        paid_to_name: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "expense_date",
        sort_order: str = "desc",
    ) -> tuple[list[TripExpense], int]:
        """
        Retrieves filtered, sorted, and paginated Trip Expenses.
        """
        # Base query filters
        filters = [TripExpense.deleted_at.is_(None)]

        if trip_id is not None:
            filters.append(TripExpense.trip_id == trip_id)
        if expense_type is not None:
            filters.append(TripExpense.expense_type == expense_type)
        if payment_mode is not None:
            filters.append(TripExpense.payment_mode == payment_mode)
        if paid_to_name is not None:
            filters.append(TripExpense.paid_to_name.ilike(f"%{paid_to_name}%"))
        if start_date is not None:
            filters.append(TripExpense.expense_date >= start_date)
        if end_date is not None:
            filters.append(TripExpense.expense_date <= end_date)
        if min_amount is not None:
            filters.append(TripExpense.amount >= min_amount)
        if max_amount is not None:
            filters.append(TripExpense.amount <= max_amount)

        # Count query
        count_stmt = select(func.count()).select_from(TripExpense).where(and_(*filters))
        count_res = await self.session.execute(count_stmt)
        total_count = count_res.scalar() or 0

        # Sort mapping
        sort_attr = getattr(TripExpense, sort_by, TripExpense.expense_date)
        order_expr = desc(sort_attr) if sort_order == "desc" else asc(sort_attr)

        # Eager load relationships
        stmt = (
            select(TripExpense)
            .options(selectinload(TripExpense.trip), selectinload(TripExpense.party))
            .where(and_(*filters))
            .order_by(order_expr)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        expenses = list(result.scalars().all())

        return expenses, total_count

    async def get_monthly_expenses(self, year: int) -> list[dict[str, Any]]:
        """
        Retrieves total expenses grouped by month for a given year.
        """
        stmt = (
            select(
                extract("month", TripExpense.expense_date).label("month"),
                func.sum(TripExpense.amount).label("total_amount"),
                func.count(TripExpense.id).label("count")
            )
            .where(
                TripExpense.deleted_at.is_(None),
                extract("year", TripExpense.expense_date) == year
            )
            .group_by(extract("month", TripExpense.expense_date))
            .order_by(asc("month"))
        )
        res = await self.session.execute(stmt)
        return [{"month": int(r.month), "total_amount": r.total_amount, "count": r.count} for r in res.all()]

    async def get_expenses_by_type(self, trip_id: uuid.UUID | None = None) -> list[dict[str, Any]]:
        """
        Retrieves aggregate expense sums grouped by ExpenseType.
        """
        filters = [TripExpense.deleted_at.is_(None)]
        if trip_id is not None:
            filters.append(TripExpense.trip_id == trip_id)

        stmt = (
            select(
                TripExpense.expense_type,
                func.sum(TripExpense.amount).label("total_amount"),
                func.count(TripExpense.id).label("count")
            )
            .where(and_(*filters))
            .group_by(TripExpense.expense_type)
            .order_by(desc("total_amount"))
        )
        res = await self.session.execute(stmt)
        return [{"type": r.expense_type.value, "amount": r.total_amount, "count": r.count} for r in res.all()]

    async def get_expenses_by_trip(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Retrieves aggregate expense summaries grouped by trip ID.
        """
        stmt = (
            select(
                TripExpense.trip_id,
                Trip.trip_number,
                func.sum(TripExpense.amount).label("total_amount"),
                func.count(TripExpense.id).label("count")
            )
            .join(Trip, Trip.id == TripExpense.trip_id)
            .where(TripExpense.deleted_at.is_(None))
            .group_by(TripExpense.trip_id, Trip.trip_number)
            .order_by(desc("total_amount"))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return [
            {
                "trip_id": str(r.trip_id),
                "trip_number": r.trip_number,
                "total_amount": r.total_amount,
                "count": r.count,
            }
            for r in res.all()
        ]

    async def get_top_expense_category(self) -> dict[str, Any] | None:
        """
        Retrieves the expense category with the highest total amount.
        """
        stmt = (
            select(
                TripExpense.expense_type,
                func.sum(TripExpense.amount).label("total_amount")
            )
            .where(TripExpense.deleted_at.is_(None))
            .group_by(TripExpense.expense_type)
            .order_by(desc("total_amount"))
            .limit(1)
        )
        res = await self.session.execute(stmt)
        row = res.first()
        if row:
            return {"type": row.expense_type.value, "amount": row.total_amount}
        return None

    async def get_trip_profit(self, trip_id: uuid.UUID) -> dict[str, Any] | None:
        """
        Retrieves financial aggregates (freight, advances, total expenses, net profit) for a trip.
        """
        # Fetch Trip freight & advance details first
        trip_stmt = select(Trip).where(Trip.id == trip_id, Trip.deleted_at.is_(None))
        trip_res = await self.session.execute(trip_stmt)
        trip = trip_res.scalar_one_or_none()
        if not trip:
            return None

        # Aggregate expenses
        exp_stmt = (
            select(
                func.sum(TripExpense.amount).label("total_expense"),
                func.count(TripExpense.id).label("count")
            )
            .where(TripExpense.trip_id == trip_id, TripExpense.deleted_at.is_(None))
        )
        exp_res = await self.session.execute(exp_stmt)
        row = exp_res.first()

        total_expense = row.total_expense if row and row.total_expense else Decimal("0.00")
        expense_count = row.count if row and row.count else 0
        net_profit = trip.freight_amount - total_expense

        # Calculate percentages
        profit_pct = Decimal("0.00")
        loss_pct = Decimal("0.00")
        if trip.freight_amount > 0:
            pct = (net_profit / trip.freight_amount) * 100
            if pct >= 0:
                profit_pct = round(pct, 2)
            else:
                loss_pct = round(abs(pct), 2)

        return {
            "trip_id": str(trip.id),
            "trip_number": trip.trip_number,
            "freight_amount": trip.freight_amount,
            "advance_amount": trip.advance_amount,
            "total_expense": total_expense,
            "net_profit": net_profit,
            "expense_count": expense_count,
            "profit_percentage": profit_pct,
            "loss_percentage": loss_pct,
        }

    async def get_driver_expense(self, driver_id: uuid.UUID) -> Decimal:
        """
        Retrieves sum of all expenses incurred by a driver.
        """
        stmt = (
            select(func.sum(TripExpense.amount))
            .join(Trip, Trip.id == TripExpense.trip_id)
            .where(
                TripExpense.deleted_at.is_(None),
                Trip.driver_id == driver_id,
                Trip.deleted_at.is_(None)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar() or Decimal("0.00")

    async def get_tractor_expense(self, tractor_id: uuid.UUID) -> Decimal:
        """
        Retrieves sum of all expenses incurred by a tractor.
        """
        stmt = (
            select(func.sum(TripExpense.amount))
            .join(Trip, Trip.id == TripExpense.trip_id)
            .where(
                TripExpense.deleted_at.is_(None),
                Trip.tractor_id == tractor_id,
                Trip.deleted_at.is_(None)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar() or Decimal("0.00")

    async def get_dashboard_summary(self) -> dict[str, Any]:
        """
        Retrieves global analytical summary metrics for dashboard reporting.
        """
        # Global expense summary
        exp_stmt = select(
            func.sum(TripExpense.amount).label("total_expenses"),
            func.count(TripExpense.id).label("expense_count")
        ).where(TripExpense.deleted_at.is_(None))
        exp_res = await self.session.execute(exp_stmt)
        exp_row = exp_res.first()
        total_expenses = exp_row.total_expenses if exp_row and exp_row.total_expenses else Decimal("0.00")
        expense_count = exp_row.expense_count if exp_row and exp_row.expense_count else 0

        # Global trip metrics
        trip_stmt = select(
            func.sum(Trip.freight_amount).label("total_freight"),
            func.sum(Trip.advance_amount).label("total_advances"),
            func.count(Trip.id).label("trip_count")
        ).where(Trip.deleted_at.is_(None))
        trip_res = await self.session.execute(trip_stmt)
        trip_row = trip_res.first()
        total_freight = trip_row.total_freight if trip_row and trip_row.total_freight else Decimal("0.00")
        total_advances = trip_row.total_advances if trip_row and trip_row.total_advances else Decimal("0.00")
        trip_count = trip_row.trip_count if trip_row and trip_row.trip_count else 0

        net_profit = total_freight - total_expenses
        remaining_advances = total_freight - total_advances

        return {
            "total_expenses": total_expenses,
            "expense_count": expense_count,
            "total_freight": total_freight,
            "total_advances": total_advances,
            "trip_count": trip_count,
            "net_profit": net_profit,
            "remaining_advances_to_collect": remaining_advances,
        }

    async def get_max_sequence_for_year(self, year: int) -> int:
        """
        Retrieves the maximum sequence number used for the specified year.
        """
        stmt = (
            select(TripExpense.expense_number)
            .where(
                TripExpense.expense_number.like(f"EXP-{year}-%"),
                TripExpense.deleted_at.is_(None)
            )
        )
        res = await self.session.execute(stmt)
        expense_numbers = res.scalars().all()
        
        max_seq = 0
        for num in expense_numbers:
            try:
                # Format is EXP-YYYY-XXXXXX, sequence is last 6 characters
                parts = num.split("-")
                if len(parts) == 3:
                    seq_part = int(parts[2])
                    if seq_part > max_seq:
                        max_seq = seq_part
            except ValueError:
                continue
                
        return max_seq

    async def get_trip_status_history(self, trip_id: uuid.UUID) -> list[TripStatusHistory]:
        """
        Retrieves status change history for a given trip.
        """
        stmt = (
            select(TripStatusHistory)
            .where(
                TripStatusHistory.trip_id == trip_id,
                TripStatusHistory.deleted_at.is_(None)
            )
            .order_by(TripStatusHistory.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
