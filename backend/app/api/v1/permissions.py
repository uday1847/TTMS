from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_session
from app.api.dependencies.permissions import PermissionChecker
from app.infrastructure.repositories.permission_repository import SQLAlchemyPermissionRepository
from app.application.services.permission_service import PermissionService
from app.schemas.response import APIResponse
from app.schemas.user.permission_response import PermissionResponse

router = APIRouter(prefix="/permissions", tags=["Permissions"])


def get_permission_service(session: AsyncSession = Depends(get_session)) -> PermissionService:
    """
    Dependency injection factory constructing the PermissionService.
    """
    permission_repo = SQLAlchemyPermissionRepository(session)
    return PermissionService(session, permission_repo)


@router.get(
    "",
    response_model=APIResponse[list[PermissionResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("permissions:read"))],
    summary="Get all permissions",
)
async def list_permissions(
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> APIResponse[list[PermissionResponse]]:
    """
    Lists all defined permissions (system access rights).
    """
    permissions = await permission_service.get_all_permissions()
    return APIResponse(
        success=True,
        message="Permissions retrieved successfully.",
        data=[PermissionResponse.model_validate(p) for p in permissions],
    )
