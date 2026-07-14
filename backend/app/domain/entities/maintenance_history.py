import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.maintenance import Maintenance
    from app.domain.entities.user import User


class MaintenanceHistory(BaseEntity):
    __tablename__ = "maintenance_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    maintenance_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("maintenances.id", ondelete="CASCADE"), nullable=False)
    
    old_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    old_vendor_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    new_vendor_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    old_total_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    new_total_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    
    old_odometer: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_odometer: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    remarks: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    maintenance: Mapped["Maintenance"] = relationship("Maintenance", back_populates="histories", foreign_keys=[maintenance_id])
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[changed_by])
