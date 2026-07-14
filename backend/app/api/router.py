from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.drivers import router as drivers_router
from app.api.v1.tractors import router as tractors_router
from app.api.v1.parties import router as parties_router
from app.api.v1.trips import router as trips_router
from app.api.v1.trip_expenses import router as trip_expenses_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.invoice_payments import router as invoice_payments_router
from app.api.v1.maintenances import router as maintenances_router
from app.api.v1.fuel_vendors import router as fuel_vendors_router
from app.api.v1.fuel_transactions import router as fuel_transactions_router
from app.api.v1.reports import router as reports_router
from app.api.v1.auth import router as auth_router
from app.api.v1.login_history import router as login_history_router
from app.api.v1.audit import router as audit_router
from app.api.v1.sessions import router as sessions_router

# Central API Router under v1 namespace
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(permissions_router)
api_router.include_router(drivers_router)
api_router.include_router(tractors_router)
api_router.include_router(parties_router)
api_router.include_router(trips_router)
api_router.include_router(trip_expenses_router)
api_router.include_router(invoices_router)
api_router.include_router(invoice_payments_router)
api_router.include_router(maintenances_router)
api_router.include_router(fuel_vendors_router)
api_router.include_router(fuel_transactions_router)
api_router.include_router(reports_router)
api_router.include_router(auth_router)
api_router.include_router(login_history_router)
api_router.include_router(audit_router)
api_router.include_router(sessions_router)
