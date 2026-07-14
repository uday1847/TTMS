import uuid
from typing import Sequence
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.role_repository import RoleRepository
from app.application.dtos.users import UserCreate, UserUpdate
from app.application.services.permission_cache_service import PermissionCacheService
from app.core.security import security_settings
from app.domain.exceptions.base import ResourceNotFoundException, ValidationException
from app.domain.enums.user_status import UserStatus

class UserService:
    def __init__(self, user_repository: UserRepository, role_repository: RoleRepository):
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.user_repository.get_with_roles_and_permissions(user_id)
        if not user:
            raise ResourceNotFoundException("User not found")
        return user

    async def create_user(self, dto: UserCreate) -> User:
        existing = await self.user_repository.get_by_email(dto.email)
        if existing:
            raise ValidationException("Email already exists")
            
        hashed_password = security_settings.get_password_hash(dto.password)
        user = User(
            email=dto.email,
            username=dto.username,
            password_hash=hashed_password,
            first_name=dto.first_name,
            last_name=dto.last_name,
            phone=dto.phone,
            status=UserStatus.ACTIVE
        )
        if dto.role_ids:
            for role_id in dto.role_ids:
                role = await self.role_repository.get_by_id(role_id)
                if role:
                    user.roles.append(role)
        return await self.user_repository.create(user)

    async def update_user(self, user_id: uuid.UUID, dto: UserUpdate) -> User:
        user = await self.get_user_by_id(user_id)
        if dto.first_name is not None:
            user.first_name = dto.first_name
        if dto.last_name is not None:
            user.last_name = dto.last_name
        if dto.phone is not None:
            user.phone = dto.phone
        if dto.profile_picture_url is not None:
            user.profile_picture_url = dto.profile_picture_url
            
        if dto.role_ids is not None:
            user.roles = []
            for role_id in dto.role_ids:
                role = await self.role_repository.get_by_id(role_id)
                if role:
                    user.roles.append(role)
            PermissionCacheService.invalidate_user_permissions(str(user_id))
            user.token_version += 1 # Invalidate existing tokens on role change
            
        return await self.user_repository.update(user)

    async def lock_user(self, user_id: uuid.UUID) -> User:
        user = await self.get_user_by_id(user_id)
        user.status = UserStatus.LOCKED
        user.token_version += 1
        return await self.user_repository.update(user)

    async def unlock_user(self, user_id: uuid.UUID) -> User:
        user = await self.get_user_by_id(user_id)
        user.status = UserStatus.ACTIVE
        user.failed_login_attempts = 0
        user.locked_until = None
        return await self.user_repository.update(user)

    async def delete_user(self, user_id: uuid.UUID, deleted_by: uuid.UUID | None = None) -> None:
        user = await self.get_user_by_id(user_id)
        user.token_version += 1
        await self.user_repository.delete(user, deleted_by=deleted_by)
        
    async def list_users(self, skip: int = 0, limit: int = 100, search: str | None = None) -> tuple[Sequence[User], int]:
        return await self.user_repository.list_users(skip, limit, search)

    async def get_dashboard_stats(self) -> dict:
        total = await self.user_repository.get_total_count()
        active = await self.user_repository.get_active_count()
        locked = await self.user_repository.get_locked_count()
        return {
            "total_users": total,
            "active_users": active,
            "locked_users": locked,
            "inactive_users": total - active - locked
        }

    async def verify_user_permission(self, user_id: uuid.UUID, required_permission: str) -> bool:
        user = await self.get_user_by_id(user_id)
        for role in user.roles:
            for perm in role.permissions:
                if perm.name == required_permission:
                    return True
        return False

    async def verify_user_role(self, user_id: uuid.UUID, required_role: str) -> bool:
        user = await self.get_user_by_id(user_id)
        for role in user.roles:
            if role.name.lower() == required_role.lower():
                return True
        return False
