from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_session
from app.api.dependencies.permissions import PermissionChecker
from app.domain.entities.user import User
from app.infrastructure.repositories.permission_repository import SQLAlchemyPermissionRepository
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.application.services.role_service import RoleService
from app.schemas.response import APIResponse
from app.schemas.user.role_response import RoleCreate, RoleResponse

router = APIRouter(prefix="/roles", tags=["Roles"])


def get_role_service(session: AsyncSession = Depends(get_session)) -> RoleService:
    """
    Dependency injection factory constructing the RoleService.
    """
    role_repo = SQLAlchemyRoleRepository(session)
    permission_repo = SQLAlchemyPermissionRepository(session)
    return RoleService(role_repo, permission_repo)


@router.get(
    "",
    response_model=APIResponse[list[RoleResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("roles:read"))],
    summary="Get all roles",
)
async def list_roles(
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> APIResponse[list[RoleResponse]]:
    """
    Lists all defined active roles.
    """
    roles = await role_service.get_all_roles()
    return APIResponse(
        success=True,
        message="Roles retrieved successfully.",
        data=[RoleResponse.model_validate(r) for r in roles],
    )


@router.post(
    "",
    response_model=APIResponse[RoleResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("roles:create"))],
    summary="Create a new role",
)
async def create_role(
    dto: RoleCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> APIResponse[RoleResponse]:
    """
    Registers a new authorization role definition in the system.
    """
    role = await role_service.create_role(
        dto=dto,
        current_user_id=current_user.id,
    )
    return APIResponse(
        success=True,
        message="Role created successfully.",
        data=RoleResponse.model_validate(role),
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("roles:delete"))],
    summary="Delete a role",
)
async def delete_role(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> APIResponse[None]:
    """
    Soft-deletes a role definition.
    """
    success = await role_service.delete_role(role_id=id, deleted_by=current_user.id)
    if not success:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "Role not found.", "data": None},
        )
    return APIResponse(
        success=True,
        message="Role has been deleted successfully.",
        data=None,
    )


@router.post(
    "/{id}/permissions/{permission_code}",
    response_model=APIResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("roles:permission_assign"))],
    summary="Assign permission to role",
)
async def assign_role_permission(
    id: uuid.UUID,
    permission_code: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> APIResponse[RoleResponse]:
    """
    Binds an access permission privilege to a role configuration.
    """
    role = await role_service.assign_permission_to_role(
        role_id=id,
        permission_code=permission_code,
        current_user_id=current_user.id,
    )
    return APIResponse(
        success=True,
        message=f"Permission '{permission_code}' assigned to role successfully.",
        data=RoleResponse.model_validate(role),
    )


@router.delete(
    "/{id}/permissions/{permission_code}",
    response_model=APIResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("roles:permission_assign"))],
    summary="Remove permission from role",
)
async def remove_role_permission(
    id: uuid.UUID,
    permission_code: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> APIResponse[RoleResponse]:
    """
    Unbinds an access permission privilege from a role configuration.
    """
    role = await role_service.remove_permission_from_role(
        role_id=id,
        permission_code=permission_code,
        current_user_id=current_user.id,
    )
    return APIResponse(
        success=True,
        message=f"Permission '{permission_code}' removed from role successfully.",
        data=RoleResponse.model_validate(role),
    )
