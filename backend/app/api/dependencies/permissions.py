from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.dependencies.auth import get_current_active_user, get_user_service
from app.domain.entities.user import User
from app.application.services.user_service import UserService


class PermissionChecker:
    """
    FastAPI dependency checker verifying that the current active user possesses
    the required privilege/permission.
    """

    def __init__(self, required_permission: str) -> None:
        self.required_permission = required_permission.lower().strip()

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_active_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
    ) -> None:
        has_permission = await user_service.verify_user_permission(current_user.id, self.required_permission)
        if not has_permission:
            # Phase 13 - Logging: Add structured logging for authorization failures
            import logging
            logger = logging.getLogger("auth")
            logger.warning(
                f"Authorization Failed - UserID: {current_user.id}, Email: {current_user.email}, "
                f"Required Permission: {self.required_permission}, Decision: Denied"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: lack required permission '{self.required_permission}'.",
            )


class RoleChecker:
    """
    FastAPI dependency checker verifying that the current active user possesses
    the required RBAC role.
    """

    def __init__(self, required_role: str) -> None:
        self.required_role = required_role.lower().strip()

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_active_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
    ) -> None:
        has_role = await user_service.verify_user_role(current_user.id, self.required_role)
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: lack required role '{self.required_role}'.",
            )
