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
from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_status_history import InvoiceStatusHistory
from app.domain.enums.invoice_status import InvoiceStatus
from app.infrastructure.repositories.invoice_repository import SQLAlchemyInvoiceRepository
from app.infrastructure.repositories.trip_repository import SQLAlchemyTripRepository
from app.application.services.invoice_service import InvoiceService
from app.application.services.invoice_number_generator import InvoiceNumberGenerator
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceStatusUpdate,
    InvoiceResponse,
    InvoiceStatusHistoryResponse,
    InvoiceSummaryResponse,
    InvoiceDashboardResponse,
)

logger = logging.getLogger("ttms.invoices")

router = APIRouter(tags=["Invoices"])


def get_invoice_service(session: AsyncSession = Depends(get_session)) -> InvoiceService:
    """
    Dependency injection factory constructing the InvoiceService.
    """
    repository = SQLAlchemyInvoiceRepository(session)
    trip_repository = SQLAlchemyTripRepository(session)
    generator = InvoiceNumberGenerator(repository)
    return InvoiceService(session, repository, trip_repository, generator)


def map_invoice_response(invoice: Invoice) -> InvoiceResponse:
    """
    Transforms Invoice domain model to rich API response DTO with computed aggregates.
    """
    res = InvoiceResponse.model_validate(invoice)

    trip = getattr(invoice, "trip", None)
    party = getattr(invoice, "party", None)

    if trip:
        res.trip_number = trip.trip_number
        res.trip_date = trip.trip_date
        driver = getattr(trip, "driver", None)
        tractor = getattr(trip, "tractor", None)
        if driver:
            res.driver_name = driver.name
        if tractor:
            res.tractor_number = tractor.tractor_number

    if party:
        res.party_name = party.name
        res.party_mobile = party.mobile_number

    # Calculate due days
    today_date = date.today()
    res.due_days = (invoice.due_date - today_date).days

    # Determine overdue status
    res.is_overdue = (
        invoice.due_date < today_date
        and invoice.status not in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED)
    )

    # Calculate collection percentage
    if invoice.gross_amount > Decimal("0.00"):
        res.payment_percentage = (invoice.received_amount / invoice.gross_amount) * Decimal("100.00")
    else:
        res.payment_percentage = Decimal("0.00")

    # Format status label
    res.status_label = invoice.status.value.replace("_", " ").title()

    return res


@router.post(
    "/invoices",
    response_model=APIResponse[InvoiceResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("trips:create"))],
    summary="Create a new invoice",
)
async def create_invoice(
    payload: InvoiceCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info(f"Creating invoice for Trip ID: {payload.trip_id} by User ID: {current_user.id}")
    invoice = await service.create_invoice(payload, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Invoice created successfully in DRAFT state.",
            "data": map_invoice_response(invoice).model_dump(mode="json"),
        },
    )


@router.get(
    "/invoices/dashboard",
    response_model=APIResponse[InvoiceDashboardResponse],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get aggregated dashboard financial metrics",
)
async def get_invoice_dashboard(
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info("Fetching consolidated invoice dashboard metrics.")
    summary = await service.repository.get_invoice_dashboard_summary()
    data = InvoiceDashboardResponse.model_validate(summary).model_dump(mode="json")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Dashboard metrics retrieved successfully.",
            "data": data,
        },
    )


@router.get(
    "/invoices/summary",
    response_model=APIResponse[InvoiceSummaryResponse],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get unified invoice receivables summary",
)
async def get_invoice_summary(
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info("Fetching invoice financial summaries.")
    summary = await service.repository.get_invoice_dashboard_summary()
    data = InvoiceSummaryResponse.model_validate(summary).model_dump(mode="json")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Summary metrics retrieved successfully.",
            "data": data,
        },
    )


@router.get(
    "/invoices/overdue",
    response_model=APIResponse[list[InvoiceResponse]],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get list of overdue invoices",
)
async def get_overdue_invoices_list(
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info("Listing overdue invoices.")
    invoices = await service.repository.get_overdue_invoices()
    response_data = [map_invoice_response(i).model_dump(mode="json") for i in invoices]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Overdue invoices retrieved successfully.",
            "data": response_data,
        },
    )


@router.get(
    "/invoices/pending",
    response_model=APIResponse[list[InvoiceResponse]],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get list of pending/active invoices",
)
async def get_pending_invoices_list(
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info("Listing active/pending invoices.")
    invoices = await service.repository.get_pending_invoices()
    response_data = [map_invoice_response(i).model_dump(mode="json") for i in invoices]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Pending invoices retrieved successfully.",
            "data": response_data,
        },
    )


@router.get(
    "/invoices/party/{party_id}",
    response_model=APIResponse[PaginatedData[InvoiceResponse]],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get invoices associated with a specific party",
)
async def get_invoices_by_party(
    party_id: uuid.UUID,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
) -> JSONResponse:
    logger.info(f"Fetching invoices for Party ID: {party_id}")
    invoices, total = await service.repository.get_invoices(
        party_id=party_id,
        page=page,
        size=size,
    )
    response_data = [map_invoice_response(i).model_dump(mode="json") for i in invoices]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Party invoices retrieved successfully.",
            "data": {
                "items": response_data,
                "total": total,
                "page": page,
                "size": size,
            },
        },
    )


