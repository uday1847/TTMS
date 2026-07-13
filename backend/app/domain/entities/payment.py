import datetime
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Enum as SQLEnum, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.payment_mode import PaymentMode
from app.domain.enums.payment_type import PaymentType

if TYPE_CHECKING:
    from app.domain.entities.driver import Driver
    from app.domain.entities.expense_category import ExpenseCategory
    from app.domain.entities.party import Party
    from app.domain.entities.trip import Trip


class Payment(BaseEntity):
    """
    Represents a payment transaction in the system, either incoming (receipts from clients)
    or outgoing (disbursements to drivers, suppliers, or expense categories).
    """
    __tablename__ = "payments"

    # Unique reference voucher code
    payment_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    payment_type: Mapped[PaymentType] = mapped_column(
        SQLEnum(PaymentType, name="payment_type_enum", native_enum=True),
        nullable=False,
    )

    payment_mode: Mapped[PaymentMode] = mapped_column(
        SQLEnum(PaymentMode, name="payment_mode_enum", native_enum=True),
        nullable=False,
    )

    # Monetary fields
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Linkages and relationships (nullable to support multiple payment types)
    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    party_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("parties.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    expense_category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("expense_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    trip: Mapped["Trip | None"] = relationship()
    party: Mapped["Party | None"] = relationship()
    driver: Mapped["Driver | None"] = relationship()
    expense_category: Mapped["ExpenseCategory | None"] = relationship()

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_payments_payment_number",
            "payment_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        CheckConstraint("amount > 0", name="chk_payments_amount"),
        CheckConstraint(
            "(party_id IS NOT NULL) OR (driver_id IS NOT NULL) OR (trip_id IS NOT NULL) OR (expense_category_id IS NOT NULL)",
            name="chk_payments_target_not_empty",
        ),
    )
