import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    String,
    ForeignKey,
    Numeric,
    Date,
    Integer,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.maintenance_status import MaintenanceStatus
from app.domain.enums.maintenance_type import MaintenanceType
from app.domain.enums.maintenance_priority import MaintenancePriority

if TYPE_CHECKING:
    from app.domain.entities.tractor import Tractor
    from app.domain.entities.maintenance_history import MaintenanceHistory


class Maintenance(BaseEntity):
    __tablename__ = "maintenances"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    maintenance_number: Mapped[str] = mapped_column(String(50), nullable=False)
    tractor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tractors.id"), nullable=False)
    
    maintenance_type: Mapped[MaintenanceType] = mapped_column(
        PGEnum(MaintenanceType, name="maintenance_type_enum", create_type=False),
        nullable=False,
    )
    priority: Mapped[MaintenancePriority] = mapped_column(
        PGEnum(MaintenancePriority, name="maintenance_priority_enum", create_type=False),
        nullable=False,
    )
    status: Mapped[MaintenanceStatus] = mapped_column(
        PGEnum(MaintenanceStatus, name="maintenance_status_enum", create_type=False),
        nullable=False,
        default=MaintenanceStatus.SCHEDULED,
    )

    vendor_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    vendor_mobile: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    service_center: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_service_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    current_odometer: Mapped[int] = mapped_column(Integer, nullable=False)
    next_service_odometer: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    parts_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    other_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    
    remarks: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    attachment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    tractor: Mapped["Tractor"] = relationship("Tractor", back_populates="maintenances", foreign_keys=[tractor_id])
    histories: Mapped[list["MaintenanceHistory"]] = relationship(
        "MaintenanceHistory",
        back_populates="maintenance",
        cascade="all, delete-orphan",
        order_by="desc(MaintenanceHistory.created_at)",
    )

    __table_args__ = (
        CheckConstraint("parts_cost >= 0", name="chk_maintenance_parts_cost"),
        CheckConstraint("labor_cost >= 0", name="chk_maintenance_labor_cost"),
        CheckConstraint("other_cost >= 0", name="chk_maintenance_other_cost"),
        CheckConstraint("total_cost >= 0", name="chk_maintenance_total_cost"),
        # We enforce start_date >= scheduled_date and completion_date >= start_date in python to avoid nullable logic complexity
        
        Index("idx_maintenance_number", maintenance_number),
        Index("idx_maintenance_tractor_id", tractor_id),
        Index("idx_maintenance_status", status),
        Index("idx_maintenance_scheduled_date", scheduled_date),
        Index("idx_maintenance_type", maintenance_type),
        Index("idx_maintenance_created_at", "created_at"),
        # Unique maintenance_number for non-deleted records
        Index(
            "idx_unique_maintenance_number",
            maintenance_number,
            unique=True,
            postgresql_where=mapped_column(String(50), name="deleted_at").is_(None)
        ),
    )
