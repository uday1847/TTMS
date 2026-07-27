import uuid
from typing import Sequence
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.role_repository import RoleRepository
from app.application.dtos.users import UserCreate, UserUpdate, UserRoleUpdate, UserPermissionOverrideUpdate, UserResponse
from app.application.dtos.audit import AuditContext
from app.application.services.audit_service import AuditService
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.permission_module import PermissionModule
from app.domain.entities.user_permission import UserPermission
from app.application.services.permission_cache_service import PermissionCacheService
from app.core.security import security_settings
from app.domain.exceptions.base import ResourceNotFoundException, ValidationException
from app.domain.enums.user_status import UserStatus

class UserService:
    def __init__(self, user_repository: UserRepository, role_repository: RoleRepository, audit_service: AuditService):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.audit_service = audit_service

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.user_repository.get_with_roles_and_permissions(user_id)
        if not user:
            raise ResourceNotFoundException("User not found")
        return user

    def _calculate_effective_permissions(self, user: User) -> list[str]:
        effective = set()
        
        for role in user.roles:
            for perm in getattr(role, 'permissions', []):
                effective.add(perm.name)
                
        for up in getattr(user, 'direct_permissions', []):
            if up.permission:
                if up.is_granted:
                    effective.add(up.permission.name)
                else:
                    effective.discard(up.permission.name)
                    
        return sorted(list(effective))

    async def get_user_with_access_profile(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.get_user_by_id(user_id)
        
        effective_permissions = self._calculate_effective_permissions(user)
        direct_permissions = []
        for up in getattr(user, 'direct_permissions', []):
            if up.permission and up.is_granted:
                direct_permissions.append(up.permission.name)
        
        dto = UserResponse.model_validate(user)
        dto.effective_permissions = effective_permissions
        dto.direct_permissions = sorted(direct_permissions)
        return dto

    async def create_user(self, dto: UserCreate, current_user_id: uuid.UUID | None = None) -> UserResponse:
        import logging
        from sqlalchemy.exc import IntegrityError
        from app.domain.exceptions.auth import UserAlreadyExistsException

        logger = logging.getLogger(__name__)

        logger.info("Create user request received", extra={"email": dto.email, "username": dto.username})

        existing_email = await self.user_repository.get_by_email(dto.email)
        if existing_email:
            logger.warning("Duplicate email detected", extra={"email": dto.email})
            raise UserAlreadyExistsException("Email already exists")

        existing_username = await self.user_repository.get_by_username(dto.username)
        if existing_username:
            logger.warning("Duplicate username detected", extra={"username": dto.username})
            raise UserAlreadyExistsException(f"Username '{dto.username}' is already registered")

        missing_roles = []
        roles_to_assign = []
        for role_id in dto.role_ids or []:
            role = await self.role_repository.get_by_id(role_id)
            if not role:
                missing_roles.append(str(role_id))
            else:
                roles_to_assign.append(role)

        if missing_roles:
            raise ValidationException(f"Invalid role IDs: {', '.join(missing_roles)}")

        hashed_password = security_settings.get_password_hash(dto.password)
        logger.info("Password hashed successfully", extra={"username": dto.username})

        user = User(
            email=dto.email,
            username=dto.username,
            password_hash=hashed_password,
            first_name=dto.first_name,
            last_name=dto.last_name,
            phone=dto.phone,
            status=UserStatus.ACTIVE
        )
        
        if current_user_id is not None:
            user.created_by = current_user_id

        logger.info("Assigning roles", extra={"role_ids": [str(r) for r in dto.role_ids or []]})
        user.roles = roles_to_assign

        session = self.user_repository.session
        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            logger.info("Database transaction committed", extra={"user_id": str(user.id)})
            logger.info("User created successfully", extra={"user_id": str(user.id)})
            
        except IntegrityError as exc:
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            raise

        return await self.get_user_with_access_profile(user.id)

    async def update_user(self, user_id: uuid.UUID, dto: UserUpdate, audit_context: AuditContext | None = None) -> User:
        user = await self.get_user_by_id(user_id)
        
        security_changed = False
        
        if dto.first_name is not None:
            user.first_name = dto.first_name
        if dto.last_name is not None:
            user.last_name = dto.last_name
        if dto.email is not None and dto.email != user.email:
            user.email = dto.email
            security_changed = True
        if dto.username is not None and dto.username != user.username:
            user.username = dto.username
            security_changed = True
        if dto.phone is not None:
            user.phone = dto.phone
        if dto.is_active is not None:
            new_status = UserStatus.ACTIVE if dto.is_active else UserStatus.INACTIVE
            if user.status != new_status:
                user.status = new_status
                security_changed = True
            
        if dto.role_ids is not None:
            user.roles = []
            for role_id in dto.role_ids:
                role = await self.role_repository.get_by_id(role_id)
                if role:
                    user.roles.append(role)
            PermissionCacheService.invalidate_user_permissions(str(user_id))
            security_changed = True
            
        if security_changed:
            user.token_version += 1
            
        if audit_context is not None:
            user.updated_by = audit_context.actor_id
            if security_changed:
                await self.audit_service.log_action(
                    action=AuditAction.UPDATE,
                    module=PermissionModule.USERS,
                    table_name="users",
                    record_id=user.id,
                    new_values={"token_version": user.token_version, "event": "SECURITY_STATE_CHANGED"},
                    user_id=audit_context.actor_id,
                    ip_address=audit_context.ip_address,
                    user_agent=audit_context.user_agent
                )
            
        return await self.user_repository.update(user)

    async def lock_user(self, user_id: uuid.UUID, audit_context: AuditContext | None = None) -> User:
        user = await self.get_user_by_id(user_id)
        user.status = UserStatus.LOCKED
        user.token_version += 1
        if audit_context is not None:
            user.updated_by = audit_context.actor_id
        return await self.user_repository.update(user)

    async def unlock_user(self, user_id: uuid.UUID, audit_context: AuditContext | None = None) -> User:
        user = await self.get_user_by_id(user_id)
        user.status = UserStatus.ACTIVE
        user.failed_login_attempts = 0
        user.locked_until = None
        user.token_version += 1
        if audit_context is not None:
            user.updated_by = audit_context.actor_id
        return await self.user_repository.update(user)


    async def delete_user(
        self,
        user_id: uuid.UUID,
        deleted_by: uuid.UUID | None = None
    ) -> None:
        user = await self.get_user_by_id(user_id)
    
        # invalidate existing tokens
        user.token_version += 1
    
        # optional audit field
        if deleted_by and hasattr(user, 'updated_by'):
            user.updated_by = deleted_by
    
        # save token_version/update_by before deleting
        await self.user_repository.update(user)
    
        # pass ID, not entity
        await self.user_repository.delete(user.id)


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
        effective = self._calculate_effective_permissions(user)
        return required_permission in effective

    async def verify_user_role(self, user_id: uuid.UUID, required_role: str) -> bool:
        user = await self.get_user_by_id(user_id)
        for role in user.roles:
            if role.name.lower() == required_role.lower():
                return True
        return False

    async def assign_role(self, user_id: uuid.UUID, role_name: str, audit_context: AuditContext | None = None) -> User:
        user = await self.get_user_by_id(user_id)
        role = await self.role_repository.get_by_name(role_name)
        if not role:
            raise ResourceNotFoundException(f"Role '{role_name}' not found")
        
        if not any(r.id == role.id for r in user.roles):
            user.roles.append(role)
            if audit_context:
                user.updated_by = audit_context.actor_id
            user.token_version += 1
            PermissionCacheService.invalidate_user_permissions(str(user_id))
            return await self.user_repository.update(user)
        return user

    async def remove_role(self, user_id: uuid.UUID, role_name: str, audit_context: AuditContext | None = None) -> User:
        user = await self.get_user_by_id(user_id)
        role = await self.role_repository.get_by_name(role_name)
        if not role:
            raise ResourceNotFoundException(f"Role '{role_name}' not found")
            
        initial_count = len(user.roles)
        user.roles = [r for r in user.roles if r.id != role.id]
        
        if len(user.roles) < initial_count:
            if audit_context:
                user.updated_by = audit_context.actor_id
            user.token_version += 1
            PermissionCacheService.invalidate_user_permissions(str(user_id))
            return await self.user_repository.update(user)
        return user

    async def update_user_roles(self, *, user_id: uuid.UUID, dto: UserRoleUpdate, audit_context: AuditContext) -> User:
        target_user = await self.get_user_by_id(user_id)
        
        # Self-protection logic
        admin_role_name = "admin"
        had_admin = any(r.name == admin_role_name for r in target_user.roles)
        
        new_roles = []
        for role_id in dto.role_ids:
            role = await self.role_repository.get_by_id(role_id)
            if not role:
                raise ResourceNotFoundException(f"Role {role_id} not found")
            new_roles.append(role)
            
        will_have_admin = any(r.name == admin_role_name for r in new_roles)
        
        if target_user.id == audit_context.actor_id and had_admin and not will_have_admin:
            raise ValidationException("You cannot remove your own last administrator role.")
            
        target_user.roles = new_roles
        target_user.updated_by = audit_context.actor_id
        target_user.token_version += 1
        PermissionCacheService.invalidate_user_permissions(str(target_user.id))
        
        await self.audit_service.log_action(
            action=AuditAction.UPDATE,
            module=PermissionModule.USERS,
            table_name="users",
            record_id=target_user.id,
            new_values={"event": "ROLE_ASSIGNMENT_CHANGED", "token_version": target_user.token_version},
            user_id=audit_context.actor_id,
            ip_address=audit_context.ip_address,
            user_agent=audit_context.user_agent
        )
        
        return await self.user_repository.update(target_user)

    async def update_user_permission_overrides(self, *, user_id: uuid.UUID, dto: UserPermissionOverrideUpdate, audit_context: AuditContext) -> User:
        target_user = await self.get_user_by_id(user_id)
        
        from sqlalchemy import select
        from app.domain.entities.permission import Permission
        
        result = await self.user_repository.session.execute(select(Permission))
        all_permissions = result.scalars().all()
            
        perm_map = {p.name: p for p in all_permissions}
        
        # Verify requested permissions exist
        for p_name in dto.grant_permissions + dto.revoke_permissions:
            if p_name not in perm_map:
                raise ResourceNotFoundException(f"Permission '{p_name}' not found")
                
        # Remove existing overrides for these permissions if any, to cleanly apply new ones
        updated_override_names = set(dto.grant_permissions + dto.revoke_permissions)
        target_user.direct_permissions = [
            up for up in target_user.direct_permissions 
            if up.permission.name not in updated_override_names
        ]
        
        # Add new overrides
        for p_name in dto.grant_permissions:
            up = UserPermission(
                user_id=target_user.id,
                permission_id=perm_map[p_name].id,
                is_granted=True,
                created_by=audit_context.actor_id
            )
            up.permission = perm_map[p_name]
            target_user.direct_permissions.append(up)
            
        for p_name in dto.revoke_permissions:
            up = UserPermission(
                user_id=target_user.id,
                permission_id=perm_map[p_name].id,
                is_granted=False,
                created_by=audit_context.actor_id
            )
            up.permission = perm_map[p_name]
            target_user.direct_permissions.append(up)
            
        target_user.updated_by = audit_context.actor_id
        target_user.token_version += 1
        PermissionCacheService.invalidate_user_permissions(str(target_user.id))
        
        await self.audit_service.log_action(
            action=AuditAction.UPDATE,
            module=PermissionModule.USERS,
            table_name="users",
            record_id=target_user.id,
            new_values={"event": "PERMISSION_OVERRIDE_CHANGED", "token_version": target_user.token_version},
            user_id=audit_context.actor_id,
            ip_address=audit_context.ip_address,
            user_agent=audit_context.user_agent
        )
        
        return await self.user_repository.update(target_user)
