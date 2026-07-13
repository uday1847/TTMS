from datetime import date
from decimal import Decimal
import uuid

from sqlalchemy import String, Date, Numeric, ForeignKey, Index, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.payment_source import PaymentSource
from app.domain.enums.payment_status import PaymentStatus


class InvoicePayment(BaseEntity):
    __tablename__ = "invoice_payments"

    receipt_number: Mapped[str] = mapped_column(String(30), nullable=False)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    payment_source: Mapped[PaymentSource] = mapped_column(Enum(PaymentSource, name="payment_source_enum"), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus, name="payment_status_enum"), nullable=False, default=PaymentStatus.SUCCESS)

    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    account_holder: Mapped[str | None] = mapped_column(String(100), nullable=True)
    transaction_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cheque_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cheque_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    received_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")
    receiver: Mapped["User"] = relationship("User", foreign_keys=[received_by])

    __table_args__ = (
        Index(
            "ix_invoice_payments_receipt_number", 
            "receipt_number", 
            unique=True, 
            postgresql_where=mapped_column("deleted_at").is_(None)
        ),
        Index("ix_invoice_payments_invoice_id", "invoice_id"),
        Index("ix_invoice_payments_payment_date", "payment_date"),
        Index("ix_invoice_payments_payment_status", "payment_status"),
        Index("ix_invoice_payments_payment_source", "payment_source"),
        Index("ix_invoice_payments_created_at", "created_at"),
    )
