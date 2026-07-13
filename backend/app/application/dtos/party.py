from datetime import datetime
from decimal import Decimal
import uuid
import re
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PartyBase(BaseModel):
    """
    Shared attributes for party operations.
    """
    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: any) -> any:
        if isinstance(data, dict):
            for k, v in list(data.items()):
                if isinstance(v, str):
                    v = v.strip()
                    if k in ["gst_number", "pan_number"]:
                        # Convert taxes identifiers to uppercase
                        v = v.upper()
                    if k == "name":
                        # Consolidate multiple spaces
                        v = re.sub(r"\s+", " ", v)
                    data[k] = v
        return data

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Party full business name.",
    )
    party_type: str = Field(
        ...,
        description="Classification: CUSTOMER, SUPPLIER, BROKER, OTHER.",
    )
    mobile_number: str = Field(
        ...,
        min_length=10,
        max_length=20,
        pattern=r"^\+?[0-9\-\s]+$",
        description="Primary mobile/contact number.",
    )
    alternate_mobile: str | None = Field(
        default=None,
        min_length=10,
        max_length=20,
        pattern=r"^\+?[0-9\-\s]+$",
        description="Backup or alternate contact number.",
    )
    email: str | None = Field(
        default=None,
        max_length=255,
        description="Nullable business contact email.",
    )
    gst_number: str | None = Field(
        default=None,
        min_length=15,
        max_length=15,
        description="Indian 15-character GSTIN number.",
    )
    pan_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=10,
        description="Indian 10-character PAN number.",
    )
    address: str | None = Field(
        default=None,
        description="Physical billing or street address.",
    )
    city: str | None = Field(
        default=None,
        max_length=100,
        description="City.",
    )
    state: str | None = Field(
        default=None,
        max_length=100,
        description="State.",
    )
    pincode: str | None = Field(
        default=None,
        max_length=20,
        description="Postal/ZIP code.",
    )
    contact_person: str | None = Field(
        default=None,
        max_length=100,
        description="Key accounts person name.",
    )
    opening_balance: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
        description="Initial account opening balance.",
    )
    credit_limit: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
        description="Allowed credit limit scale.",
    )
    remarks: str | None = Field(
        default=None,
        max_length=500,
        description="Audit or generic remarks.",
    )

    @field_validator("party_type")
    @classmethod
    def validate_party_type(cls, v: str) -> str:
        normalized = v.strip().upper()
        allowed = ["CUSTOMER", "SUPPLIER", "BROKER", "OTHER"]
        if normalized not in allowed:
            raise ValueError(f"Party type must be one of {allowed}.")
        return normalized

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str | None) -> str | None:
        if v is not None:
            v_cleaned = v.strip()
            # Loose regex check for email
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v_cleaned):
                raise ValueError("Invalid email address format.")
            return v_cleaned
        return v

    @field_validator("gst_number")
    @classmethod
    def validate_gst_format(cls, v: str | None) -> str | None:
        if v is not None:
            # Indian GSTIN check: 2 digits, 5 letters, 4 digits, 1 letter, 1 alpha-numeric/digit, Z, 1 alpha-numeric/digit
            # e.g., 07AAAAA1111A1Z1
            if not re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", v):
                raise ValueError("Invalid Indian GSTIN format.")
        return v

    @field_validator("pan_number")
    @classmethod
    def validate_pan_format(cls, v: str | None) -> str | None:
        if v is not None:
            # Indian PAN check: 5 letters, 4 digits, 1 letter
            if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", v):
                raise ValueError("Invalid Indian PAN format.")
        return v


class PartyCreate(PartyBase):
    """
    Request model for party profile creation.
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Jaipur Quarry Minerals",
                "party_type": "CUSTOMER",
                "mobile_number": "+91 9999900000",
                "alternate_mobile": "+91 9999911111",
                "email": "contact@jaipurminerals.com",
                "gst_number": "08AAAAA1111A1Z2",
                "pan_number": "AAAAA1111A",
                "address": "123 Quarry Road, Jaipur District",
                "city": "Jaipur",
                "state": "Rajasthan",
                "pincode": "302001",
                "contact_person": "Mr. Raj Kumar Sharma",
                "opening_balance": "15000.00",
                "credit_limit": "50000.00",
                "remarks": "Priority accounts customer."
            }
        }
    }


class PartyUpdate(BaseModel):
    """
    Request model for updating an existing party profile (allows partial updates).
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Jaipur Quarry Minerals Ltd",
                "credit_limit": "75000.00",
                "email": "accounts@jaipurminerals.com",
                "remarks": "Credit limit increased by management."
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
                    if k in ["gst_number", "pan_number"]:
                        v = v.upper()
                    if k == "name":
                        v = re.sub(r"\s+", " ", v)
                    data[k] = v
        return data

    name: str | None = Field(default=None, min_length=3, max_length=100)
    party_type: str | None = Field(default=None)
    mobile_number: str | None = Field(default=None, min_length=10, max_length=20, pattern=r"^\+?[0-9\-\s]+$")
    alternate_mobile: str | None = Field(default=None, min_length=10, max_length=20, pattern=r"^\+?[0-9\-\s]+$")
    email: str | None = Field(default=None, max_length=255)
    gst_number: str | None = Field(default=None, min_length=15, max_length=15)
    pan_number: str | None = Field(default=None, min_length=10, max_length=10)
    address: str | None = Field(default=None)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=20)
    contact_person: str | None = Field(default=None, max_length=100)
    opening_balance: Decimal | None = Field(default=None, ge=Decimal("0.00"), max_digits=12, decimal_places=2)
    credit_limit: Decimal | None = Field(default=None, ge=Decimal("0.00"), max_digits=12, decimal_places=2)
    remarks: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None

    @field_validator("party_type")
    @classmethod
    def validate_party_type(cls, v: str | None) -> str | None:
        if v is not None:
            normalized = v.strip().upper()
            allowed = ["CUSTOMER", "SUPPLIER", "BROKER", "OTHER"]
            if normalized not in allowed:
                raise ValueError(f"Party type must be one of {allowed}.")
            return normalized
        return v

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str | None) -> str | None:
        if v is not None:
            v_cleaned = v.strip()
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v_cleaned):
                raise ValueError("Invalid email address format.")
            return v_cleaned
        return v

    @field_validator("gst_number")
    @classmethod
    def validate_gst_format(cls, v: str | None) -> str | None:
        if v is not None:
            if not re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", v):
                raise ValueError("Invalid Indian GSTIN format.")
        return v

    @field_validator("pan_number")
    @classmethod
    def validate_pan_format(cls, v: str | None) -> str | None:
        if v is not None:
            if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", v):
                raise ValueError("Invalid Indian PAN format.")
        return v


class PartyResponse(BaseModel):
    """
    Serialized read response model for Party.
    """
    id: uuid.UUID
    name: str
    party_type: str
    mobile_number: str
    alternate_mobile: str | None = None
    email: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    contact_person: str | None = None
    opening_balance: Decimal
    credit_limit: Decimal
    remarks: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
