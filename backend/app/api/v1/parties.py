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
from app.infrastructure.repositories.party_repository import SQLAlchemyPartyRepository
from app.application.services.party_service import PartyService
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.party import PartyCreate, PartyUpdate, PartyResponse

logger = logging.getLogger("ttms.parties")

router = APIRouter(prefix="/parties", tags=["Parties"])


def get_party_service(session: AsyncSession = Depends(get_session)) -> PartyService:
    """
    Dependency injection factory constructing the PartyService.
    """
    repository = SQLAlchemyPartyRepository(session)
    return PartyService(session, repository)


@router.get(
    "",
    response_model=APIResponse[PaginatedData[PartyResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("parties:read"))],
    summary="Get paginated list of parties with search and filter support",
)
async def list_parties(
    party_service: Annotated[PartyService, Depends(get_party_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    size: int = Query(default=10, ge=1, le=100, description="Items per page limit."),
    q: str | None = Query(default=None, description="Search query matching Name, Mobile, GST, City, or Contact Person."),
    party_type: str | None = Query(default=None, description="Filter by party type: CUSTOMER, SUPPLIER, BROKER, OTHER."),
    status: str | None = Query(default=None, description="Filter by status: ACTIVE, INACTIVE, or ALL."),
    city: str | None = Query(default=None, description="Filter by exact city name."),
    state: str | None = Query(default=None, description="Filter by exact state name."),
    created_date_start: str | None = Query(default=None, description="Filter by created date range start (YYYY-MM-DD)."),
    created_date_end: str | None = Query(default=None, description="Filter by created date range end (YYYY-MM-DD)."),
    sort_by: str = Query(default="created_at", description="Sort field: name, created_at, or opening_balance."),
    order: str = Query(default="desc", description="Sort order: asc or desc."),
    include_deleted: bool = Query(default=False, description="Include soft-deleted records (Admin only)."),
) -> APIResponse[PaginatedData[PartyResponse]]:
    """
    Retrieves a paginated list of parties with optional search, sorting, and filters.
    Only users with Admin role can query soft-deleted records.
    """
    # Enforce Admin restriction on include_deleted query parameter
    resolved_include_deleted = False
    if include_deleted:
        is_admin = any(role.name.lower() in ["super admin", "admin"] for role in current_user.roles)
        if is_admin:
            resolved_include_deleted = True
        else:
            logger.warning(
                f"Non-admin user {current_user.email} attempted to query soft-deleted parties."
            )

    items, total = await party_service.paginate_parties(
        page=page,
        size=size,
        search_query=q,
        party_type_filter=party_type,
        status_filter=status,
        city_filter=city,
        state_filter=state,
        created_date_start=created_date_start,
        created_date_end=created_date_end,
        sort_by=sort_by,
        order=order,
        include_deleted=resolved_include_deleted,
    )

    response_data = [PartyResponse.model_validate(item) for item in items]
    return APIResponse(
        success=True,
        message="Party list retrieved successfully.",
        data=PaginatedData(
            items=response_data,
            total=total,
            page=page,
            size=size,
        ),
    )


@router.get(
    "/{id}",
    response_model=APIResponse[PartyResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("parties:read"))],
    summary="Get party details by ID",
)
async def get_party(
    id: uuid.UUID,
    party_service: Annotated[PartyService, Depends(get_party_service)],
) -> APIResponse[PartyResponse]:
    """
    Retrieves detailed properties for a single active party profile.
    """
    party = await party_service.get_party_by_id(id)
    return APIResponse(
        success=True,
        message="Party details retrieved successfully.",
        data=PartyResponse.model_validate(party),
    )


@router.post(
    "",
    response_model=APIResponse[PartyResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("parties:create"))],
    summary="Register a new party",
)
async def create_party(
    dto: PartyCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    party_service: Annotated[PartyService, Depends(get_party_service)],
) -> APIResponse[PartyResponse]:
    """
    Registers a new party profile after validating unique constraints.
    Requires 'parties:create' permission scope.
    """
    logger.info(f"Party registration initiated by {current_user.email} for name: {dto.name}")
    party = await party_service.create_party(dto, current_user_id=current_user.id)
    logger.info(f"Party created successfully: ID {party.id} (Name: {party.name})")

    return APIResponse(
        success=True,
        message="Party created successfully.",
        data=PartyResponse.model_validate(party),
    )


@router.put(
    "/{id}",
    response_model=APIResponse[PartyResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("parties:update"))],
    summary="Update party details",
)
async def update_party(
    id: uuid.UUID,
    dto: PartyUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    party_service: Annotated[PartyService, Depends(get_party_service)],
) -> APIResponse[PartyResponse]:
    """
    Updates the configuration of an existing active party profile.
    Enforces unique checks. Requires 'parties:update' scope.
    """
    logger.info(f"Party update initiated by {current_user.email} for ID {id}")
    party = await party_service.update_party(id, dto, current_user_id=current_user.id)
    logger.info(f"Party updated successfully: ID {id}")

    return APIResponse(
        success=True,
        message="Party updated successfully.",
        data=PartyResponse.model_validate(party),
    )


@router.patch(
    "/{id}/status",
    response_model=APIResponse[PartyResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("parties:update"))],
    summary="Toggle party logical status",
)
async def toggle_party_status(
    id: uuid.UUID,
    is_active: bool,
    current_user: Annotated[User, Depends(get_current_active_user)],
    party_service: Annotated[PartyService, Depends(get_party_service)],
) -> APIResponse[PartyResponse]:
    """
    Enables or disables a party profile logically.
    Requires 'parties:update' scope.
    """
    logger.info(f"Party status toggle initiated by {current_user.email} for ID {id} (is_active: {is_active})")
    update_dto = PartyUpdate(is_active=is_active)
    party = await party_service.update_party(id, update_dto, current_user_id=current_user.id)
    logger.info(f"Party status toggled successfully: ID {id}")

    return APIResponse(
        success=True,
        message="Party status updated successfully.",
        data=PartyResponse.model_validate(party),
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("parties:delete"))],
    summary="Soft-delete party profile",
)
async def delete_party(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    party_service: Annotated[PartyService, Depends(get_party_service)],
) -> APIResponse[None]:
    """
    Soft-deletes a party profile. Blocks deletion if party is linked to active trips.
    Requires 'parties:delete' scope.
    """
    logger.info(f"Party deletion initiated by {current_user.email} for ID {id}")
    await party_service.delete_party(id, current_user_id=current_user.id)
    logger.info(f"Party soft-deleted successfully: ID {id}")

    return APIResponse(
        success=True,
        message="Party deleted successfully.",
        data=None,
    )
