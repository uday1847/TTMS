from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Query, status, Request
from fastapi.responses import JSONResponse

from app.api.dependencies.auth import get_current_active_user, get_user_service
from app.api.dependencies.permissions import PermissionChecker
from app.domain.entities.user import User
from app.application.services.user_service import UserService
from app.schemas.response import APIResponse, PaginatedData
from app.application.dtos.audit import AuditContext
from app.application.dtos.users import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserRoleUpdate,
    UserPermissionOverrideUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=APIResponse[PaginatedData[UserResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:read"))],
    summary="Get paginated list of users with search support",
)
async def list_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    size: int = Query(default=10, ge=1, le=100, description="Items per page limit."),
    q: str | None = Query(default=None, description="Search query string matching email, username, or name."),
) -> APIResponse[PaginatedData[UserResponse]]:
    """
    Retrieves a paginated list of users. If a query 'q' is provided, performs a text-based search.
    """
    skip = (page - 1) * size
    items, total = await user_service.list_users(skip, size, search=q)

    data = PaginatedData(
        items=[UserResponse.model_validate(u) for u in items],
        total=total,
        page=page,
        size=size,
    )
    return APIResponse(
        success=True,
        message="Users listed successfully.",
        data=data,
    )


@router.get(
    "/{id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:read"))],
    summary="Get user details by ID",
)
async def get_user(
    id: uuid.UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Retrieves user profile details and role configurations by ID.
    """
    user = await user_service.get_user_by_id(id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "User not found.", "data": None},
        )
    return APIResponse(
        success=True,
        message="User details retrieved successfully.",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("users:create"))],
    summary="Create a new user profile",
)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Enables administrators to register new users in the system.
    """
    created_user = await user_service.create_user(dto=user_data, current_user_id=current_user.id)
    
    return APIResponse(
        success=True,
        message="User profile created successfully.",
        data=created_user,
    )


@router.put(
    "/{id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:update"))],
    summary="Update user details",
)
async def update_user(
    request: Request,
    id: uuid.UUID,
    dto: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Updates profile values of a user.
    """
    audit_context = AuditContext(actor_id=current_user.id, actor_email=current_user.email, ip_address=request.client.host if request.client else None, user_agent=request.headers.get("user-agent"))
    user = await user_service.update_user(user_id=id, dto=dto, audit_context=audit_context)
    response_dto = await user_service.get_user_with_access_profile(id)

    return APIResponse(
        success=True,
        message="User profile updated successfully.",
        data=UserResponse.model_validate(response_dto),
    )


@router.patch(
    "/{id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:update"))],
    summary="Partially update user details",
)
async def patch_user(
    request: Request,
    id: uuid.UUID,
    dto: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Performs partial updates on user details.
    """
    audit_context = AuditContext(actor_id=current_user.id, actor_email=current_user.email, ip_address=request.client.host if request.client else None, user_agent=request.headers.get("user-agent"))
    user = await user_service.update_user(user_id=id, dto=dto, audit_context=audit_context)
    response_dto = await user_service.get_user_with_access_profile(id)
    return APIResponse(
        success=True,
        message="User profile updated successfully.",
        data=UserResponse.model_validate(response_dto),
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:delete"))],
    summary="Soft-delete user account",
)

@router.delete(
    '/{id}',
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker('users:delete'))],
)
async def delete_user(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[None]:

    await user_service.delete_user(
        user_id=id,
        deleted_by=current_user.id,
    )

    return APIResponse(
        success=True,
        message='User deleted successfully.',
        data=None,
    )


@router.post(
    "/{id}/roles/{role_name}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:role_assign"))],
    summary="Assign a role to user",
)
async def assign_user_role(
    request: Request,
    id: uuid.UUID,
    role_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Assigns an authorization role group to a user account.
    """
    audit_context = AuditContext(actor_id=current_user.id, actor_email=current_user.email, ip_address=request.client.host if request.client else None, user_agent=request.headers.get("user-agent"))
    user = await user_service.assign_role(id, role_name, audit_context=audit_context)
    return APIResponse(
        success=True,
        message=f"Role '{role_name}' assigned to user successfully.",
        data=UserResponse.model_validate(user),
    )


@router.delete(
    "/{id}/roles/{role_name}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:role_assign"))],
    summary="Remove a role from user",
)
async def remove_user_role(
    request: Request,
    id: uuid.UUID,
    role_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Revokes an authorization role group from a user account.
    """
    audit_context = AuditContext(actor_id=current_user.id, actor_email=current_user.email, ip_address=request.client.host if request.client else None, user_agent=request.headers.get("user-agent"))
    user = await user_service.remove_role(id, role_name, audit_context=audit_context)
    return APIResponse(
        success=True,
        message=f"Role '{role_name}' removed from user successfully.",
        data=UserResponse.model_validate(user),
    )


@router.get(
    "/{id}/access-profile",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:read"))],
    summary="Get user access profile",
)
async def get_user_access_profile(
    id: uuid.UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Retrieves a user's full access profile, including roles, effective permissions, and direct overrides.
    """
    dto = await user_service.get_user_with_access_profile(id)
    return APIResponse(
        success=True,
        message="User access profile retrieved successfully.",
        data=dto,
    )


@router.put(
    "/{id}/roles",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:role_assign"))],
    summary="Update user roles",
)
async def update_user_roles(
    request: Request,
    id: uuid.UUID,
    dto: UserRoleUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Updates the complete list of roles assigned to a user.
    """
    audit_context = AuditContext(actor_id=current_user.id, actor_email=current_user.email, ip_address=request.client.host if request.client else None, user_agent=request.headers.get("user-agent"))
    user = await user_service.update_user_roles(
        user_id=id, dto=dto, audit_context=audit_context
    )
    # Refresh to get populated access profile
    profile_dto = await user_service.get_user_with_access_profile(id)
    return APIResponse(
        success=True,
        message="User roles updated successfully.",
        data=profile_dto,
    )


@router.put(
    "/{id}/permissions",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("roles:permission_assign"))],
    summary="Update user permission overrides",
)
async def update_user_permission_overrides(
    request: Request,
    id: uuid.UUID,
    dto: UserPermissionOverrideUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Updates direct permission overrides (grants and revocations) for a user.
    """
    audit_context = AuditContext(actor_id=current_user.id, actor_email=current_user.email, ip_address=request.client.host if request.client else None, user_agent=request.headers.get("user-agent"))
    user = await user_service.update_user_permission_overrides(
        user_id=id, dto=dto, audit_context=audit_context
    )
    # Refresh to get populated access profile
    profile_dto = await user_service.get_user_with_access_profile(id)
    return APIResponse(
        success=True,
        message="User permission overrides updated successfully.",
        data=profile_dto,
    )


@router.get(
    "/{id}/effective-permissions",
    response_model=APIResponse[list[str]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("permissions:read"))],
    summary="Get user effective permissions",
)
async def get_effective_permissions(
    id: uuid.UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[list[str]]:
    """
    Returns a flat list of effective permissions for a user.
    """
    user = await user_service.get_user_by_id(id)
    perms = user_service._calculate_effective_permissions(user)
    return APIResponse(
        success=True,
        message="Effective permissions retrieved successfully.",
        data=perms,
    )
