from datetime import date
from decimal import Decimal
import logging
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_session
from app.api.dependencies.permissions import PermissionChecker
from app.domain.entities.user import User
from app.domain.entities.trip_expense import TripExpense
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode
from app.infrastructure.repositories.trip_expense_repository import SQLAlchemyTripExpenseRepository
from app.infrastructure.repositories.trip_repository import SQLAlchemyTripRepository
from app.application.services.trip_expense_service import TripExpenseService
from app.application.services.expense_number_generator import ExpenseNumberGenerator
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.trip_expense import (
    TripExpenseCreate,
    TripExpenseUpdate,
    TripExpenseResponse,
    TripExpenseSummaryResponse,
    TripDashboardResponse,
)

logger = logging.getLogger("ttms.trip_expenses")

router = APIRouter(tags=["Trip Expenses"])


def get_trip_expense_service(session: AsyncSession = Depends(get_session)) -> TripExpenseService:
    """
    Dependency injection factory constructing the TripExpenseService.
    """
    repository = SQLAlchemyTripExpenseRepository(session)
    trip_repository = SQLAlchemyTripRepository(session)
    number_generator = ExpenseNumberGenerator(repository)
    return TripExpenseService(session, repository, trip_repository, number_generator)


def map_expense_response(expense: TripExpense) -> TripExpenseResponse:
    """
    Helper converting TripExpense entity to DTO response.
    """
    return TripExpenseResponse.model_validate(expense)


@router.post(
    "/trip-expenses",
    response_model=APIResponse[TripExpenseResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("trips:update"))],
    summary="Create a new trip expense",
)
async def create_trip_expense(
    dto: TripExpenseCreate,
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Request,
) -> APIResponse[TripExpenseResponse]:
    """
    Creates a new operational expense entry under an active, non-completed trip.
    """
    client_ip = request.client.host if request.client else None
    expense = await service.create_expense(dto, current_user.id, client_ip)
    return APIResponse(
        success=True,
        message="Trip expense created successfully.",
        data=map_expense_response(expense),
    )


@router.get(
    "/trip-expenses",
    response_model=APIResponse[PaginatedData[TripExpenseResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get paginated list of trip expenses with filtering",
)
async def list_trip_expenses(
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    trip_id: uuid.UUID | None = Query(default=None),
    expense_type: ExpenseType | None = Query(default=None),
    payment_mode: PaymentMode | None = Query(default=None),
    paid_to_name: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    min_amount: Decimal | None = Query(default=None),
    max_amount: Decimal | None = Query(default=None),
    sort_by: str = Query(default="expense_date"),
    sort_order: str = Query(default="desc"),
) -> APIResponse[PaginatedData[TripExpenseResponse]]:
    """
    Retrieves filtered list of operational expenses with sorting and pagination.
    """
    skip = (page - 1) * size
    expenses, total = await service.get_trip_expenses(
        trip_id=trip_id,
        expense_type=expense_type,
        payment_mode=payment_mode,
        paid_to_name=paid_to_name,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        skip=skip,
        limit=size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    response_list = [map_expense_response(e) for e in expenses]
    
    return APIResponse(
        success=True,
        message="Trip expenses retrieved successfully.",
        data=PaginatedData(
            items=response_list,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        ),
    )


@router.get(
    "/trip-expenses/{id}",
    response_model=APIResponse[TripExpenseResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get trip expense details by ID",
)
async def get_trip_expense(
    id: uuid.UUID,
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
) -> APIResponse[TripExpenseResponse]:
    """
    Retrieves complete detail for a single trip expense entry.
    """
    expense = await service.get_expense_by_id(id)
    return APIResponse(
        success=True,
        message="Trip expense details retrieved successfully.",
        data=map_expense_response(expense),
    )


@router.put(
    "/trip-expenses/{id}",
    response_model=APIResponse[TripExpenseResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:update"))],
    summary="Update trip expense details by ID",
)
async def update_trip_expense(
    id: uuid.UUID,
    dto: TripExpenseUpdate,
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Request,
) -> APIResponse[TripExpenseResponse]:
    """
    Updates properties of an existing trip expense entry.
    """
    client_ip = request.client.host if request.client else None
    expense = await service.update_expense(id, dto, current_user.id, client_ip)
    return APIResponse(
        success=True,
        message="Trip expense updated successfully.",
        data=map_expense_response(expense),
    )


@router.delete(
    "/trip-expenses/{id}",
    response_model=APIResponse[TripExpenseResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:update"))],
    summary="Soft delete a trip expense entry",
)
async def delete_trip_expense(
    id: uuid.UUID,
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Request,
) -> APIResponse[TripExpenseResponse]:
    """
    Soft deletes a trip expense transaction from operational log.
    """
    client_ip = request.client.host if request.client else None
    expense = await service.delete_expense(id, current_user.id, client_ip)
    return APIResponse(
        success=True,
        message="Trip expense deleted successfully.",
        data=map_expense_response(expense),
    )


@router.get(
    "/trips/{trip_id}/expenses",
    response_model=APIResponse[list[TripExpenseResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get all expenses for a specific trip",
)
async def get_expenses_for_trip(
    trip_id: uuid.UUID,
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
) -> APIResponse[list[TripExpenseResponse]]:
    """
    Retrieves all active expenses linked to the specified Trip.
    """
    expenses, _ = await service.get_trip_expenses(trip_id=trip_id, limit=1000)
    response_list = [map_expense_response(e) for e in expenses]
    return APIResponse(
        success=True,
        message="Trip expenses retrieved successfully.",
        data=response_list,
    )


@router.get(
    "/trips/{trip_id}/expense-summary",
    response_model=APIResponse[TripExpenseSummaryResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get aggregated expense summary for a trip",
)
async def get_trip_expense_summary(
    trip_id: uuid.UUID,
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
) -> APIResponse[TripExpenseSummaryResponse]:
    """
    Returns total and grouped expense category aggregates for a single trip.
    """
    summary = await service.get_trip_expense_summary(trip_id)
    return APIResponse(
        success=True,
        message="Trip expense summary retrieved successfully.",
        data=summary,
    )


@router.get(
    "/trips/{trip_id}/profit",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get detailed profit and margins details for a trip",
)
async def get_trip_profit(
    trip_id: uuid.UUID,
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
) -> APIResponse[dict]:
    """
    Returns profit margins percentages, freight sum, total expenses and net profit for a trip.
    """
    profit = await service.get_trip_profit_details(trip_id)
    return APIResponse(
        success=True,
        message="Trip profit details retrieved successfully.",
        data=profit,
    )


@router.get(
    "/trips/{trip_id}/dashboard",
    response_model=APIResponse[TripDashboardResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get comprehensive aggregated context for single-screen rendering",
)
async def get_trip_dashboard(
    trip_id: uuid.UUID,
    service: Annotated[TripExpenseService, Depends(get_trip_expense_service)],
) -> APIResponse[TripDashboardResponse]:
    """
    Returns the comprehensive aggregated dataset (financials, expenses list, history timeline) for the trip screen.
    """
    dashboard = await service.get_trip_dashboard(trip_id)
    return APIResponse(
        success=True,
        message="Trip dashboard aggregation retrieved successfully.",
        data=dashboard,
    )
