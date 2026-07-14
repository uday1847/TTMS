from datetime import date, datetime
import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.enums.maintenance_status import MaintenanceStatus
from app.domain.enums.maintenance_type import MaintenanceType
from app.domain.enums.maintenance_priority import MaintenancePriority


class MaintenanceBase(BaseModel):
    """
    Shared attributes for maintenance records.
    """
    vendor_name: Optional[str] = Field(None, max_length=100)
    vendor_mobile: Optional[str] = Field(None, max_length=15)
    service_center: Optional[str] = Field(None, max_length=150)
    invoice_number: Optional[str] = Field(None, max_length=100)
    
    scheduled_date: date
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    next_service_date: Optional[date] = None
    
    current_odometer: int = Field(..., ge=0)
    next_service_odometer: Optional[int] = None
    
    parts_cost: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), decimal_places=2)
    labor_cost: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), decimal_places=2)
    other_cost: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), decimal_places=2)
    
    remarks: Optional[str] = Field(None, max_length=500)
    attachment: Optional[str] = Field(None, max_length=255)

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: any) -> any:
        if isinstance(data, dict):
            for k, v in list(data.items()):
                if isinstance(v, str):
                    v = v.strip()
                    if k in ["vendor_name", "service_center", "invoice_number"]:
                        import re
                        v = re.sub(r"\s+", " ", v)
                    data[k] = v
        return data

    @model_validator(mode="after")
    def validate_dates(self) -> "MaintenanceBase":
        if self.next_service_date and self.scheduled_date > self.next_service_date:
            raise ValueError("scheduled_date cannot be after next_service_date")
        if self.start_date and self.start_date < self.scheduled_date:
            raise ValueError("start_date cannot be before scheduled_date")
        if self.completion_date and self.start_date and self.completion_date < self.start_date:
            raise ValueError("completion_date cannot be before start_date")
        return self
        
    @model_validator(mode="after")
    def validate_odometer(self) -> "MaintenanceBase":
        if self.next_service_odometer is not None and self.next_service_odometer <= self.current_odometer:
            raise ValueError("next_service_odometer must be greater than current_odometer")
        return self


class MaintenanceCreate(MaintenanceBase):
    tractor_id: uuid.UUID
    maintenance_type: MaintenanceType
    priority: MaintenancePriority
    
    # We explicitly exclude total_cost from create/update as it must be auto-calculated
    # Also exclude status, as it defaults to SCHEDULED


class MaintenanceUpdate(BaseModel):
    vendor_name: Optional[str] = Field(None, max_length=100)
    vendor_mobile: Optional[str] = Field(None, max_length=15)
    service_center: Optional[str] = Field(None, max_length=150)
    invoice_number: Optional[str] = Field(None, max_length=100)
    
    scheduled_date: Optional[date] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    next_service_date: Optional[date] = None
    
    current_odometer: Optional[int] = Field(None, ge=0)
    next_service_odometer: Optional[int] = None
    
    parts_cost: Optional[Decimal] = Field(None, ge=Decimal("0.00"), decimal_places=2)
    labor_cost: Optional[Decimal] = Field(None, ge=Decimal("0.00"), decimal_places=2)
    other_cost: Optional[Decimal] = Field(None, ge=Decimal("0.00"), decimal_places=2)
    
    remarks: Optional[str] = Field(None, max_length=500)
    attachment: Optional[str] = Field(None, max_length=255)


class MaintenanceStatusUpdate(BaseModel):
    status: MaintenanceStatus
    remarks: Optional[str] = Field(None, max_length=500)


class MaintenanceResponse(MaintenanceBase):
    id: uuid.UUID
    maintenance_number: str
    tractor_id: uuid.UUID
    maintenance_type: MaintenanceType
    priority: MaintenancePriority
    status: MaintenanceStatus
    
    total_cost: Decimal
    
    # Derived from Tractor relationship
    tractor_number: str
    tractor_model: Optional[str] = None
    
    # Computed property
    days_remaining: Optional[int] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaintenanceHistoryResponse(BaseModel):
    id: uuid.UUID
    maintenance_id: uuid.UUID
    old_status: Optional[str]
    new_status: Optional[str]
    old_vendor_name: Optional[str]
    new_vendor_name: Optional[str]
    old_total_cost: Optional[Decimal]
    new_total_cost: Optional[Decimal]
    old_odometer: Optional[int]
    new_odometer: Optional[int]
    remarks: Optional[str]
    changed_by: Optional[uuid.UUID]
    created_at: datetime
    
    # Derived
    changed_by_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaintenanceDashboardResponse(BaseModel):
    scheduled_count: int
    in_progress_count: int
    completed_count: int
    cancelled_count: int
    
    total_cost: Decimal
    current_month_cost: Decimal
    current_year_cost: Decimal
    average_cost: Decimal
    
    upcoming_service_count: int
    overdue_service_count: int
    
    highest_cost_repair: Optional[Decimal]
    average_cost_by_tractor: Optional[Decimal]
    
    cost_by_maintenance_type: dict[str, Decimal]
    priority_distribution: dict[str, int]
    monthly_trend: list[dict] # e.g. [{"month": "2026-01", "cost": 1500.00}]
