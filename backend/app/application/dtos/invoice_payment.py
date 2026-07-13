import uuid
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums.payment_source import PaymentSource
from app.domain.enums.payment_status import PaymentStatus


class InvoicePaymentBase(BaseModel):
    payment_date: date
    amount: Decimal = Field(..., gt=0, description="Payment amount must be greater than zero")
    payment_source: PaymentSource
    payment_status: PaymentStatus = Field(default=PaymentStatus.SUCCESS)
    
    bank_name: str | None = Field(default=None, max_length=100)
    account_holder: str | None = Field(default=None, max_length=100)
    transaction_number: str | None = Field(default=None, max_length=100)
    cheque_number: str | None = Field(default=None, max_length=50)
    cheque_date: date | None = None
    reference_number: str | None = Field(default=None, max_length=100)
    
    remarks: str | None = None

    @field_validator(
        "bank_name",
        "account_holder",
        "transaction_number",
        "cheque_number",
        "reference_number",
        "remarks",
        mode="before"
    )
    @classmethod
    def strip_strings(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            return v.strip() or None
        return v


class InvoicePaymentCreate(InvoicePaymentBase):
    invoice_id: uuid.UUID

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "invoice_id": "123e4567-e89b-12d3-a456-426614174000",
                "payment_date": "2026-07-15",
                "amount": "25000.00",
                "payment_source": "BANK",
                "payment_status": "SUCCESS",
                "bank_name": "HDFC Bank",
                "transaction_number": "TRX987654321",
                "remarks": "Partial payment for invoice"
            }
        }
    )


class InvoicePaymentUpdate(BaseModel):
    # As per requirements, we might only allow updating remarks or certain fields
    remarks: str | None = None


class InvoicePaymentResponse(InvoicePaymentBase):
    id: uuid.UUID
    receipt_number: str
    invoice_id: uuid.UUID
    
    # Flattened UI fields for list views
    invoice_number: str | None = None
    party_name: str | None = None
    trip_number: str | None = None
    received_by_name: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReceiptResponse(BaseModel):
    """
    Flattened DTO specifically designed for PDF receipt generation or printing.
    """
    receipt_number: str
    invoice_number: str
    trip_number: str
    party_name: str
    gst_number: str | None = None
    pan_number: str | None = None
    mobile_number: str | None = None
    
    payment_date: date
    payment_source: PaymentSource
    amount: Decimal
    balance: Decimal
    
    transaction_number: str | None = None
    cheque_number: str | None = None
    bank_name: str | None = None
    
    collector_name: str | None = None
    remarks: str | None = None

    model_config = ConfigDict(from_attributes=True)


class InvoicePaymentDashboardResponse(BaseModel):
    todays_collection: Decimal = Decimal("0.00")
    monthly_collection: Decimal = Decimal("0.00")
    yearly_collection: Decimal = Decimal("0.00")
    
    pending_receivables: Decimal = Decimal("0.00")
    
    collected_amount: Decimal = Decimal("0.00")
    outstanding_amount: Decimal = Decimal("0.00")
    collection_count: int = 0
    
    payment_source_breakdown: dict[str, Decimal] = Field(default_factory=dict)
