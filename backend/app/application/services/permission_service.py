import logging
from typing import Sequence
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.permission import Permission
from app.domain.repositories.permission_repository import PermissionRepository

logger = logging.getLogger("ttms.permission_service")


class PermissionService:
    """
    Service layer orchestrating permission catalogs and access codes.
    """

    def __init__(
        self,
        session: AsyncSession,
        permission_repository: PermissionRepository,
    ) -> None:
        self.session = session
        self.permission_repository = permission_repository

    async def create_permission(self, code: str, description: str | None, current_user_id: uuid.UUID) -> Permission:
        """
        Registers a new permission code (useful during seeding/initialization).
        """
        logger.info(f"Registering permission code: {code}")
        normalized_code = code.lower().strip()

        async with self.session.begin():
            existing = await self.permission_repository.get_by_code(normalized_code)
            if existing:
                raise ValueError(f"Permission code '{code}' already exists.")

            permission = Permission(
                code=normalized_code,
                description=description,
                created_by=current_user_id,
                updated_by=current_user_id,
                is_active=True,
            )
            await self.permission_repository.create(permission)

        logger.info(f"Permission '{normalized_code}' registered (ID: {permission.id}).")
        return permission

    async def get_all_permissions(self) -> Sequence[Permission]:
        """
        Loads all active privileges.
        """
        return await self.permission_repository.get_all()
