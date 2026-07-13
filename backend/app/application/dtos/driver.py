from datetime import date, datetime
from decimal import Decimal
import uuid
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.enums.driver_status import DriverStatus


class DriverBase(BaseModel):
    """
    Shared attributes for driver operations.
    """
    user_id: uuid.UUID | None = Field(default=None, description="Optional system login account linkage.")
    employee_code: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Z0-9_\-]+$",
        description="Unique business identifier code for driver (Uppercase, numbers, hyphens, underscores).",
    )
    license_number: str = Field(
        min_length=5,
        max_length=50,
        description="Driver driving license identifier.",
    )
    license_expiry: date = Field(description="Expiration date of driving license.")
    license_class: str = Field(
        min_length=1,
        max_length=30,
        description="Classification of driving license (e.g. Heavy Duty, LMV).",
    )
    contact_phone: str = Field(
        min_length=10,
        max_length=30,
        pattern=r"^\+?[0-9\-\s]+$",
        description="Primary contact number.",
    )
    emergency_contact_phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=30,
        pattern=r"^\+?[0-9\-\s]+$",
        description="Emergency backup contact number.",
    )
    fixed_salary: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
        description="Standard monthly salary base (if salaried).",
    )
    commission_percentage: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        le=Decimal("100.00"),
        max_digits=5,
        decimal_places=2,
        description="Commission payout scale per trip.",
    )
    driver_type: str = Field(
        min_length=3,
        max_length=20,
        description="Employment categorization (e.g., 'SALARIED', 'COMMISSION_BASED', 'CONTRACT').",
    )
    current_status: DriverStatus = Field(
        default=DriverStatus.AVAILABLE,
        description="Operational availability.",
    )


class DriverCreate(DriverBase):
    """
    Request model for driver creation.
    """

    @field_validator("license_expiry")
    @classmethod
    def validate_license_expiry(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Driver license has already expired.")
        return v

    @model_validator(mode="after")
    def validate_phones(self) -> Self:
        if self.contact_phone == self.emergency_contact_phone:
            raise ValueError("Emergency contact phone cannot be the same as primary contact phone.")
        return self


class DriverUpdate(BaseModel):
    """
    Request model for driver update (allows partial updates).
    """
    user_id: uuid.UUID | None = None
    employee_code: str | None = Field(default=None, min_length=3, max_length=50, pattern=r"^[A-Z0-9_\-]+$")
    license_number: str | None = Field(default=None, min_length=5, max_length=50)
    license_expiry: date | None = None
    license_class: str | None = Field(default=None, min_length=1, max_length=30)
    contact_phone: str | None = Field(default=None, min_length=10, max_length=30, pattern=r"^\+?[0-9\-\s]+$")
    emergency_contact_phone: str | None = Field(default=None, min_length=10, max_length=30, pattern=r"^\+?[0-9\-\s]+$")
    fixed_salary: Decimal | None = Field(default=None, ge=Decimal("0.00"), max_digits=12, decimal_places=2)
    commission_percentage: Decimal | None = Field(default=None, ge=Decimal("0.00"), le=Decimal("100.00"), max_digits=5, decimal_places=2)
    driver_type: str | None = Field(default=None, min_length=3, max_length=20)
    current_status: DriverStatus | None = None
    is_active: bool | None = None

    @field_validator("license_expiry")
    @classmethod
    def validate_license_expiry(cls, v: date | None) -> date | None:
        if v is not None and v < date.today():
            raise ValueError("Driver license has already expired.")
        return v

    @model_validator(mode="after")
    def validate_phones(self) -> Self:
        if self.contact_phone is not None and self.emergency_contact_phone is not None:
            if self.contact_phone == self.emergency_contact_phone:
                raise ValueError("Emergency contact phone cannot be the same as primary contact phone.")
        return self


class DriverResponse(DriverBase):
    """
    Response model returning driver records.
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None
    is_active: bool
    version_id: int

    model_config = {
        "from_attributes": True,
    }


class DriverListResponse(BaseModel):
    """
    Paginated driver response list wrapper.
    """
    items: list[DriverResponse]
    total: int
    page: int
    size: int