@router.get(
    "/invoices/trip/{trip_id}",
    response_model=APIResponse[InvoiceResponse],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get invoice generated for a specific trip",
)
async def get_invoice_by_trip(
    trip_id: uuid.UUID,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info(f"Fetching invoice matching Trip ID: {trip_id}")
    invoice = await service.repository.get_by_trip(trip_id)
    if not invoice:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": f"No active invoice found generated for Trip ID {trip_id}.",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Trip invoice retrieved successfully.",
            "data": map_invoice_response(invoice).model_dump(mode="json"),
        },
    )


@router.get(
    "/invoices",
    response_model=APIResponse[PaginatedData[InvoiceResponse]],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="List paginated invoices with search and filters",
)
async def list_invoices(
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
    q: str | None = Query(default=None, description="Search query matching invoice/trip number, party mobile or name"),
    status_filter: InvoiceStatus | None = Query(default=None, alias="status"),
    party_id: uuid.UUID | None = Query(default=None),
    trip_id: uuid.UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    balance_min: float | None = Query(default=None),
    balance_max: float | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
) -> JSONResponse:
    logger.info("Listing invoices with parameters.")
    invoices, total = await service.repository.get_invoices(
        search_query=q,
        status=status_filter,
        party_id=party_id,
        trip_id=trip_id,
        date_from=date_from,
        date_to=date_to,
        balance_min=balance_min,
        balance_max=balance_max,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        size=size,
    )
    response_data = [map_invoice_response(i).model_dump(mode="json") for i in invoices]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Invoices retrieved successfully.",
            "data": {
                "items": response_data,
                "total": total,
                "page": page,
                "size": size,
            },
        },
    )


@router.get(
    "/invoices/{id}",
    response_model=APIResponse[InvoiceResponse],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get invoice detail by unique ID",
)
async def get_invoice(
    id: uuid.UUID,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info(f"Retrieving invoice ID: {id}")
    invoice = await service.get_invoice_by_id(id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Invoice details retrieved successfully.",
            "data": map_invoice_response(invoice).model_dump(mode="json"),
        },
    )


@router.get(
    "/invoices/{id}/history",
    response_model=APIResponse[list[InvoiceStatusHistoryResponse]],
    dependencies=[Depends(PermissionChecker("trips:read"))],
    summary="Get invoice status audit log history",
)
async def get_invoice_history(
    id: uuid.UUID,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info(f"Fetching status history logs for Invoice ID: {id}")
    history = await service.repository.get_invoice_status_history(id)
    response_data = [InvoiceStatusHistoryResponse.model_validate(h).model_dump(mode="json") for h in history]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Invoice status history logs retrieved successfully.",
            "data": response_data,
        },
    )


@router.put(
    "/invoices/{id}",
    response_model=APIResponse[InvoiceResponse],
    dependencies=[Depends(PermissionChecker("trips:update"))],
    summary="Update invoice properties",
)
async def update_invoice(
    id: uuid.UUID,
    payload: InvoiceUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info(f"Updating invoice ID: {id} by User ID: {current_user.id}")
    invoice = await service.update_invoice(id, payload, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Invoice updated successfully.",
            "data": map_invoice_response(invoice).model_dump(mode="json"),
        },
    )


@router.patch(
    "/invoices/{id}/status",
    response_model=APIResponse[InvoiceResponse],
    dependencies=[Depends(PermissionChecker("trips:update"))],
    summary="Update invoice state",
)
async def update_invoice_status(
    id: uuid.UUID,
    payload: InvoiceStatusUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info(f"Patching status on invoice ID: {id} to {payload.status} by User ID: {current_user.id}")
    invoice = await service.update_status(id, payload, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": f"Invoice status updated successfully to {payload.status.value}.",
            "data": map_invoice_response(invoice).model_dump(mode="json"),
        },
    )


@router.post(
    "/invoices/{id}/payments",
    response_model=APIResponse[InvoiceResponse],
    dependencies=[Depends(PermissionChecker("trips:update"))],
    summary="Record a payment receipt on an invoice",
)
async def record_invoice_payment(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
    amount: Decimal = Query(gt=0, description="Amount received"),
    remarks: str | None = Query(default=None, max_length=500),
) -> JSONResponse:
    logger.info(f"Recording payment of {amount} on invoice ID: {id} by User ID: {current_user.id}")
    invoice = await service.record_payment(id, amount, remarks, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Invoice payment transaction recorded successfully.",
            "data": map_invoice_response(invoice).model_dump(mode="json"),
        },
    )


@router.delete(
    "/invoices/{id}",
    response_model=APIResponse[InvoiceResponse],
    dependencies=[Depends(PermissionChecker("trips:delete"))],
    summary="Soft delete a draft invoice",
)
async def delete_invoice(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> JSONResponse:
    logger.info(f"Soft deleting invoice ID: {id} by User ID: {current_user.id}")
    invoice = await service.delete_invoice(id, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Invoice soft deleted successfully.",
            "data": map_invoice_response(invoice).model_dump(mode="json"),
        },
    )
