import datetime
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.expense_category import ExpenseCategory
    from app.domain.entities.tractor import Tractor
    from app.domain.entities.trip import Trip


class Expense(BaseEntity):
    """
    Represents an operational expense (e.g., fuel, toll, maintenance, allowances)
    associated with trips, tractors, or general fleet costs.
    """
    __tablename__ = "expenses"

    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("expense_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Optional linkages (can be general or mapped to specific assets/trips)
    tractor_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("tractors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("trips.id", ondelete="CASCADE"),  # If a trip is deleted, cascade deletion of its specific expenses
        nullable=True,
        index=True,
    )

    # Financial details
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    expense_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    recipient: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    receipt_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    # Relationships
    category: Mapped["ExpenseCategory"] = relationship()
    tractor: Mapped["Tractor | None"] = relationship()
    trip: Mapped["Trip | None"] = relationship()

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_expenses_amount"),
        Index("idx_expenses_date", expense_date.desc()),
    )
