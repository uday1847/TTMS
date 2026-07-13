from datetime import datetime, timezone
import logging
from typing import Sequence
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.domain.entities.role import Role
from app.domain.exceptions.auth import RoleNotFoundException
from app.domain.repositories.permission_repository import PermissionRepository
from app.domain.repositories.role_repository import RoleRepository

logger = logging.getLogger("ttms.role_service")


class RoleService:
    """
    Service layer orchestrating roles, descriptions, and permission mapping links.
    """

    def __init__(
        self,
        session: AsyncSession,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
    ) -> None:
        self.session = session
        self.role_repository = role_repository
        self.permission_repository = permission_repository

    async def create_role(
        self, name: str, display_name: str, description: str | None, current_user_id: uuid.UUID
    ) -> Role:
        """
        Creates a new role definition.
        """
        logger.info(f"Creating role name: {name}")
        normalized_name = name.lower().strip()

        async with self.session.begin():
            existing = await self.role_repository.get_by_name(normalized_name)
            if existing:
                raise ValueError(f"Role name '{name}' is already defined.")

            role = Role(
                name=normalized_name,
                display_name=display_name,
                description=description,
                created_by=current_user_id,
                updated_by=current_user_id,
                is_active=True,
            )
            await self.role_repository.create(role)

        logger.info(f"Role '{normalized_name}' created (ID: {role.id}).")
        return role

    async def get_role_by_id(self, role_id: uuid.UUID) -> Role:
        """
        Retrieves a role by ID.
        """
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id, Role.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise RoleNotFoundException(str(role_id))
        return role

    async def get_all_roles(self) -> Sequence[Role]:
        """
        Loads all active roles with loaded permissions.
        """
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_role(self, role_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """
        Soft-deletes a role.
        """
        logger.info(f"Soft deleting role ID: {role_id}")
        async with self.session.begin():
            role = await self.role_repository.get_by_id(role_id)
            if not role:
                raise RoleNotFoundException(str(role_id))

            role.updated_by = current_user_id
            role.updated_at = datetime.now(timezone.utc)
            await self.role_repository.delete(role_id, soft=True)

        logger.info(f"Role {role_id} successfully deleted.")
        return True

    async def assign_permission_to_role(
        self, role_id: uuid.UUID, permission_code: str, current_user_id: uuid.UUID
    ) -> Role:
        """
        Assigns a permission code to a role.
        """
        logger.info(f"Assigning permission '{permission_code}' to role: {role_id}")

        async with self.session.begin():
            # Load role
            stmt = (
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == role_id, Role.deleted_at.is_(None))
            )
            result = await self.session.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                raise RoleNotFoundException(str(role_id))

            # Load permission
            permission = await self.permission_repository.get_by_code(permission_code)
            if not permission:
                raise ValueError(f"Permission code '{permission_code}' does not exist.")

            if permission not in role.permissions:
                role.permissions.append(permission)
                role.updated_by = current_user_id
                role.updated_at = datetime.now(timezone.utc)
                await self.role_repository.update(role)

        logger.info(f"Permission '{permission_code}' bound to role '{role.name}'.")
        return role

    async def remove_permission_from_role(
        self, role_id: uuid.UUID, permission_code: str, current_user_id: uuid.UUID
    ) -> Role:
        """
        Removes a permission code from a role.
        """
        logger.info(f"Removing permission '{permission_code}' from role: {role_id}")

        async with self.session.begin():
            stmt = (
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == role_id, Role.deleted_at.is_(None))
            )
            result = await self.session.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                raise RoleNotFoundException(str(role_id))

            permission = await self.permission_repository.get_by_code(permission_code)
            if not permission:
                raise ValueError(f"Permission code '{permission_code}' does not exist.")

            if permission in role.permissions:
                role.permissions.remove(permission)
                role.updated_by = current_user_id
                role.updated_at = datetime.now(timezone.utc)
                await self.role_repository.update(role)

        logger.info(f"Permission '{permission_code}' removed from role '{role.name}'.")
        return role
