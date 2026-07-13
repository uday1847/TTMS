from datetime import date
from decimal import Decimal
import uuid
from typing import Any

from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode
from app.domain.enums.payment_status import PaymentStatus
from app.application.dtos.trip import TripStatusHistoryResponse


class TripExpenseBase(BaseModel):
    """
    Base DTO schema with validation for Trip Expenses.
    """
    trip_id: uuid.UUID
    party_id: uuid.UUID | None = Field(default=None, description="Linked vendor/supplier party record")
    paid_to_name: str | None = Field(default=None, max_length=100, description="Manual text record of who was paid")
    expense_type: ExpenseType
    expense_date: date
    amount: Decimal = Field(gt=0, decimal_places=2, description="Expense amount (must be positive)")
    payment_mode: PaymentMode
    payment_status: PaymentStatus = Field(default=PaymentStatus.PAID, description="PAID, UNPAID, or PARTIAL")
    reference_number: str | None = Field(default=None, max_length=100, description="Transaction transaction reference ID")
    remarks: str | None = Field(default=None, max_length=500, description="Optional description/remarks")
    
    # Attachment metadata
    attachment_path: str | None = Field(default=None, max_length=500, description="File path to uploaded file")
    attachment_name: str | None = Field(default=None, max_length=255, description="Filename of attachment")
    attachment_size: int | None = Field(default=None, ge=0, description="Size in bytes")
    attachment_content_type: str | None = Field(default=None, max_length=100, description="MIME content type")

    @field_validator(
        "paid_to_name", "reference_number", "remarks", 
        "attachment_path", "attachment_name", "attachment_content_type", 
        mode="before"
    )
    @classmethod
    def trim_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            trimmed = v.strip()
            return trimmed if trimmed else None
        return v


class TripExpenseCreate(TripExpenseBase):
    """
    Schema for creating a new Trip Expense.
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "trip_id": "82a5220e-5ece-4115-9b9d-4e38dbfba67c",
                "party_id": "f1743f41-5ece-4115-9b9d-4e38dbfba67c",
                "paid_to_name": "HP Petrol Pump",
                "expense_type": "DIESEL",
                "expense_date": "2026-07-13",
                "amount": 7500.00,
                "payment_mode": "UPI",
                "payment_status": "PAID",
                "reference_number": "TXN987654321",
                "remarks": "Diesel for initial trip segment",
                "attachment_path": "/uploads/expenses/hp_bill.jpg",
                "attachment_name": "hp_bill.jpg",
                "attachment_size": 102400,
                "attachment_content_type": "image/jpeg"
            }
        }
    }


class TripExpenseUpdate(BaseModel):
    """
    Schema for updating an existing Trip Expense. All fields are optional.
    """
    party_id: uuid.UUID | None = None
    paid_to_name: str | None = None
    expense_type: ExpenseType | None = None
    expense_date: date | None = None
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    payment_mode: PaymentMode | None = None
    payment_status: PaymentStatus | None = None
    reference_number: str | None = None
    remarks: str | None = None
    attachment_path: str | None = None
    attachment_name: str | None = None
    attachment_size: int | None = None
    attachment_content_type: str | None = None

    @field_validator(
        "paid_to_name", "reference_number", "remarks", 
        "attachment_path", "attachment_name", "attachment_content_type", 
        mode="before"
    )
    @classmethod
    def trim_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            trimmed = v.strip()
            return trimmed if trimmed else None
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 8000.00,
                "remarks": "Diesel amount revised",
                "payment_status": "PAID"
            }
        }
    }


class TripExpenseResponse(TripExpenseBase):
    """
    Read representation schema for Trip Expense.
    """
    id: uuid.UUID
    expense_number: str
    created_at: Any
    updated_at: Any
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    is_active: bool
    version_id: int

    model_config = ConfigDict(from_attributes=True)


class ExpenseBreakdownItem(BaseModel):
    """
    Single item representation of expense breakdown grouped by type.
    """
    type: str
    amount: Decimal


class TripExpenseSummaryResponse(BaseModel):
    """
    Aggregated operational expense metrics for a specific Trip.
    """
    trip_number: str
    freight: Decimal
    advance: Decimal
    expenses: Decimal
    profit: Decimal
    expense_count: int
    expense_breakdown: list[ExpenseBreakdownItem]


class TripDashboardResponse(BaseModel):
    """
    Full contextual aggregation for React frontend rendering.
    """
    trip_number: str
    status: str
    driver_name: str | None = None
    tractor_number: str | None = None
    party_name: str | None = None
    freight: Decimal
    advance: Decimal
    remaining_freight: Decimal
    expenses: Decimal
    profit: Decimal
    remaining_profit: Decimal
    expense_count: int
    expenses_list: list[TripExpenseResponse]
    timeline: list[TripStatusHistoryResponse]
