from datetime import date, datetime
from decimal import Decimal
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.enums.invoice_status import InvoiceStatus


class InvoiceBase(BaseModel):
    invoice_date: date
    due_date: date
    remarks: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_dates(self) -> "InvoiceBase":
        if self.due_date < self.invoice_date:
            raise ValueError("due_date must be greater than or equal to invoice_date")
        return self

    @field_validator("remarks", mode="before")
    @classmethod
    def trim_remarks(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v


class InvoiceCreate(InvoiceBase):
    trip_id: uuid.UUID


class InvoiceUpdate(BaseModel):
    invoice_date: date | None = None
    due_date: date | None = None
    remarks: str | None = Field(default=None, max_length=500)

    @field_validator("remarks", mode="before")
    @classmethod
    def trim_remarks(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v


class InvoiceStatusUpdate(BaseModel):
    status: InvoiceStatus
    remarks: str | None = Field(default=None, max_length=500)

    @field_validator("remarks", mode="before")
    @classmethod
    def trim_remarks(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    invoice_number: str
    trip_id: uuid.UUID
    party_id: uuid.UUID
    invoice_date: date
    due_date: date
    gross_amount: Decimal
    received_amount: Decimal
    balance_amount: Decimal
    remarks: str | None
    status: InvoiceStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Computed fields for rich frontend context
    trip_number: str | None = None
    party_name: str | None = None
    party_mobile: str | None = None
    driver_name: str | None = None
    tractor_number: str | None = None
    trip_date: date | None = None
    due_days: int = 0
    is_overdue: bool = False
    payment_percentage: Decimal = Decimal("0.00")
    status_label: str = ""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "c3b07e82-2775-4c07-94d3-820de0d01d4a",
                "invoice_number": "INV-2026-000001",
                "trip_id": "8c257321-4f11-4770-9844-325d0c0d1d4a",
                "party_id": "5fa232b2-65a8-4220-91a5-81230c0d1d4a",
                "invoice_date": "2026-07-13",
                "due_date": "2026-07-28",
                "gross_amount": "50000.00",
                "received_amount": "15000.00",
                "balance_amount": "35000.00",
                "remarks": "Initial segment invoice",
                "status": "PARTIALLY_PAID",
                "is_active": True,
                "created_at": "2026-07-13T16:00:00Z",
                "updated_at": "2026-07-13T16:30:00Z",
                "trip_number": "TRIP-2026-000001",
                "party_name": "Indian Oil Corp Ltd",
                "party_mobile": "9998887776",
                "driver_name": "Ramesh Kumar",
                "tractor_number": "GJ-01-XX-1234",
                "trip_date": "2026-07-10",
                "due_days": 15,
                "is_overdue": False,
                "payment_percentage": "30.00",
                "status_label": "Partially Paid"
            }
        }
    )


class InvoiceStatusHistoryResponse(BaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    old_status: str | None
    new_status: str
    remarks: str | None
    changed_by: uuid.UUID | None
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceSummaryResponse(BaseModel):
    total_invoices: int
    total_revenue: Decimal
    total_collected: Decimal
    total_outstanding: Decimal

    model_config = ConfigDict(from_attributes=True)


class InvoiceFinancialPeriodMetrics(BaseModel):
    revenue: Decimal
    collection: Decimal
    outstanding: Decimal


class InvoiceDashboardResponse(BaseModel):
    total_invoices: int
    draft_count: int
    issued_count: int
    partially_paid_count: int
    paid_count: int
    cancelled_count: int
    total_revenue: Decimal
    total_collected: Decimal
    total_outstanding: Decimal
    overdue_count: int

    monthly_analytics: InvoiceFinancialPeriodMetrics
    yearly_analytics: InvoiceFinancialPeriodMetrics

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "total_invoices": 120,
                "draft_count": 10,
                "issued_count": 30,
                "partially_paid_count": 20,
                "paid_count": 50,
                "cancelled_count": 10,
                "total_revenue": "1200000.00",
                "total_collected": "900000.00",
                "total_outstanding": "300000.00",
                "overdue_count": 15,
                "monthly_analytics": {
                    "revenue": "150000.00",
                    "collection": "120000.00",
                    "outstanding": "30000.00"
                },
                "yearly_analytics": {
                    "revenue": "1200000.00",
                    "collection": "900000.00",
                    "outstanding": "300000.00"
                }
            }
        }
    )
