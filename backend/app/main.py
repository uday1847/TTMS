import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.middleware.logging import RequestLoggingMiddleware
from app.api.router import api_router
from app.infrastructure.database.base import Base
from app.domain.exceptions.auth import (
    AuthenticationException,
    AuthorizationException,
    InvalidCredentialsException,
    PermissionDeniedException,
    RoleNotFoundException,
    TokenExpiredException,
    UserAlreadyExistsException,
)
from app.domain.exceptions.base import DomainException
from app.domain.exceptions.driver import DriverNotFoundException, DriverHasActiveTripsException, DriverAlreadyExistsException
from app.domain.exceptions.tractor import TractorNotFoundException, TractorAlreadyExistsException, TractorHasActiveTripsException
from app.domain.exceptions.party import PartyNotFoundException, PartyAlreadyExistsException, PartyHasActiveTripsException
from app.domain.exceptions.trip import (
    TripNotFoundException,
    TripAlreadyExistsException,
    TripStatusException,
    DriverBusyException,
    TractorBusyException,
    TripDeleteException,
    InactiveDriverException,
    InactiveTractorException,
    InactivePartyException,
    InvalidTripDateException,
    AdvanceAmountException,
    TripAlreadyCompletedException,
)
from app.domain.exceptions.trip_expense import (
    TripExpenseNotFoundException,
    TripCompletedException,
    TripCancelledException,
    TripExpenseValidationException,
)
from app.domain.exceptions.invoice import (
    InvoiceNotFoundException,
    InvoiceStatusException,
    InvoicePaymentException,
    InvoiceGenerationException,
    InvoiceAlreadyExistsException,
)
from app.domain.exceptions.invoice_payment import (
    InvoicePaymentNotFoundException,
    InvoicePaymentExceededException,
    InvoiceDraftException,
    InvoiceCancelledException,
    InvoiceAlreadyPaidException,
    InvoicePaymentValidationException,
    ReceiptNotFoundException,
)

# Configure structured logging globally
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("ttms.main")

# Initialize FastAPI App with OpenAPI documentation configuration
app = FastAPI(
    title="Transport Tractor Management System (TTMS)",
    description="Enterprise-grade tractor and trip management API built on Clean Architecture.",
    version="1.0.0",
)

# Register request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include central router
app.include_router(api_router)


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """
    Global exception mapper intercepting business exceptions and converting them
    to structured client-friendly API responses.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = exc.message

    if isinstance(exc, InvalidCredentialsException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, TokenExpiredException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthenticationException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, PermissionDeniedException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, AuthorizationException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, RoleNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DriverNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DriverHasActiveTripsException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, UserAlreadyExistsException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, DriverAlreadyExistsException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, TractorNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, TractorHasActiveTripsException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, TractorAlreadyExistsException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, PartyNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, PartyHasActiveTripsException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, PartyAlreadyExistsException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, TripNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, TripAlreadyExistsException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, (
        TripStatusException,
        DriverBusyException,
        TractorBusyException,
        TripDeleteException,
        InactiveDriverException,
        InactiveTractorException,
        InactivePartyException,
        InvalidTripDateException,
        AdvanceAmountException,
        TripAlreadyCompletedException,
        TripCompletedException,
        TripCancelledException,
        TripExpenseValidationException,
    )):
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, TripExpenseNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exc, InvoiceNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exc, InvoiceAlreadyExistsException):
        status_code = status.HTTP_409_CONFLICT

    elif isinstance(exc, (
        InvoiceStatusException,
        InvoicePaymentException,
        InvoiceGenerationException,
        InvoicePaymentExceededException,
        InvoiceDraftException,
        InvoiceCancelledException,
        InvoiceAlreadyPaidException,
        InvoicePaymentValidationException,
    )):
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, InvoicePaymentNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exc, ReceiptNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND

    logger.warning(
        f"Domain exception intercepted: type={exc.__class__.__name__} | "
        f"message={message} | mapped_status={status_code}"
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": None,
        },
    )


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """
    Service health probe endpoint.
    """
    return {"status": "healthy", "service": "Transport Tractor Management System"}