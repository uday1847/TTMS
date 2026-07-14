import uuid
from datetime import datetime, date, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FuelVendorBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    vendor_code: str = Field(..., min_length=2, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=255)
    mobile: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    gst_number: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    is_company_owned: bool = False
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True


class FuelVendorCreate(FuelVendorBase):
    pass


class FuelVendorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    vendor_code: Optional[str] = Field(None, min_length=2, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=255)
    mobile: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    gst_number: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    is_company_owned: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class FuelVendorResponse(FuelVendorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
