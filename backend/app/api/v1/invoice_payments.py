import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.api.dependencies.db import get_session
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.invoice_payment import (
    InvoicePaymentCreate,
    InvoicePaymentUpdate,
    InvoicePaymentResponse,
    InvoicePaymentDashboardResponse,
    ReceiptResponse,
)
from app.application.services.invoice_payment_service import InvoicePaymentService
from app.application.services.receipt_service import ReceiptService
from app.domain.entities.invoice_payment import InvoicePayment
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.repositories.invoice_payment_repository import SQLAlchemyInvoicePaymentRepository
from app.infrastructure.repositories.invoice_repository import SQLAlchemyInvoiceRepository
from app.domain.entities.user import User

router = APIRouter(prefix="/invoice-payments", tags=["Invoice Payments"])


def get_invoice_payment_service(session: AsyncSessionLocal = Depends(get_session)) -> InvoicePaymentService:
    payment_repo = SQLAlchemyInvoicePaymentRepository(session)
    invoice_repo = SQLAlchemyInvoiceRepository(session)
    return InvoicePaymentService(payment_repo, invoice_repo)


def get_receipt_service(session: AsyncSessionLocal = Depends(get_session)) -> ReceiptService:
    payment_repo = SQLAlchemyInvoicePaymentRepository(session)
    return ReceiptService(payment_repo)


def map_payment_response(payment: InvoicePayment) -> InvoicePaymentResponse:
    res = InvoicePaymentResponse.model_validate(payment)
    
    invoice = getattr(payment, "invoice", None)
    if invoice:
        res.invoice_number = invoice.invoice_number
        trip = getattr(invoice, "trip", None)
        party = getattr(invoice, "party", None)
        
        if trip:
            res.trip_number = trip.trip_number
        if party:
            res.party_name = party.name
            
    receiver = getattr(payment, "receiver", None)
    if receiver:
        res.received_by_name = receiver.name
        
    return res


@router.get(
    "/dashboard",
    response_model=APIResponse[InvoicePaymentDashboardResponse],
    dependencies=[Depends(PermissionChecker("invoice_payments:read"))],
    summary="Get invoice payment dashboard metrics",
)
async def get_dashboard(
    service: InvoicePaymentService = Depends(get_invoice_payment_service),
) -> Any:
    metrics = await service.get_dashboard_metrics()
    source_breakdown = await service.get_payment_source_breakdown()
    
    metrics["payment_source_breakdown"] = source_breakdown
    response_data = InvoicePaymentDashboardResponse(**metrics)
    
    return APIResponse(
        success=True,
        message="Dashboard metrics retrieved successfully",
        data=response_data,
    )


@router.post(
    "",
    response_model=APIResponse[InvoicePaymentResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("invoice_payments:create"))],
    summary="Record a new invoice payment",
)
async def create_payment(
    data: InvoicePaymentCreate,
    current_user: User = Depends(get_current_active_user),
    service: InvoicePaymentService = Depends(get_invoice_payment_service),
) -> Any:
    payment = await service.create_payment(data, current_user.id)
    return APIResponse(
        success=True,
        message="Invoice payment recorded successfully",
        data=map_payment_response(payment),
    )


@router.get(
    "",
    response_model=APIResponse[PaginatedData[InvoicePaymentResponse]],
    summary="List invoice payments",
    dependencies=[Depends(PermissionChecker("invoice_payments:read"))],
)
async def list_payments(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Records to return"),
    search: str | None = Query(None, description="Search term"),
    invoice_id: uuid.UUID | None = Query(None, description="Filter by Invoice ID"),
    party_id: uuid.UUID | None = Query(None, description="Filter by Party ID"),
    payment_status: str | None = Query(None, description="Filter by payment status"),
    payment_source: str | None = Query(None, description="Filter by payment source"),
    sort_by: str | None = Query(None, description="Column to sort by"),
    sort_desc: bool = Query(True, description="Sort descending"),
    service: InvoicePaymentService = Depends(get_invoice_payment_service),
) -> Any:
    payments, total = await service.list_payments(
        skip=skip,
        limit=limit,
        search=search,
        invoice_id=invoice_id,
        party_id=party_id,
        payment_status=payment_status,
        payment_source=payment_source,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )
    
    data = [map_payment_response(p) for p in payments]
    return APIResponse(
        success=True,
        message="Payments retrieved successfully",
        data=PaginatedData(items=data, total=total, skip=skip, limit=limit),
    )


@router.get(
    "/{id}",
    response_model=APIResponse[InvoicePaymentResponse],
    summary="Get invoice payment by ID",
    dependencies=[Depends(PermissionChecker("invoice_payments:read"))],
)
async def get_payment(
    id: uuid.UUID,
    service: InvoicePaymentService = Depends(get_invoice_payment_service),
) -> Any:
    payment = await service.get_payment(id)
    return APIResponse(
        success=True,
        message="Payment retrieved successfully",
        data=map_payment_response(payment),
    )


@router.get(
    "/receipt/{id}",
    response_model=APIResponse[ReceiptResponse],
    summary="Get printable receipt for a payment",
    dependencies=[Depends(PermissionChecker("invoice_payments:read"))],
)
async def get_receipt(
    id: uuid.UUID,
    service: ReceiptService = Depends(get_receipt_service),
) -> Any:
    receipt = await service.generate_receipt_json(id)
    return APIResponse(
        success=True,
        message="Receipt generated successfully",
        data=receipt,
    )


@router.put(
    "/{id}",
    response_model=APIResponse[InvoicePaymentResponse],
    summary="Update invoice payment remarks",
    dependencies=[Depends(PermissionChecker("invoice_payments:update"))],
)
async def update_payment(
    id: uuid.UUID,
    data: InvoicePaymentUpdate,
    current_user: User = Depends(get_current_active_user),
    service: InvoicePaymentService = Depends(get_invoice_payment_service),
) -> Any:
    payment = await service.update_payment(id, data, current_user.id)
    return APIResponse(
        success=True,
        message="Payment updated successfully",
        data=map_payment_response(payment),
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    summary="Soft delete an invoice payment",
    dependencies=[Depends(PermissionChecker("invoice_payments:delete"))],
)
async def delete_payment(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: InvoicePaymentService = Depends(get_invoice_payment_service),
) -> Any:
    await service.delete_payment(id, current_user.id)
    return APIResponse(
        success=True,
        message="Payment deleted successfully",
        data=None,
    )


@router.patch(
    "/{id}/restore",
    response_model=APIResponse[InvoicePaymentResponse],
    summary="Restore a soft-deleted payment",
    dependencies=[Depends(PermissionChecker("invoice_payments:update"))],
)
async def restore_payment(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: InvoicePaymentService = Depends(get_invoice_payment_service),
) -> Any:
    payment = await service.restore_payment(id, current_user.id)
    return APIResponse(
        success=True,
        message="Payment restored successfully",
        data=map_payment_response(payment),
    )
