from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.dependencies.auth import get_current_active_user, get_user_service
from app.api.dependencies.permissions import PermissionChecker
from app.domain.entities.user import User
from app.application.services.user_service import UserService
from app.schemas.response import APIResponse, PaginatedData
from app.schemas.user.user_create import UserCreate
from app.schemas.user.user_response import UserResponse
from app.schemas.user.user_update import UserUpdate

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
    dto: UserCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Enables administrators to register new users in the system.
    """
    user = await user_service.register_user(dto, current_user_id=current_user.id)
    return APIResponse(
        success=True,
        message="User profile created successfully.",
        data=UserResponse.model_validate(user),
    )


@router.put(
    "/{id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:update"))],
    summary="Update user details",
)
async def update_user(
    id: uuid.UUID,
    dto: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Updates profile values of a user.
    """
    user = await user_service.update_user(id, dto, current_user_id=current_user.id)
    return APIResponse(
        success=True,
        message="User profile updated successfully.",
        data=UserResponse.model_validate(user),
    )


@router.patch(
    "/{id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:update"))],
    summary="Partially update user details",
)
async def patch_user(
    id: uuid.UUID,
    dto: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Performs partial updates on user details.
    """
    user = await user_service.update_user(id, dto, current_user_id=current_user.id)
    return APIResponse(
        success=True,
        message="User profile updated successfully.",
        data=UserResponse.model_validate(user),
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker("users:delete"))],
    summary="Soft-delete user account",
)
async def delete_user(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[None]:
    """
    Soft-deletes a user profile and revokes all active session refresh tokens.
    """
    success = await user_service.delete_user(id, current_user_id=current_user.id)
    if not success:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "User not found.", "data": None},
        )
    return APIResponse(
        success=True,
        message="User profile has been soft deleted.",
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
    id: uuid.UUID,
    role_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Assigns an authorization role group to a user account.
    """
    user = await user_service.assign_role(id, role_name, current_user_id=current_user.id)
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
    id: uuid.UUID,
    role_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Revokes an authorization role group from a user account.
    """
    user = await user_service.remove_role(id, role_name, current_user_id=current_user.id)
    return APIResponse(
        success=True,
        message=f"Role '{role_name}' removed from user successfully.",
        data=UserResponse.model_validate(user),
    )
