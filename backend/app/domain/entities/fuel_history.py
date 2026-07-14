import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Numeric, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.fuel_transaction_status import FuelTransactionStatus

if TYPE_CHECKING:
    from app.domain.entities.fuel_transaction import FuelTransaction


class FuelHistory(BaseEntity):
    __tablename__ = "fuel_histories"

    fuel_transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fuel_transactions.id"), index=True
    )
    
    old_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    new_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    
    old_odometer: Mapped[int | None] = mapped_column(Integer)
    new_odometer: Mapped[int | None] = mapped_column(Integer)
    
    old_vendor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    new_vendor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    
    old_status: Mapped[FuelTransactionStatus | None] = mapped_column(SQLEnum(FuelTransactionStatus, name="fuel_transaction_status_enum", native_enum=True))
    new_status: Mapped[FuelTransactionStatus | None] = mapped_column(SQLEnum(FuelTransactionStatus, name="fuel_transaction_status_enum", native_enum=True))
    
    reason: Mapped[str] = mapped_column(String(500))
    edited_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    fuel_transaction: Mapped["FuelTransaction"] = relationship(
        "FuelTransaction", back_populates="histories"
    )
