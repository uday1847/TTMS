import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status

from app.api.dependencies.db import get_session
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.application.dtos.fuel_vendor import FuelVendorCreate, FuelVendorUpdate, FuelVendorResponse
from app.application.services.fuel_vendor_service import FuelVendorService
from app.infrastructure.repositories.fuel_vendor_repository import SQLAlchemyFuelVendorRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/fuel-vendors", tags=["Fuel Vendors"])

def get_fuel_vendor_service(session: AsyncSession = Depends(get_session)) -> FuelVendorService:
    repository = SQLAlchemyFuelVendorRepository(session)
    return FuelVendorService(repository)

@router.post(
    "",
    response_model=FuelVendorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("fuel:create"))]
)
async def create_fuel_vendor(
    data: FuelVendorCreate,
    current_user: dict = Depends(get_current_active_user),
    service: FuelVendorService = Depends(get_fuel_vendor_service)
):
    return await service.create_vendor(data, created_by=uuid.UUID(current_user["id"]))

@router.get(
    "",
    response_model=List[FuelVendorResponse],
    dependencies=[Depends(PermissionChecker("fuel:read"))]
)
async def list_fuel_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    service: FuelVendorService = Depends(get_fuel_vendor_service)
):
    return await service.get_vendors(skip=skip, limit=limit, is_active=is_active, search=search)

@router.get(
    "/{vendor_id}",
    response_model=FuelVendorResponse,
    dependencies=[Depends(PermissionChecker("fuel:read"))]
)
async def get_fuel_vendor(
    vendor_id: uuid.UUID = Path(...),
    service: FuelVendorService = Depends(get_fuel_vendor_service)
):
    return await service.get_vendor(vendor_id)

@router.put(
    "/{vendor_id}",
    response_model=FuelVendorResponse,
    dependencies=[Depends(PermissionChecker("fuel:update"))]
)
async def update_fuel_vendor(
    data: FuelVendorUpdate,
    vendor_id: uuid.UUID = Path(...),
    current_user: dict = Depends(get_current_active_user),
    service: FuelVendorService = Depends(get_fuel_vendor_service)
):
    return await service.update_vendor(vendor_id, data, updated_by=uuid.UUID(current_user["id"]))

@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker("fuel:delete"))]
)
async def delete_fuel_vendor(
    vendor_id: uuid.UUID = Path(...),
    current_user: dict = Depends(get_current_active_user),
    service: FuelVendorService = Depends(get_fuel_vendor_service)
):
    await service.delete_vendor(vendor_id, deleted_by=uuid.UUID(current_user["id"]))
