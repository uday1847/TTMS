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
