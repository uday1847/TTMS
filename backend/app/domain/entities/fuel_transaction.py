import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List
from sqlalchemy import String, ForeignKey, Numeric, Integer, Date, Boolean, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.fuel_type import FuelType
from app.domain.enums.fuel_payment_mode import FuelPaymentMode
from app.domain.enums.fuel_station_type import FuelStationType
from app.domain.enums.fuel_transaction_status import FuelTransactionStatus

if TYPE_CHECKING:
    from app.domain.entities.tractor import Tractor
    from app.domain.entities.trip import Trip
    from app.domain.entities.driver import Driver
    from app.domain.entities.fuel_vendor import FuelVendor
    from app.domain.entities.fuel_history import FuelHistory


class FuelTransaction(BaseEntity):
    __tablename__ = "fuel_transactions"

    fuel_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    tractor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tractors.id"), index=True)
    trip_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id"), index=True)
    driver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("drivers.id"), index=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fuel_vendors.id"), index=True)
    
    station_type: Mapped[FuelStationType] = mapped_column(SQLEnum(FuelStationType, name="fuel_station_type_enum", native_enum=True))
    fuel_type: Mapped[FuelType] = mapped_column(SQLEnum(FuelType, name="fuel_type_enum", native_enum=True))
    fuel_date: Mapped[date] = mapped_column(Date, index=True)
    
    odometer: Mapped[int] = mapped_column(Integer)
    liters: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    rate_per_liter: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    previous_odometer: Mapped[int | None] = mapped_column(Integer)
    distance_since_last_fill: Mapped[int | None] = mapped_column(Integer)
    average_kmpl: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    
    payment_mode: Mapped[FuelPaymentMode] = mapped_column(SQLEnum(FuelPaymentMode, name="fuel_payment_mode_enum", native_enum=True))
    invoice_number: Mapped[str | None] = mapped_column(String(100), index=True)
    remarks: Mapped[str | None] = mapped_column(String(1000))
    attachment: Mapped[str | None] = mapped_column(String(500))
    
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    is_full_tank: Mapped[bool] = mapped_column(Boolean, default=False)
    
    fuel_card_number: Mapped[str | None] = mapped_column(String(100))
    authorization_code: Mapped[str | None] = mapped_column(String(100))
    transaction_reference: Mapped[str | None] = mapped_column(String(255))
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    
    status: Mapped[FuelTransactionStatus] = mapped_column(SQLEnum(FuelTransactionStatus, name="fuel_transaction_status_enum", native_enum=True), default=FuelTransactionStatus.DRAFT)
    
    gps_latitude: Mapped[float | None] = mapped_column(Float)
    gps_longitude: Mapped[float | None] = mapped_column(Float)
    gps_accuracy: Mapped[float | None] = mapped_column(Float)
    device_id: Mapped[str | None] = mapped_column(String(100))
    location_address: Mapped[str | None] = mapped_column(String(500))

    # Relationships
    tractor: Mapped["Tractor"] = relationship("Tractor", back_populates="fuel_transactions")
    trip: Mapped["Trip"] = relationship("Trip", back_populates="fuel_transactions")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="fuel_transactions")
    vendor: Mapped["FuelVendor"] = relationship("FuelVendor", back_populates="fuel_transactions")
    histories: Mapped[List["FuelHistory"]] = relationship("FuelHistory", back_populates="fuel_transaction", cascade="all, delete-orphan")
