from datetime import date
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Enum as SQLEnum, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.trip_status import TripStatus

if TYPE_CHECKING:
    from app.domain.entities.driver import Driver
    from app.domain.entities.party import Party
    from app.domain.entities.tractor import Tractor
    from app.domain.entities.trip_status_history import TripStatusHistory
    from app.domain.entities.trip_expense import TripExpense
    from app.domain.entities.invoice import Invoice


class Trip(BaseEntity):
    """
    Represents a single transportation trip transaction.
    Records delivery details, client billing rates, material info, and operational status.
    """
    __tablename__ = "trips"

    # Trip identification
    trip_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    trip_date: Mapped[date] = mapped_column(
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

    # Locations
    source_location: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    destination_location: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    expected_delivery_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    actual_delivery_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # Financial details
    freight_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    advance_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[TripStatus] = mapped_column(
        SQLEnum(TripStatus, name="trip_status_enum", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TripStatus.PENDING,
        index=True,
    )

    # Relationships
    driver: Mapped["Driver"] = relationship(foreign_keys=[driver_id])
    tractor: Mapped["Tractor"] = relationship(foreign_keys=[tractor_id])
    party: Mapped["Party"] = relationship(foreign_keys=[party_id])
    status_history: Mapped[list["TripStatusHistory"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripStatusHistory.created_at.asc()",
    )
    expenses: Mapped[list["TripExpense"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[TripExpense.trip_id]"
    )
    invoice: Mapped["Invoice | None"] = relationship(
        back_populates="trip",
        uselist=False,
        lazy="selectin",
        foreign_keys="[Invoice.trip_id]"
    )
    fuel_transactions: Mapped[list["FuelTransaction"]] = relationship(
        "FuelTransaction",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_trips_trip_number",
            "trip_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        CheckConstraint("freight_amount > 0", name="chk_trips_freight_amount"),
        CheckConstraint("advance_amount >= 0", name="chk_trips_advance_amount"),
        CheckConstraint("advance_amount <= freight_amount", name="chk_trips_advance_freight"),
    )
