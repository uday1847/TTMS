import logging
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_session
from app.api.dependencies.permissions import PermissionChecker
from app.domain.entities.user import User
from app.infrastructure.repositories.driver_repository import SQLAlchemyDriverRepository
from app.application.services.driver_service import DriverService
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.driver import DriverCreate, DriverUpdate, DriverResponse

logger = logging.getLogger("ttms.drivers")

router = APIRouter(prefix="/drivers", tags=["Drivers"])


def get_driver_service(session: AsyncSession = Depends(get_session)) -> DriverService:
    """
    Dependency injection factory constructing the DriverService.
    """
    repository = SQLAlchemyDriverRepository(session)
    return DriverService(session, repository)


@router.get(
    "",
    response_model=APIResponse[PaginatedData[DriverResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("drivers:read"))],
    summary="Get paginated list of drivers with search and filter support",
)
async def list_drivers(
    driver_service: Annotated[DriverService, Depends(get_driver_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    size: int = Query(default=10, ge=1, le=100, description="Items per page limit."),
    q: str | None = Query(default=None, description="Search query matching Name, Mobile, or License."),
    status: str | None = Query(default=None, description="Filter by status: ACTIVE, INACTIVE, or ALL."),
    sort_by: str = Query(default="created_at", description="Sort field: name or created_at."),
    order: str = Query(default="desc", description="Sort order: asc or desc."),
    include_deleted: bool = Query(default=False, description="Include soft-deleted records (Admin only)."),
) -> APIResponse[PaginatedData[DriverResponse]]:
    """
    Retrieves a paginated list of drivers with optional search, sorting, and status filtering.
    Only users with Admin role can query soft-deleted records.
    """
    # Enforce Admin restriction on include_deleted query parameter
    resolved_include_deleted = False
    if include_deleted:
        # Resolve user permissions/roles for inclusion
        is_admin = any(role.name.lower() in ["super admin", "admin"] for role in current_user.roles)
        if is_admin:
            resolved_include_deleted = True
        else:
            logger.warning(
                f"Non-admin user {current_user.email} attempted to query soft-deleted drivers."
            )

    items, total = await driver_service.paginate_drivers(
        page=page,
        size=size,
        search_query=q,
        status_filter=status,
        sort_by=sort_by,
        order=order,
        include_deleted=resolved_include_deleted,
    )

    data = PaginatedData(
        items=[DriverResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        size=size,
    )
    return APIResponse(
        success=True,
        message="Drivers listed successfully.",
        data=data,
    )


@router.get(
    "/{id}",
    response_model=APIResponse[DriverResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("drivers:read"))],
    summary="Get driver details by ID",
)
async def get_driver(
    id: uuid.UUID,
    driver_service: Annotated[DriverService, Depends(get_driver_service)],
) -> APIResponse[DriverResponse]:
    """
    Retrieves driver details and licensing info by ID.
    """
    driver = await driver_service.get_driver_by_id(id)
    return APIResponse(
        success=True,
        message="Driver details retrieved successfully.",
        data=DriverResponse.model_validate(driver),
    )


@router.post(
    "",
    response_model=APIResponse[DriverResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("drivers:create"))],
    summary="Register a new driver",
)
async def create_driver(
    dto: DriverCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    driver_service: Annotated[DriverService, Depends(get_driver_service)],
) -> APIResponse[DriverResponse]:
    """
    Registers a new vehicle driver. Only users with write privilege can access this endpoint.
    """
    driver = await driver_service.create_driver(dto=dto, current_user_id=current_user.id)
    logger.info(
        f"Driver created: id={driver.id} | name={driver.name} | created_by={current_user.id}"
    )
    return APIResponse(
        success=True,
        message="Driver registered successfully.",
        data=DriverResponse.model_validate(driver),
    )


@router.put(
    "/{id}",
    response_model=APIResponse[DriverResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("drivers:update"))],
    summary="Update driver details",
)
async def update_driver(
    id: uuid.UUID,
    dto: DriverUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    driver_service: Annotated[DriverService, Depends(get_driver_service)],
) -> APIResponse[DriverResponse]:
    """
    Updates configuration values of an active driver.
    """
    driver = await driver_service.update_driver(driver_id=id, dto=dto, current_user_id=current_user.id)
    
    # Collect list of changed keys for logging
    updated_fields = [k for k, v in dto.model_dump(exclude_unset=True).items()]
    logger.info(
        f"Driver updated: id={id} | updated_fields={updated_fields} | updated_by={current_user.id}"
    )
    
    return APIResponse(
        success=True,
        message="Driver profile updated successfully.",
        data=DriverResponse.model_validate(driver),
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("drivers:delete"))],
    summary="Soft-delete driver profile",
)
async def delete_driver(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    driver_service: Annotated[DriverService, Depends(get_driver_service)],
) -> APIResponse[None]:
    """
    Soft-deletes a driver profile, checking active trips constraints.
    """
    await driver_service.delete_driver(driver_id=id, current_user_id=current_user.id)
    logger.info(
        f"Driver soft-deleted: id={id} | deleted_by={current_user.id}"
    )
    return APIResponse(
        success=True,
        message="Driver profile has been soft deleted.",
        data=None,
    )


@router.patch(
    "/{id}/status",
    response_model=APIResponse[DriverResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("drivers:update"))],
    summary="Toggle driver logical status",
)
async def toggle_driver_status(
    id: uuid.UUID,
    is_active: bool,
    current_user: Annotated[User, Depends(get_current_active_user)],
    driver_service: Annotated[DriverService, Depends(get_driver_service)],
) -> APIResponse[DriverResponse]:
    """
    Toggles logical is_active status of a driver.
    """
    dto = DriverUpdate(is_active=is_active)
    driver = await driver_service.update_driver(driver_id=id, dto=dto, current_user_id=current_user.id)
    logger.info(
        f"Driver status toggled: id={id} | is_active={is_active} | updated_by={current_user.id}"
    )
    return APIResponse(
        success=True,
        message=f"Driver status set to {'active' if is_active else 'inactive'}.",
        data=DriverResponse.model_validate(driver),
    )
