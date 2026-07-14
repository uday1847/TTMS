import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.api.dependencies.db import get_session
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceStatusUpdate,
    MaintenanceResponse,
    MaintenanceDashboardResponse,
    MaintenanceHistoryResponse,
)
from app.application.services.maintenance_service import MaintenanceService
from app.domain.entities.user import User
from app.domain.enums.maintenance_status import MaintenanceStatus
from app.domain.enums.maintenance_priority import MaintenancePriority
from app.domain.enums.maintenance_type import MaintenanceType
from app.infrastructure.repositories.maintenance_repository import SQLAlchemyMaintenanceRepository
from app.infrastructure.repositories.tractor_repository import SQLAlchemyTractorRepository
from app.infrastructure.database.session import AsyncSessionLocal


router = APIRouter(prefix="/maintenances", tags=["Maintenances"])


def get_maintenance_service(session: AsyncSessionLocal = Depends(get_session)) -> MaintenanceService:
    maintenance_repo = SQLAlchemyMaintenanceRepository(session)
    tractor_repo = SQLAlchemyTractorRepository(session)
    return MaintenanceService(maintenance_repo, tractor_repo)


@router.post(
    "",
    response_model=APIResponse[MaintenanceResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("maintenance:create"))],
)
async def create_maintenance(
    data: MaintenanceCreate,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_active_user),
) -> APIResponse[MaintenanceResponse]:
    """Create a new maintenance record."""
    maintenance = await service.create_maintenance(data, current_user.id)
    return APIResponse(
        success=True,
        message="Maintenance record created successfully",
        data=MaintenanceResponse.model_validate(maintenance),
    )


@router.get(
    "/dashboard",
    response_model=APIResponse[MaintenanceDashboardResponse],
    dependencies=[Depends(PermissionChecker("maintenance:dashboard"))],
)
async def get_dashboard(
    service: MaintenanceService = Depends(get_maintenance_service),
) -> APIResponse[MaintenanceDashboardResponse]:
    """Retrieve maintenance dashboard statistics."""
    stats = await service.get_dashboard()
    return APIResponse(
        success=True,
        message="Dashboard statistics retrieved successfully",
        data=MaintenanceDashboardResponse.model_validate(stats),
    )


@router.get(
    "/upcoming",
    response_model=APIResponse[list[MaintenanceResponse]],
    dependencies=[Depends(PermissionChecker("maintenance:read"))],
)
async def get_upcoming_services(
    service: MaintenanceService = Depends(get_maintenance_service),
) -> APIResponse[list[MaintenanceResponse]]:
    """Retrieve upcoming maintenance services."""
    services = await service.get_upcoming_services()
    return APIResponse(
        success=True,
        message="Upcoming services retrieved successfully",
        data=[MaintenanceResponse.model_validate(s) for s in services],
    )


@router.get(
    "/overdue",
    response_model=APIResponse[list[MaintenanceResponse]],
    dependencies=[Depends(PermissionChecker("maintenance:read"))],
)
async def get_overdue_services(
    service: MaintenanceService = Depends(get_maintenance_service),
) -> APIResponse[list[MaintenanceResponse]]:
    """Retrieve overdue maintenance services."""
    services = await service.get_overdue_services()
    return APIResponse(
        success=True,
        message="Overdue services retrieved successfully",
        data=[MaintenanceResponse.model_validate(s) for s in services],
    )


