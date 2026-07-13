from datetime import date, datetime
from decimal import Decimal
import re
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.enums.trip_status import TripStatus


class TripBase(BaseModel):
    """
    Shared attributes for trip operations.
    """
    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: any) -> any:
        if isinstance(data, dict):
            for k, v in list(data.items()):
                if isinstance(v, str):
                    v = v.strip()
                    if k in ["source_location", "destination_location"]:
                        v = re.sub(r"\s+", " ", v)
                    data[k] = v
        return data

    party_id: uuid.UUID = Field(..., description="Unique ID of the linked Party/Customer.")
    tractor_id: uuid.UUID = Field(..., description="Unique ID of the linked Tractor.")
    driver_id: uuid.UUID = Field(..., description="Unique ID of the linked Driver.")
    source_location: str = Field(..., min_length=2, max_length=100, description="Start/source dispatch location.")
    destination_location: str = Field(..., min_length=2, max_length=100, description="Destination dispatch location.")
    trip_date: date = Field(..., description="Starting trip date.")
    expected_delivery_date: date = Field(..., description="Expected delivery date.")
    freight_amount: Decimal = Field(..., gt=Decimal("0.00"), max_digits=12, decimal_places=2, description="Freight cost (must be > 0).")
    advance_amount: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), max_digits=12, decimal_places=2, description="Paid advance amount.")
    remarks: str | None = Field(default=None, max_length=500, description="Optional remarks.")

    @model_validator(mode="after")
    def validate_amounts_and_dates(self) -> "TripBase":
        # 1. Advance cannot exceed Freight
        if self.advance_amount > self.freight_amount:
            raise ValueError("Advance amount cannot exceed the freight amount.")
        # 2. Expected delivery date cannot be before trip date
        if self.expected_delivery_date < self.trip_date:
            raise ValueError("Expected delivery date cannot be before the trip date.")
        return self


class TripCreate(TripBase):
    """
    Request model for creating a new Trip.
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "party_id": "00000000-0000-0000-0000-000000000000",
                "tractor_id": "00000000-0000-0000-0000-000000000000",
                "driver_id": "00000000-0000-0000-0000-000000000000",
                "source_location": "Jaipur Mines",
                "destination_location": "Delhi Construction Site",
                "trip_date": "2026-07-13",
                "expected_delivery_date": "2026-07-15",
                "freight_amount": "25000.00",
                "advance_amount": "5000.00",
                "remarks": "Urgent stone dispatch load."
            }
        }
    }


class TripUpdate(BaseModel):
    """
    Request model for updating an existing Trip (allows partial updates).
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "expected_delivery_date": "2026-07-16",
                "remarks": "Delivery delayed by weather."
            }
        }
    }

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: any) -> any:
        if isinstance(data, dict):
            for k, v in list(data.items()):
                if isinstance(v, str):
                    v = v.strip()
                    if k in ["source_location", "destination_location"]:
                        v = re.sub(r"\s+", " ", v)
                    data[k] = v
        return data

    party_id: uuid.UUID | None = None
    tractor_id: uuid.UUID | None = None
    driver_id: uuid.UUID | None = None
    source_location: str | None = Field(default=None, min_length=2, max_length=100)
    destination_location: str | None = Field(default=None, min_length=2, max_length=100)
    trip_date: date | None = None
    expected_delivery_date: date | None = None
    actual_delivery_date: date | None = None
    freight_amount: Decimal | None = Field(default=None, gt=Decimal("0.00"))
    advance_amount: Decimal | None = Field(default=None, ge=Decimal("0.00"))
    remarks: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class TripStatusUpdate(BaseModel):
    """
    Request model to update trip workflow status.
    """
    status: TripStatus = Field(..., description="Target TripStatus enum value.")
    remarks: str | None = Field(default=None, max_length=500, description="Audit change remarks.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "DISPATCHED",
                "remarks": "Driver dispatched from loading area."
            }
        }
    }


class TripStatusHistoryResponse(BaseModel):
    """
    Response model for trip status timeline history.
    """
    id: uuid.UUID
    old_status: str | None = None
    new_status: str
    remarks: str | None = None
    created_by: uuid.UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TripResponse(BaseModel):
    """
    Serialized read response model for a Trip.
    """
    id: uuid.UUID
    trip_number: str
    party_id: uuid.UUID
    tractor_id: uuid.UUID
    driver_id: uuid.UUID
    source_location: str
    destination_location: str
    trip_date: date
    expected_delivery_date: date
    actual_delivery_date: date | None = None
    freight_amount: Decimal
    advance_amount: Decimal
    remarks: str | None = None
    status: TripStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Computed fields
    driver_name: str | None = None
    tractor_number: str | None = None
    party_name: str | None = None
    trip_age: int | None = None
    status_label: str | None = None
    total_expense: Decimal | None = None
    net_profit: Decimal | None = None
    total_advances: Decimal | None = None
    expense_count: int | None = None

    model_config = ConfigDict(from_attributes=True)
