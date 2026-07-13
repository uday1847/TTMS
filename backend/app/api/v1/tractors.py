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
from app.infrastructure.repositories.tractor_repository import SQLAlchemyTractorRepository
from app.application.services.tractor_service import TractorService
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.tractor import TractorCreate, TractorUpdate, TractorResponse

logger = logging.getLogger("ttms.tractors")

router = APIRouter(prefix="/tractors", tags=["Tractors"])


def get_tractor_service(session: AsyncSession = Depends(get_session)) -> TractorService:
    """
    Dependency injection factory constructing the TractorService.
    """
    repository = SQLAlchemyTractorRepository(session)
    return TractorService(session, repository)


@router.get(
    "",
    response_model=APIResponse[PaginatedData[TractorResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("tractors:read"))],
    summary="Get paginated list of tractors with search and filter support",
)
async def list_tractors(
    tractor_service: Annotated[TractorService, Depends(get_tractor_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    size: int = Query(default=10, ge=1, le=100, description="Items per page limit."),
    q: str | None = Query(default=None, description="Search query matching Tractor Number, Owner Name, or RC Number."),
    status: str | None = Query(default=None, description="Filter by status: ACTIVE, INACTIVE, or ALL."),
    insurance_expiring_days: int | None = Query(default=None, description="Filter by insurance expiring within N days."),
    created_date_start: str | None = Query(default=None, description="Filter by created date range start (YYYY-MM-DD)."),
    created_date_end: str | None = Query(default=None, description="Filter by created date range end (YYYY-MM-DD)."),
    sort_by: str = Query(default="created_at", description="Sort field: tractor_number, owner_name, insurance_expiry, or created_at."),
    order: str = Query(default="desc", description="Sort order: asc or desc."),
    include_deleted: bool = Query(default=False, description="Include soft-deleted records (Admin only)."),
) -> APIResponse[PaginatedData[TractorResponse]]:
    """
    Retrieves a paginated list of tractors with optional search, sorting, and status filtering.
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
                f"Non-admin user {current_user.email} attempted to query soft-deleted tractors."
            )

    items, total = await tractor_service.paginate_tractors(
        page=page,
        size=size,
        search_query=q,
        status_filter=status,
        insurance_expiring_days=insurance_expiring_days,
        created_date_start=created_date_start,
        created_date_end=created_date_end,
        sort_by=sort_by,
        order=order,
        include_deleted=resolved_include_deleted,
    )

    response_data = [TractorResponse.model_validate(item) for item in items]
    return APIResponse(
        success=True,
        message="Tractor list retrieved successfully.",
        data=PaginatedData(
            items=response_data,
            total=total,
            page=page,
            size=size,
        ),
    )


@router.get(
    "/{id}",
    response_model=APIResponse[TractorResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("tractors:read"))],
    summary="Get tractor details by ID",
)
async def get_tractor(
    id: uuid.UUID,
    tractor_service: Annotated[TractorService, Depends(get_tractor_service)],
) -> APIResponse[TractorResponse]:
    """
    Retrieves detailed properties for a single active tractor profile.
    """
    tractor = await tractor_service.get_tractor_by_id(id)
    return APIResponse(
        success=True,
        message="Tractor details retrieved successfully.",
        data=TractorResponse.model_validate(tractor),
    )


@router.post(
    "",
    response_model=APIResponse[TractorResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("tractors:create"))],
    summary="Register a new tractor",
)
async def create_tractor(
    dto: TractorCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    tractor_service: Annotated[TractorService, Depends(get_tractor_service)],
) -> APIResponse[TractorResponse]:
    """
    Registers a new tractor profile after validating unique constraints.
    Requires 'tractors:create' permission scope.
    """
    logger.info(f"Tractor registration initiated by {current_user.email} for plate: {dto.tractor_number}")
    tractor = await tractor_service.create_tractor(dto, current_user_id=current_user.id)
    logger.info(f"Tractor created successfully: ID {tractor.id} (Plate: {tractor.tractor_number})")
    
    return APIResponse(
        success=True,
        message="Tractor created successfully.",
        data=TractorResponse.model_validate(tractor),
    )


@router.put(
    "/{id}",
    response_model=APIResponse[TractorResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("tractors:update"))],
    summary="Update tractor details",
)
async def update_tractor(
    id: uuid.UUID,
    dto: TractorUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    tractor_service: Annotated[TractorService, Depends(get_tractor_service)],
) -> APIResponse[TractorResponse]:
    """
    Updates the configuration of an existing active tractor profile.
    Enforces unique checks. Requires 'tractors:update' scope.
    """
    logger.info(f"Tractor update initiated by {current_user.email} for ID {id}")
    tractor = await tractor_service.update_tractor(id, dto, current_user_id=current_user.id)
    logger.info(f"Tractor updated successfully: ID {id}")
    
    return APIResponse(
        success=True,
        message="Tractor updated successfully.",
        data=TractorResponse.model_validate(tractor),
    )


@router.patch(
    "/{id}/status",
    response_model=APIResponse[TractorResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("tractors:update"))],
    summary="Toggle tractor logical status",
)
async def toggle_tractor_status(
    id: uuid.UUID,
    is_active: bool,
    current_user: Annotated[User, Depends(get_current_active_user)],
    tractor_service: Annotated[TractorService, Depends(get_tractor_service)],
) -> APIResponse[TractorResponse]:
    """
    Enables or disables a tractor profile logically.
    Requires 'tractors:update' scope.
    """
    logger.info(f"Tractor status toggle initiated by {current_user.email} for ID {id} (is_active: {is_active})")
    update_dto = TractorUpdate(is_active=is_active)
    tractor = await tractor_service.update_tractor(id, update_dto, current_user_id=current_user.id)
    logger.info(f"Tractor status toggled successfully: ID {id}")
    
    return APIResponse(
        success=True,
        message="Tractor status updated successfully.",
        data=TractorResponse.model_validate(tractor),
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("tractors:delete"))],
    summary="Soft-delete tractor profile",
)
async def delete_tractor(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    tractor_service: Annotated[TractorService, Depends(get_tractor_service)],
) -> APIResponse[None]:
    """
    Soft-deletes a tractor profile. Blocks deletion if tractor is linked to active trips.
    Requires 'tractors:delete' scope.
    """
    logger.info(f"Tractor deletion initiated by {current_user.email} for ID {id}")
    await tractor_service.delete_tractor(id, current_user_id=current_user.id)
    logger.info(f"Tractor soft-deleted successfully: ID {id}")
    
    return APIResponse(
        success=True,
        message="Tractor deleted successfully.",
        data=None,
    )
