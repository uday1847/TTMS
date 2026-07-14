import uuid
from typing import Sequence
from app.domain.entities.role import Role
from app.domain.repositories.role_repository import RoleRepository
from app.domain.repositories.permission_repository import PermissionRepository
from app.application.dtos.roles import RoleCreate, RoleUpdate
from app.application.services.permission_cache_service import PermissionCacheService
from app.domain.exceptions.base import ResourceNotFoundException

class RoleService:
    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository
    ):
        self.role_repository = role_repository
        self.permission_repository = permission_repository

    async def get_role_by_id(self, role_id: uuid.UUID) -> Role:
        role = await self.role_repository.get_by_id(role_id)
        if not role:
            raise ResourceNotFoundException("Role not found")
        return role

    async def list_roles(self, skip: int = 0, limit: int = 100) -> tuple[Sequence[Role], int]:
        return await self.role_repository.list_roles(skip, limit)

    async def create_role(self, dto: RoleCreate) -> Role:
        role = Role(name=dto.name, description=dto.description)
        if dto.permission_ids:
            permissions = await self.permission_repository.get_by_ids(dto.permission_ids)
            role.permissions = permissions
        return await self.role_repository.create(role)

    async def update_role(self, role_id: uuid.UUID, dto: RoleUpdate) -> Role:
        role = await self.get_role_by_id(role_id)
        if dto.name is not None:
            role.name = dto.name
        if dto.description is not None:
            role.description = dto.description
        if dto.permission_ids is not None:
            permissions = await self.permission_repository.get_by_ids(dto.permission_ids)
            role.permissions = permissions
        
        updated_role = await self.role_repository.update(role)
        PermissionCacheService.invalidate_all_permissions() # Invalidate cache to reflect new role perms
        return updated_role

    async def delete_role(self, role_id: uuid.UUID, deleted_by: uuid.UUID | None = None) -> None:
        role = await self.get_role_by_id(role_id)
        await self.role_repository.delete(role, deleted_by=deleted_by)
        PermissionCacheService.invalidate_all_permissions()
