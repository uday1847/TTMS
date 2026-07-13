from datetime import date, datetime
import uuid
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TractorBase(BaseModel):
    """
    Shared attributes for tractor operations.
    """
    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: any) -> any:
        if isinstance(data, dict):
            for k, v in list(data.items()):
                if isinstance(v, str):
                    v = v.strip()
                    if k in ["tractor_number", "rc_number"]:
                        # Convert lookups to uppercase
                        v = v.upper()
                    if k == "owner_name":
                        import re
                        v = re.sub(r"\s+", " ", v)
                    data[k] = v
        return data

    tractor_number: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Unique registration license/tractor plate number.",
    )
    owner_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the tractor asset owner/firm.",
    )
    rc_number: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Unique Registration Certificate book number.",
    )
    insurance_number: str | None = Field(
        default=None,
        max_length=100,
        description="Tractor active insurance policy code.",
    )
    insurance_expiry: date = Field(
        ...,
        description="Expiry date of active insurance policy.",
    )
    manufacturer: str | None = Field(
        default=None,
        max_length=50,
        description="Tractor brand/manufacturer.",
    )
    model: str | None = Field(
        default=None,
        max_length=50,
        description="Tractor specification model name.",
    )
    registration_date: date | None = Field(
        default=None,
        description="Asset database/government registration date.",
    )
    remarks: str | None = Field(
        default=None,
        max_length=500,
        description="Nullable audit or general remarks.",
    )


class TractorCreate(TractorBase):
    """
    Request model for tractor creation.
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "tractor_number": "RJ-14-1234",
                "owner_name": "Jaipur Logistics Ltd",
                "rc_number": "RC-JAIPUR-888999",
                "insurance_number": "INS-TR-990011",
                "insurance_expiry": "2027-12-31",
                "manufacturer": "Mahindra & Mahindra",
                "model": "Arjun 555 DI",
                "registration_date": "2024-01-15",
                "remarks": "Assigned to quarry operations.",
            }
        }
    }

    @field_validator("insurance_expiry")
    @classmethod
    def validate_insurance_expiry(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Tractor insurance has already expired.")
        return v


class TractorUpdate(BaseModel):
    """
    Request model for tractor updates (allows partial updates).
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "owner_name": "Jaipur Logistics Services",
                "insurance_number": "INS-TR-990011-REV2",
                "insurance_expiry": "2028-12-31",
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
                    if k in ["tractor_number", "rc_number"]:
                        v = v.upper()
                    if k == "owner_name":
                        import re
                        v = re.sub(r"\s+", " ", v)
                    data[k] = v
        return data

    tractor_number: str | None = Field(default=None, min_length=3, max_length=30)
    owner_name: str | None = Field(default=None, min_length=2, max_length=100)
    rc_number: str | None = Field(default=None, min_length=5, max_length=50)
    insurance_number: str | None = Field(default=None, max_length=100)
    insurance_expiry: date | None = Field(default=None)
    manufacturer: str | None = Field(default=None, max_length=50)
    model: str | None = Field(default=None, max_length=50)
    registration_date: date | None = Field(default=None)
    remarks: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None

    @field_validator("insurance_expiry")
    @classmethod
    def validate_insurance_expiry(cls, v: date | None) -> date | None:
        if v is not None and v < date.today():
            raise ValueError("Tractor insurance has already expired.")
        return v


class TractorResponse(BaseModel):
    """
    Serialized read response model for Tractor.
    """
    id: uuid.UUID
    tractor_number: str
    owner_name: str
    rc_number: str
    insurance_number: str | None = None
    insurance_expiry: date
    manufacturer: str | None = None
    model: str | None = None
    registration_date: date | None = None
    remarks: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
