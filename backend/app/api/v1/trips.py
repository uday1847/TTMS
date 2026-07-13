from datetime import date, datetime
from decimal import Decimal
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
from app.domain.entities.trip import Trip
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.expense_type import ExpenseType
from app.infrastructure.repositories.trip_repository import SQLAlchemyTripRepository
from app.application.services.trip_service import TripService
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.trip import (
    TripCreate,
    TripUpdate,
    TripStatusUpdate,
    TripResponse,
    TripStatusHistoryResponse,
)

logger = logging.getLogger("ttms.trips")

router = APIRouter(prefix="/trips", tags=["Trips"])


def get_trip_service(session: AsyncSession = Depends(get_session)) -> TripService:
    """
    Dependency injection factory constructing the TripService.
    """
    repository = SQLAlchemyTripRepository(session)
    return TripService(session, repository)


def map_trip_response(trip: Trip) -> TripResponse:
    """
    Helper converting Trip entity to DTO including computed read properties.
    """
    res = TripResponse.model_validate(trip)
    res.driver_name = trip.driver.name if getattr(trip, "driver", None) else None
    res.tractor_number = trip.tractor.tractor_number if getattr(trip, "tractor", None) else None
    res.party_name = trip.party.name if getattr(trip, "party", None) else None
    res.trip_age = (date.today() - trip.trip_date).days
    res.status_label = trip.status.value.replace("_", " ").title()

    # Compute financial values
    active_expenses = [e for e in getattr(trip, "expenses", []) if e.is_active and e.deleted_at is None]
    res.total_expense = sum((e.amount for e in active_expenses), Decimal("0.00"))
    res.net_profit = trip.freight_amount - res.total_expense
    
    driver_advances_sum = sum((e.amount for e in active_expenses if e.expense_type == ExpenseType.DRIVER_ADVANCE), Decimal("0.00"))
    res.total_advances = trip.advance_amount + driver_advances_sum
    res.expense_count = len(active_expenses)

    return res


