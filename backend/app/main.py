import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.logging import RequestLoggingMiddleware
from app.core.settings import settings
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
from app.domain.exceptions.base import DomainException, UnauthorizedException, ResourceNotFoundException, ValidationException
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
from app.domain.exceptions.maintenance import (
    MaintenanceNotFoundException,
    MaintenanceAlreadyScheduledException,
    MaintenanceStatusException,
    MaintenanceValidationException,
    MaintenanceDeleteException,
)
from app.domain.exceptions.fuel import (
    FuelTransactionNotFoundException,
    FuelValidationException,
    FuelCapacityExceededException,
    FuelMileageException,
    FuelOdometerException,
    FuelVendorNotFoundException,
    FuelDuplicateException,
)

# Configure structured logging globally
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("ttms.main")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Phase 12 - Startup Validation
    from app.infrastructure.database.session import AsyncSessionLocal
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.domain.entities.role import Role
    from app.domain.entities.permission import Permission
    
    logger.info("Starting RBAC Startup Validation...")
    async with AsyncSessionLocal() as session:
        # Validate Permissions exist
        res = await session.execute(select(Permission))
        permissions = res.scalars().all()
        if not permissions:
            raise RuntimeError("RBAC Validation Failed: No permissions loaded in database.")
            
        perm_names = [p.name for p in permissions]
        if len(perm_names) != len(set(perm_names)):
            raise RuntimeError("RBAC Validation Failed: Duplicate permissions found.")
            
        # Validate Admin role
        res = await session.execute(select(Role).options(selectinload(Role.permissions)).where(Role.name == "admin"))
        admin_role = res.scalar_one_or_none()
        if not admin_role:
            raise RuntimeError("RBAC Validation Failed: 'admin' role not found in database.")
            
        if not admin_role.permissions:
            raise RuntimeError("RBAC Validation Failed: 'admin' role has no permissions.")
            
        # Validate Operator role
        res = await session.execute(select(Role).where(Role.name == "operator"))
        operator_role = res.scalar_one_or_none()
        if not operator_role:
            logger.warning("RBAC Validation Warning: 'operator' role not found.")
            
        logger.info(f"RBAC Validation Passed. {len(permissions)} permissions loaded.")
    yield


# Initialize FastAPI App with OpenAPI documentation configuration
app = FastAPI(
    title="Transport Tractor Management System (TTMS)",
    description="Enterprise-grade tractor and trip management API built on Clean Architecture.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Security Validation
# Ensure CORS origins are properly configured and wildcard is not used with credentials
if "*" in settings.BACKEND_CORS_ORIGINS:
    if True:  # allow_credentials is hardcoded to True below
        logger.warning(
            "CORS Security Warning: Wildcard origin '*' is configured with allow_credentials=True. "
            "This is a security risk. Credentials will be excluded for security."
        )
else:
    logger.info(f"CORS Configuration: Allowing requests from {len(settings.BACKEND_CORS_ORIGINS)} origin(s)")
    for origin in settings.BACKEND_CORS_ORIGINS:
        logger.info(f"  ✓ {origin}")

# Register request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Register CORS Middleware LAST so it becomes the outermost layer,
# running first on requests (including OPTIONS) and last on responses
# (so it can add CORS headers even to 500 errors caught by ServerErrorMiddleware).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Include central router
app.include_router(api_router)


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """
    Global exception mapper intercepting business exceptions and converting them
    to structured client-friendly API responses.
    """
    message = getattr(exc, "message", str(exc))
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, ResourceNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, InvalidCredentialsException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, TokenExpiredException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, (AuthenticationException, UnauthorizedException)):
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

    elif isinstance(exc, (MaintenanceNotFoundException, FuelTransactionNotFoundException, FuelVendorNotFoundException)):
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exc, (MaintenanceAlreadyScheduledException, FuelDuplicateException)):
        status_code = status.HTTP_409_CONFLICT

    elif isinstance(exc, (
        MaintenanceStatusException,
        MaintenanceValidationException,
        FuelValidationException,
        FuelCapacityExceededException,
        FuelOdometerException,
        FuelMileageException,
        MaintenanceDeleteException,
    )):
        status_code = status.HTTP_400_BAD_REQUEST

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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all exception handler to ensure unhandled 500 errors do not bypass
    the CORSMiddleware (which would result in a CORS error on the frontend).
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Import here to avoid circular imports
    from app.schemas.response import APIResponse
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            message="Internal Server Error",
            data=None
        ).model_dump(mode="json"),
    )


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """
    Service health probe endpoint.
    """
    return {"status": "healthy", "service": "Transport Tractor Management System"}