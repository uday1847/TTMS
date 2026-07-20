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

    async def get_all_roles(self) -> Sequence[Role]:
        roles, _ = await self.role_repository.list_roles(0, 1000)
        return roles

    async def create_role(self, dto: RoleCreate, current_user_id: uuid.UUID | None = None) -> Role:
        role = Role(name=dto.name, display_name=dto.display_name, description=dto.description)
        if dto.permission_ids:
            permissions = await self.permission_repository.get_by_ids(dto.permission_ids)
            role.permissions = permissions
        if current_user_id:
            role.created_by = current_user_id
        return await self.role_repository.create(role)

    async def update_role(self, role_id: uuid.UUID, dto: RoleUpdate, current_user_id: uuid.UUID | None = None) -> Role:
        role = await self.get_role_by_id(role_id)
        if dto.name is not None:
            role.name = dto.name
        if dto.display_name is not None:
            role.display_name = dto.display_name
        if dto.description is not None:
            role.description = dto.description
        if dto.permission_ids is not None:
            permissions = await self.permission_repository.get_by_ids(dto.permission_ids)
            role.permissions = permissions
        
        if current_user_id:
            role.updated_by = current_user_id
            
        updated_role = await self.role_repository.update(role)
        PermissionCacheService.invalidate_all_permissions()
        return updated_role

    async def delete_role(self, role_id: uuid.UUID, deleted_by: uuid.UUID | None = None) -> bool:
        role = await self.get_role_by_id(role_id)
        if deleted_by:
            role.deleted_by = deleted_by
            await self.role_repository.update(role)
        await self.role_repository.delete(role_id)
        PermissionCacheService.invalidate_all_permissions()
        return True
        
    async def assign_permission_to_role(self, role_id: uuid.UUID, permission_code: str, current_user_id: uuid.UUID | None = None) -> Role:
        role = await self.get_role_by_id(role_id)
        permission = await self.permission_repository.get_by_code(permission_code)
        if not permission:
            raise ResourceNotFoundException(f"Permission '{permission_code}' not found")
        
        if not any(p.id == permission.id for p in role.permissions):
            role.permissions.append(permission)
            if current_user_id:
                role.updated_by = current_user_id
            updated_role = await self.role_repository.update(role)
            PermissionCacheService.invalidate_all_permissions()
            return updated_role
        return role

    async def remove_permission_from_role(self, role_id: uuid.UUID, permission_code: str, current_user_id: uuid.UUID | None = None) -> Role:
        role = await self.get_role_by_id(role_id)
        permission = await self.permission_repository.get_by_code(permission_code)
        if not permission:
            raise ResourceNotFoundException(f"Permission '{permission_code}' not found")
            
        initial_count = len(role.permissions)
        role.permissions = [p for p in role.permissions if p.id != permission.id]
        
        if len(role.permissions) < initial_count:
            if current_user_id:
                role.updated_by = current_user_id
            updated_role = await self.role_repository.update(role)
            PermissionCacheService.invalidate_all_permissions()
            return updated_role
        return role