@router.get(
    "",
    response_model=APIResponse[PaginatedData[TripResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get paginated list of trips with search and filter support",
)
async def list_trips(
    trip_service: Annotated[TripService, Depends(get_trip_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    q: str | None = Query(default=None, description="Search by trip number, location, remarks, driver, tractor, or party."),
    status_filter: str | None = Query(default=None, alias="status"),
    driver_id: uuid.UUID | None = Query(default=None),
    party_id: uuid.UUID | None = Query(default=None),
    tractor_id: uuid.UUID | None = Query(default=None),
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
    created_date_start: str | None = Query(default=None),
    created_date_end: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    include_deleted: bool = Query(default=False),
) -> APIResponse[PaginatedData[TripResponse]]:
    """
    Retrieves a paginated page of trips. Include deleted is restricted to admins.
    """
    resolved_include_deleted = False
    if include_deleted:
        is_admin = any(role.name.lower() in ["super admin", "admin"] for role in current_user.roles)
        if is_admin:
            resolved_include_deleted = True
        else:
            logger.warning(f"Non-admin user {current_user.email} attempted to query soft-deleted trips.")

    items, total = await trip_service.paginate_trips(
        page=page,
        size=size,
        search_query=q,
        status_filter=status_filter,
        driver_id=driver_id,
        party_id=party_id,
        tractor_id=tractor_id,
        date_start=date_start,
        date_end=date_end,
        created_date_start=created_date_start,
        created_date_end=created_date_end,
        sort_by=sort_by,
        order=order,
        include_deleted=resolved_include_deleted,
    )

    response_data = [map_trip_response(item) for item in items]
    return APIResponse(
        success=True,
        message="Trip list retrieved successfully.",
        data=PaginatedData(
            items=response_data,
            total=total,
            page=page,
            size=size,
        ),
    )


@router.get(
    "/active",
    response_model=APIResponse[PaginatedData[TripResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get active trips list",
)
async def list_active_trips(
    trip_service: Annotated[TripService, Depends(get_trip_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
) -> APIResponse[PaginatedData[TripResponse]]:
    """
    Returns active trips (DISPATCHED and IN_PROGRESS).
    """
    # Active trips queries
    items, total = await trip_service.paginate_trips(
        page=page,
        size=size,
        status_filter="DISPATCHED", # We merge them in results or run query for both
    )
    # Get IN_PROGRESS as well
    items_in_progress, total_in_progress = await trip_service.paginate_trips(
        page=page,
        size=size,
        status_filter="IN_PROGRESS",
    )
    combined_items = list(items) + list(items_in_progress)
    combined_total = total + total_in_progress

    response_data = [map_trip_response(item) for item in combined_items]
    return APIResponse(
        success=True,
        message="Active trips retrieved successfully.",
        data=PaginatedData(
            items=response_data,
            total=combined_total,
            page=page,
            size=size,
        ),
    )


@router.get(
    "/completed",
    response_model=APIResponse[PaginatedData[TripResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get completed trips list",
)
async def list_completed_trips(
    trip_service: Annotated[TripService, Depends(get_trip_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
) -> APIResponse[PaginatedData[TripResponse]]:
    items, total = await trip_service.paginate_trips(
        page=page,
        size=size,
        status_filter="COMPLETED",
    )
    response_data = [map_trip_response(item) for item in items]
    return APIResponse(
        success=True,
        message="Completed trips retrieved successfully.",
        data=PaginatedData(
            items=response_data,
            total=total,
            page=page,
            size=size,
        ),
    )


@router.get(
    "/pending",
    response_model=APIResponse[PaginatedData[TripResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get pending trips list",
)
async def list_pending_trips(
    trip_service: Annotated[TripService, Depends(get_trip_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
) -> APIResponse[PaginatedData[TripResponse]]:
    items, total = await trip_service.paginate_trips(
        page=page,
        size=size,
        status_filter="PENDING",
    )
    response_data = [map_trip_response(item) for item in items]
    return APIResponse(
        success=True,
        message="Pending trips retrieved successfully.",
        data=PaginatedData(
            items=response_data,
            total=total,
            page=page,
            size=size,
        ),
    )


@router.get(
    "/{id}",
    response_model=APIResponse[TripResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get trip details by ID",
)
async def get_trip(
    id: uuid.UUID,
    trip_service: Annotated[TripService, Depends(get_trip_service)],
) -> APIResponse[TripResponse]:
    """
    Retrieves detailed properties for a single active trip.
    """
    trip = await trip_service.get_trip_by_id(id)
    return APIResponse(
        success=True,
        message="Trip details retrieved successfully.",
        data=map_trip_response(trip),
    )


@router.post(
    "",
    response_model=APIResponse[TripResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("trips:create"))],
    summary="Register a new trip",
)
async def create_trip(
    dto: TripCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    trip_service: Annotated[TripService, Depends(get_trip_service)],
) -> APIResponse[TripResponse]:
    """
    Registers a new trip profile after validation checks and busy checks.
    """
    logger.info(f"Trip registration initiated by {current_user.email} for driver ID: {dto.driver_id}")
    trip = await trip_service.create_trip(dto, current_user_id=current_user.id)
    logger.info(f"Trip created successfully: ID {trip.id} (Number: {trip.trip_number})")
    
    # Reload trip to get relation models
    trip_reloaded = await trip_service.get_trip_by_id(trip.id)
    return APIResponse(
        success=True,
        message="Trip created successfully.",
        data=map_trip_response(trip_reloaded),
    )


@router.put(
    "/{id}",
    response_model=APIResponse[TripResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:update"))],
    summary="Update trip details",
)
async def update_trip(
    id: uuid.UUID,
    dto: TripUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    trip_service: Annotated[TripService, Depends(get_trip_service)],
) -> APIResponse[TripResponse]:
    """
    Updates the configuration of an existing active trip profile.
    """
    logger.info(f"Trip update initiated by {current_user.email} for ID {id}")
    trip = await trip_service.update_trip(id, dto, current_user_id=current_user.id)
    logger.info(f"Trip updated successfully: ID {id}")
    
    trip_reloaded = await trip_service.get_trip_by_id(trip.id)
    return APIResponse(
        success=True,
        message="Trip updated successfully.",
        data=map_trip_response(trip_reloaded),
    )


@router.patch(
    "/{id}/status",
    response_model=APIResponse[TripResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:update"))],
    summary="Shift trip workflow status",
)
async def shift_trip_status(
    id: uuid.UUID,
    dto: TripStatusUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    trip_service: Annotated[TripService, Depends(get_trip_service)],
) -> APIResponse[TripResponse]:
    """
    Shifts the state of a trip inside the state workflow machine.
    """
    logger.info(f"Trip status shift initiated by {current_user.email} to {dto.status} for ID {id}")
    trip = await trip_service.update_trip_status(
        id,
        new_status=dto.status,
        remarks=dto.remarks,
        current_user_id=current_user.id
    )
    logger.info(f"Trip status shifted successfully: ID {id}")
    
    trip_reloaded = await trip_service.get_trip_by_id(trip.id)
    return APIResponse(
        success=True,
        message="Trip status updated successfully.",
        data=map_trip_response(trip_reloaded),
    )


@router.get(
    "/{id}/history",
    response_model=APIResponse[list[TripStatusHistoryResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get trip status change timeline history",
)
async def get_trip_history(
    id: uuid.UUID,
    trip_service: Annotated[TripService, Depends(get_trip_service)],
) -> APIResponse[list[TripStatusHistoryResponse]]:
    """
    Returns timeline logs of status transitions for a trip.
    """
    history = await trip_service.get_trip_history(id)
    response_data = [TripStatusHistoryResponse.model_validate(h) for h in history]
    return APIResponse(
        success=True,
        message="Trip status timeline history retrieved successfully.",
        data=response_data,
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:delete"))],
    summary="Soft-delete trip transaction",
)
async def delete_trip(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    trip_service: Annotated[TripService, Depends(get_trip_service)],
) -> APIResponse[None]:
    """
    Soft-deletes a trip transaction if it is in PENDING status.
    """
    logger.info(f"Trip deletion initiated by {current_user.email} for ID {id}")
    await trip_service.delete_trip(id, current_user_id=current_user.id)
    logger.info(f"Trip soft-deleted successfully: ID {id}")
    
    return APIResponse(
        success=True,
        message="Trip deleted successfully.",
        data=None,
    )
