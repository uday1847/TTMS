from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.permissions import router as permissions_router

# Central API Router under v1 namespace
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(permissions_router)
