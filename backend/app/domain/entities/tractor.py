import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Enum as SQLEnum, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.tractor_status import TractorStatus


class Tractor(BaseEntity):
    """
    Represents heavy vehicle assets, tracking registration, specs, insurance,
    mileage, and active maintenance status.
    """
    __tablename__ = "tractors"

    registration_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    chassis_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    engine_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    make: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    year_manufactured: Mapped[int] = mapped_column(
        nullable=False,
    )

    ownership_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,  # e.g., 'OWNED', 'LEASED', 'MARKET_HIRE'
    )

    insurance_expiry: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    fitness_certificate_expiry: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    road_tax_expiry: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    current_odometer: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    status: Mapped[TractorStatus] = mapped_column(
        SQLEnum(TractorStatus, name="tractor_status_enum", native_enum=True),
        nullable=False,
        default=TractorStatus.ACTIVE,
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_tractors_registration_number",
            "registration_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        CheckConstraint("current_odometer >= 0", name="chk_tractors_odometer"),
    )
