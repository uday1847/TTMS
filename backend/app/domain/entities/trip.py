import datetime
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.driver import Driver
    from app.domain.entities.material import Material
    from app.domain.entities.party import Party
    from app.domain.entities.quarry import Quarry
    from app.domain.entities.tractor import Tractor


class Trip(BaseEntity):
    """
    Represents a single transportation trip transaction.
    Records delivery details, client billing rates, material info, and operational margins.
    """
    __tablename__ = "trips"

    # Trip identification
    trip_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    trip_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    # Asset and agent linkages
    tractor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("tractors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    driver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("drivers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    party_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("parties.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quarry_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("quarries.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    material_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("materials.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Quantities and rates
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Cost Side
    purchase_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    purchase_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Revenue Side
    sale_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    sale_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Expenses & margins
    transport_expense: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    other_expense: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    net_profit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Settlements details
    payment_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,  # e.g., 'CASH', 'DEBIT', 'PARTIAL'
    )

    cash_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    debit_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    driver: Mapped["Driver"] = relationship()
    tractor: Mapped["Tractor"] = relationship()
    party: Mapped["Party"] = relationship()
    quarry: Mapped["Quarry"] = relationship()
    material: Mapped["Material"] = relationship()

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_trips_trip_number",
            "trip_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        CheckConstraint("quantity >= 0", name="chk_trips_quantity"),
        CheckConstraint("purchase_rate >= 0", name="chk_trips_purchase_rate"),
        CheckConstraint("purchase_amount >= 0", name="chk_trips_purchase_amount"),
        CheckConstraint("sale_rate >= 0", name="chk_trips_sale_rate"),
        CheckConstraint("sale_amount >= 0", name="chk_trips_sale_amount"),
        CheckConstraint("transport_expense >= 0", name="chk_trips_transport_expense"),
        CheckConstraint("other_expense >= 0", name="chk_trips_other_expense"),
        CheckConstraint("cash_amount >= 0", name="chk_trips_cash_amount"),
        CheckConstraint("debit_amount >= 0", name="chk_trips_debit_amount"),
    )
