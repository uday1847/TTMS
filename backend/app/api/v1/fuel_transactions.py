import uuid
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status, Body

from app.api.dependencies.db import get_session
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.application.dtos.fuel import FuelTransactionCreate, FuelTransactionUpdate, FuelTransactionResponse
from app.application.services.fuel_service import FuelService
from app.application.services.fuel_analytics_service import FuelAnalyticsService
from app.infrastructure.repositories.fuel_repository import SQLAlchemyFuelRepository
from app.infrastructure.repositories.fuel_vendor_repository import SQLAlchemyFuelVendorRepository
from app.infrastructure.repositories.tractor_repository import SQLAlchemyTractorRepository
from app.infrastructure.repositories.driver_repository import SQLAlchemyDriverRepository
from app.infrastructure.repositories.trip_repository import SQLAlchemyTripRepository
from app.infrastructure.repositories.trip_expense_repository import SQLAlchemyTripExpenseRepository
from app.domain.enums.fuel_transaction_status import FuelTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/fuel-transactions", tags=["Fuel Transactions"])

def get_fuel_service(session: AsyncSession = Depends(get_session)) -> FuelService:
    return FuelService(
        repository=SQLAlchemyFuelRepository(session),
        vendor_repository=SQLAlchemyFuelVendorRepository(session),
        tractor_repository=SQLAlchemyTractorRepository(session),
        driver_repository=SQLAlchemyDriverRepository(session),
        trip_repository=SQLAlchemyTripRepository(session),
        expense_repository=SQLAlchemyTripExpenseRepository(session),
        session=session
    )

def get_fuel_analytics_service(session: AsyncSession = Depends(get_session)) -> FuelAnalyticsService:
    return FuelAnalyticsService(session)

@router.post(
    "",
    response_model=FuelTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("fuel:create"))]
)
async def create_fuel_transaction(
    data: FuelTransactionCreate,
    current_user: dict = Depends(get_current_active_user),
    service: FuelService = Depends(get_fuel_service)
):
    return await service.create_transaction(data, created_by=uuid.UUID(current_user["id"]))

@router.get(
    "",
    response_model=List[FuelTransactionResponse],
    dependencies=[Depends(PermissionChecker("fuel:read"))]
)
async def list_fuel_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tractor_id: Optional[uuid.UUID] = Query(None),
    trip_id: Optional[uuid.UUID] = Query(None),
    vendor_id: Optional[uuid.UUID] = Query(None),
    status: Optional[FuelTransactionStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: FuelService = Depends(get_fuel_service)
):
    return await service.get_transactions(skip, limit, tractor_id, trip_id, vendor_id, status, start_date, end_date)

@router.get(
    "/{transaction_id}",
    response_model=FuelTransactionResponse,
    dependencies=[Depends(PermissionChecker("fuel:read"))]
)
async def get_fuel_transaction(
    transaction_id: uuid.UUID = Path(...),
    service: FuelService = Depends(get_fuel_service)
):
    return await service.get_transaction(transaction_id)

@router.put(
    "/{transaction_id}",
    response_model=FuelTransactionResponse,
    dependencies=[Depends(PermissionChecker("fuel:update"))]
)
async def update_fuel_transaction(
    data: FuelTransactionUpdate,
    transaction_id: uuid.UUID = Path(...),
    current_user: dict = Depends(get_current_active_user),
    service: FuelService = Depends(get_fuel_service)
):
    return await service.update_transaction(transaction_id, data, updated_by=uuid.UUID(current_user["id"]))

@router.patch(
    "/{transaction_id}/status",
    response_model=FuelTransactionResponse,
    dependencies=[Depends(PermissionChecker("fuel:update"))]
)
async def update_fuel_status(
    transaction_id: uuid.UUID = Path(...),
    new_status: FuelTransactionStatus = Body(..., embed=True),
    reason: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_active_user),
    service: FuelService = Depends(get_fuel_service)
):
    return await service.change_status(transaction_id, new_status, updated_by=uuid.UUID(current_user["id"]), reason=reason)

@router.get(
    "/analytics/tractor/{tractor_id}",
    dependencies=[Depends(PermissionChecker("fuel:read"))]
)
async def get_tractor_fuel_analytics(
    tractor_id: uuid.UUID = Path(...),
    analytics_service: FuelAnalyticsService = Depends(get_fuel_analytics_service)
):
    return await analytics_service.calculate_tractor_stats(str(tractor_id))

@router.get(
    "/analytics/trip/{trip_id}",
    dependencies=[Depends(PermissionChecker("fuel:read"))]
)
async def get_trip_fuel_analytics(
    trip_id: uuid.UUID = Path(...),
    analytics_service: FuelAnalyticsService = Depends(get_fuel_analytics_service)
):
    return await analytics_service.calculate_trip_stats(str(trip_id))
