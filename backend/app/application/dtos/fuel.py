import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.fuel_type import FuelType
from app.domain.enums.fuel_payment_mode import FuelPaymentMode
from app.domain.enums.fuel_station_type import FuelStationType
from app.domain.enums.fuel_transaction_status import FuelTransactionStatus


class FuelTransactionBase(BaseModel):
    tractor_id: uuid.UUID
    trip_id: Optional[uuid.UUID] = None
    driver_id: uuid.UUID
    vendor_id: uuid.UUID
    
    station_type: FuelStationType
    fuel_type: FuelType
    fuel_date: date
    
    odometer: int = Field(..., gt=0)
    liters: Decimal = Field(..., gt=0)
    rate_per_liter: Decimal = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    
    payment_mode: FuelPaymentMode
    invoice_number: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = Field(None, max_length=1000)
    attachment: Optional[str] = Field(None, max_length=500)
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_full_tank: bool = False
    
    fuel_card_number: Optional[str] = Field(None, max_length=100)
    authorization_code: Optional[str] = Field(None, max_length=100)
    transaction_reference: Optional[str] = Field(None, max_length=255)
    
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_accuracy: Optional[float] = None
    device_id: Optional[str] = Field(None, max_length=100)
    location_address: Optional[str] = Field(None, max_length=500)


class FuelTransactionCreate(FuelTransactionBase):
    pass


class FuelTransactionUpdate(BaseModel):
    tractor_id: Optional[uuid.UUID] = None
    trip_id: Optional[uuid.UUID] = None
    driver_id: Optional[uuid.UUID] = None
    vendor_id: Optional[uuid.UUID] = None
    
    station_type: Optional[FuelStationType] = None
    fuel_type: Optional[FuelType] = None
    fuel_date: Optional[date] = None
    
    odometer: Optional[int] = Field(None, gt=0)
    liters: Optional[Decimal] = Field(None, gt=0)
    rate_per_liter: Optional[Decimal] = Field(None, gt=0)
    amount: Optional[Decimal] = Field(None, gt=0)
    
    payment_mode: Optional[FuelPaymentMode] = None
    invoice_number: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = Field(None, max_length=1000)
    attachment: Optional[str] = Field(None, max_length=500)
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_full_tank: Optional[bool] = None
    
    fuel_card_number: Optional[str] = Field(None, max_length=100)
    authorization_code: Optional[str] = Field(None, max_length=100)
    transaction_reference: Optional[str] = Field(None, max_length=255)
    
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_accuracy: Optional[float] = None
    device_id: Optional[str] = Field(None, max_length=100)
    location_address: Optional[str] = Field(None, max_length=500)
    
    update_reason: str = Field(..., min_length=5, description="Reason for updating fuel transaction")


class FuelHistoryResponse(BaseModel):
    id: uuid.UUID
    fuel_transaction_id: uuid.UUID
    
    old_amount: Optional[Decimal] = None
    new_amount: Optional[Decimal] = None
    old_odometer: Optional[int] = None
    new_odometer: Optional[int] = None
    old_vendor_id: Optional[uuid.UUID] = None
    new_vendor_id: Optional[uuid.UUID] = None
    old_status: Optional[FuelTransactionStatus] = None
    new_status: Optional[FuelTransactionStatus] = None
    
    reason: str
    edited_by: uuid.UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class FuelTransactionResponse(FuelTransactionBase):
    id: uuid.UUID
    fuel_number: str
    
    previous_odometer: Optional[int] = None
    distance_since_last_fill: Optional[int] = None
    average_kmpl: Optional[Decimal] = None
    is_suspicious: bool
    status: FuelTransactionStatus
    
    created_at: datetime
    updated_at: datetime
    
    # Optional resolved fields (populated by service/orchestrator)
    tractor_number: Optional[str] = None
    driver_name: Optional[str] = None
    vendor_name: Optional[str] = None
    trip_number: Optional[str] = None
    
    histories: List[FuelHistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)
