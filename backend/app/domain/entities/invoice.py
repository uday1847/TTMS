from datetime import date
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Enum as SQLEnum, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.invoice_status import InvoiceStatus

if TYPE_CHECKING:
    from app.domain.entities.trip import Trip
    from app.domain.entities.party import Party
    from app.domain.entities.invoice_status_history import InvoiceStatusHistory
    from app.domain.entities.invoice_payment import InvoicePayment
    from app.domain.entities.invoice_payment_history import InvoicePaymentHistory


class Invoice(BaseEntity):
    """
    Represents an Invoice billing document generated against a completed Trip.
    Tracks amounts receivable and outstanding balance for party settlement.
    """
    __tablename__ = "invoices"

    invoice_number: Mapped[str] = mapped_column(
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

    party_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("parties.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    invoice_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    received_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    balance_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(
            InvoiceStatus,
            name="invoice_status_enum",
            native_enum=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=InvoiceStatus.DRAFT,
        index=True,
    )

    # Relationships
    trip: Mapped["Trip"] = relationship(
        back_populates="invoice",
        foreign_keys=[trip_id],
    )
    party: Mapped["Party"] = relationship(
        back_populates="invoices",
        foreign_keys=[party_id],
    )
    status_history: Mapped[list["InvoiceStatusHistory"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="InvoiceStatusHistory.changed_at.asc()",
    )
    payments: Mapped[list["InvoicePayment"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="InvoicePayment.payment_date.desc()",
    )

    # Unique index constraints and amount validation checks
    __table_args__ = (
        Index(
            "uq_invoices_invoice_number",
            "invoice_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "uq_invoices_trip_id",
            "trip_id",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        CheckConstraint("gross_amount >= 0", name="chk_invoices_gross_amount"),
        CheckConstraint("received_amount >= 0", name="chk_invoices_received_amount"),
        CheckConstraint("balance_amount = gross_amount - received_amount", name="chk_invoices_balance_amount"),
    )
