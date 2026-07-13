import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Enum as SQLEnum, ForeignKey, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.driver_status import DriverStatus

if TYPE_CHECKING:
    from app.domain.entities.user import User


class Driver(BaseEntity):
    """
    Represents a vehicle driver, containing licensing, contact profiles,
    payroll terms, and operational status.
    """
    __tablename__ = "drivers"

    # Profile integration link (if the driver has a user account to login)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Unique identification details
    employee_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    license_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    license_expiry: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    license_class: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # Contact Info
    contact_phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    emergency_contact_phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # Financial / Payout metrics
    fixed_salary: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0.00,
    )

    commission_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=0.00,
    )

    driver_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,  # e.g., 'SALARIED', 'COMMISSION_BASED', 'CONTRACT'
    )

    current_status: Mapped[DriverStatus] = mapped_column(
        SQLEnum(DriverStatus, name="driver_status_enum", native_enum=True),
        nullable=False,
        default=DriverStatus.AVAILABLE,
    )

    # Relationships
    user: Mapped["User | None"] = relationship(foreign_keys=[user_id])

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_drivers_employee_code",
            "employee_code",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "uq_drivers_license_number",
            "license_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        CheckConstraint("fixed_salary >= 0", name="chk_drivers_salary"),
        CheckConstraint("commission_percentage >= 0 AND commission_percentage <= 100", name="chk_drivers_commission"),
    )
