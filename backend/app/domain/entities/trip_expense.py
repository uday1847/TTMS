from datetime import date
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Enum as SQLEnum, ForeignKey, Index, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode
from app.domain.enums.payment_status import PaymentStatus

if TYPE_CHECKING:
    from app.domain.entities.trip import Trip
    from app.domain.entities.party import Party


class TripExpense(BaseEntity):
    """
    Represents an operational expense entry linked to a single trip transaction.
    """
    __tablename__ = "trip_expenses"

    expense_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    party_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("parties.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    paid_to_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    expense_type: Mapped[ExpenseType] = mapped_column(
        SQLEnum(ExpenseType, name="expense_type_enum", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_mode: Mapped[PaymentMode] = mapped_column(
        SQLEnum(PaymentMode, name="payment_mode_enum", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus, name="payment_status_enum", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PaymentStatus.PAID,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Attachment metadata
    attachment_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    attachment_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    attachment_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    attachment_content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Audit IP fields
    created_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    updated_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    # Relationships
    trip: Mapped["Trip"] = relationship(back_populates="expenses", foreign_keys=[trip_id])
    party: Mapped["Party | None"] = relationship(foreign_keys=[party_id])

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_trip_expenses_number",
            "expense_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        CheckConstraint("amount > 0", name="chk_trip_expenses_amount"),
    )
