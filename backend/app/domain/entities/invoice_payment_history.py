from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy import String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity


class InvoicePaymentHistory(BaseEntity):
    __tablename__ = "invoice_payment_history"

    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoice_payments.id"), nullable=False)
    
    old_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    new_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    old_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    
    old_payment_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_payment_source: Mapped[str] = mapped_column(String(50), nullable=False)

    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    changed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    payment: Mapped["InvoicePayment"] = relationship("InvoicePayment", backref="histories")
    user: Mapped["User"] = relationship("User", foreign_keys=[changed_by])