@router.get(
    "",
    response_model=APIResponse[PaginatedData[MaintenanceResponse]],
    dependencies=[Depends(PermissionChecker("maintenance:read"))],
)
async def list_maintenances(
    search: Optional[str] = None,
    tractor_id: Optional[uuid.UUID] = None,
    maintenance_status: Optional[MaintenanceStatus] = Query(None, alias="status"),
    priority: Optional[MaintenancePriority] = None,
    maintenance_type: Optional[MaintenanceType] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> APIResponse[PaginatedData[MaintenanceResponse]]:
    """List maintenance records with filtering and pagination."""
    filters = {
        "search": search,
        "tractor_id": tractor_id,
        "status": maintenance_status,
        "priority": priority,
        "maintenance_type": maintenance_type,
    }
    
    items, total = await service.search_maintenances(filters, page, size)
    
    return APIResponse(
        success=True,
        message="Maintenances retrieved successfully",
        data=PaginatedData(
            items=[MaintenanceResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        ),
    )


@router.get(
    "/{id}",
    response_model=APIResponse[MaintenanceResponse],
    dependencies=[Depends(PermissionChecker("maintenance:read"))],
)
async def get_maintenance(
    id: uuid.UUID,
    service: MaintenanceService = Depends(get_maintenance_service),
) -> APIResponse[MaintenanceResponse]:
    """Retrieve a specific maintenance record by ID."""
    maintenance = await service.get_maintenance(id)
    return APIResponse(
        success=True,
        message="Maintenance retrieved successfully",
        data=MaintenanceResponse.model_validate(maintenance),
    )


@router.get(
    "/{id}/history",
    response_model=APIResponse[list[MaintenanceHistoryResponse]],
    dependencies=[Depends(PermissionChecker("maintenance:read"))],
)
async def get_maintenance_history(
    id: uuid.UUID,
    service: MaintenanceService = Depends(get_maintenance_service),
) -> APIResponse[list[MaintenanceHistoryResponse]]:
    """Retrieve audit history for a specific maintenance record."""
    maintenance = await service.get_maintenance(id) # Validates existence
    history = await service.maintenance_repo.get_history(id)
    return APIResponse(
        success=True,
        message="Maintenance history retrieved successfully",
        data=[MaintenanceHistoryResponse.model_validate(h) for h in history],
    )


@router.put(
    "/{id}",
    response_model=APIResponse[MaintenanceResponse],
    dependencies=[Depends(PermissionChecker("maintenance:update"))],
)
async def update_maintenance(
    id: uuid.UUID,
    data: MaintenanceUpdate,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_active_user),
) -> APIResponse[MaintenanceResponse]:
    """Update an existing maintenance record."""
    maintenance = await service.update_maintenance(id, data, current_user.id)
    return APIResponse(
        success=True,
        message="Maintenance record updated successfully",
        data=MaintenanceResponse.model_validate(maintenance),
    )


@router.patch(
    "/{id}/status",
    response_model=APIResponse[MaintenanceResponse],
    dependencies=[Depends(PermissionChecker("maintenance:update"))],
)
async def update_maintenance_status(
    id: uuid.UUID,
    data: MaintenanceStatusUpdate,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_active_user),
) -> APIResponse[MaintenanceResponse]:
    """Update the status of a maintenance record."""
    maintenance = await service.update_status(id, data, current_user.id)
    return APIResponse(
        success=True,
        message="Maintenance status updated successfully",
        data=MaintenanceResponse.model_validate(maintenance),
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    dependencies=[Depends(PermissionChecker("maintenance:delete"))],
)
async def delete_maintenance(
    id: uuid.UUID,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_active_user),
) -> APIResponse[None]:
    """Soft delete a scheduled maintenance record."""
    await service.delete_maintenance(id, current_user.id)
    return APIResponse(
        success=True,
        message="Maintenance record deleted successfully",
        data=None,
    )


@router.post(
    "/{id}/restore",
    response_model=APIResponse[MaintenanceResponse],
    dependencies=[Depends(PermissionChecker("maintenance:restore"))],
)
async def restore_maintenance(
    id: uuid.UUID,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_active_user),
) -> APIResponse[MaintenanceResponse]:
    """Restore a deleted maintenance record."""
    maintenance = await service.restore_maintenance(id, current_user.id)
    return APIResponse(
        success=True,
        message="Maintenance record restored successfully",
        data=MaintenanceResponse.model_validate(maintenance),
    )
