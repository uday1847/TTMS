from datetime import datetime, timezone
import logging
from typing import Sequence
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.domain.entities.user import User
from app.domain.exceptions.auth import RoleNotFoundException, UserAlreadyExistsException
from app.domain.repositories.role_repository import RoleRepository
from app.domain.repositories.user_repository import UserRepository
from app.schemas.user.user_create import UserCreate
from app.schemas.user.user_update import UserUpdate
from app.application.validators.password_validator import validate_password_complexity
from app.application.validators.user_validator import validate_username

logger = logging.getLogger("ttms.user_service")


class UserService:
    """
    Service layer orchestrating business workflows and database transaction boundaries
    for User profiles and role bindings.
    """

    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def register_user(self, dto: UserCreate, current_user_id: uuid.UUID | None = None) -> User:
        """
        Registers a new user profile after performing credentials and complexity checks.
        """
        logger.info(f"Registering user with email: {dto.email}")
        
        # Enforce validation checks
        validate_username(dto.username)
        validate_password_complexity(dto.password)

        async with self.session.begin():
            # Check unique email
            existing_email = await self.user_repository.get_by_email(dto.email)
            if existing_email:
                raise UserAlreadyExistsException(f"Email '{dto.email}' is already registered.")

            # Check unique username
            existing_username = await self.user_repository.get_by_username(dto.username)
            if existing_username:
                raise UserAlreadyExistsException(f"Username '{dto.username}' is already taken.")

            # Hash credentials
            hashed_pwd = hash_password(dto.password)

            creator_id = current_user_id or uuid.uuid4() # Fallback for initial self-registration

            
            # Create user entity
            user = User(
                email=dto.email,
                username=dto.username,
                password_hash=hashed_pwd,
                first_name=dto.first_name,
                last_name=dto.last_name,
                phone=dto.phone,
                created_by=creator_id,
                updated_by=creator_id,
                is_active=True,
            )

            await self.user_repository.create(user)

        logger.info(f"User registration completed: {user.email} (ID: {user.id})")
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """
        Loads a user eager-loading active roles and permissions mappings.
        """
        return await self.user_repository.get_with_roles_and_permissions(user_id)

    async def get_all_users(self) -> Sequence[User]:
        """
        Returns all active users.
        """
        return await self.user_repository.get_all()

    async def update_user(self, user_id: uuid.UUID, dto: UserUpdate, current_user_id: uuid.UUID) -> User:
        """
        Updates basic profile attributes.
        """
        logger.info(f"Updating user profile: {user_id}")

        async with self.session.begin():
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise UserAlreadyExistsException("Target user was not found.")

            # Validate username update
            if dto.username is not None and dto.username != user.username:
                validate_username(dto.username)
                existing = await self.user_repository.get_by_username(dto.username)
                if existing:
                    raise UserAlreadyExistsException(f"Username '{dto.username}' is already taken.")
                user.username = dto.username

            # Validate email update
            if dto.email is not None and dto.email != user.email:
                existing = await self.user_repository.get_by_email(dto.email)
                if existing:
                    raise UserAlreadyExistsException(f"Email '{dto.email}' is already registered.")
                user.email = dto.email

            # Update remaining properties
            if dto.first_name is not None:
                user.first_name = dto.first_name
            if dto.last_name is not None:
                user.last_name = dto.last_name
            if dto.phone is not None:
                user.phone = dto.phone
            if dto.is_active is not None:
                user.is_active = dto.is_active

            # Stamp audit
            user.updated_by = current_user_id
            user.updated_at = datetime.now(timezone.utc)

            await self.user_repository.update(user)

        logger.info(f"User {user.email} successfully updated.")
        return user

    async def delete_user(self, user_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """
        Soft-deletes a user account.
        """
        logger.info(f"Soft deleting user account: {user_id}")
        async with self.session.begin():
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return False

            user.updated_by = current_user_id
            user.updated_at = datetime.now(timezone.utc)
            
            await self.user_repository.delete(user_id, soft=True)

        logger.info(f"User account {user_id} soft deleted.")
        return True

    async def assign_role(self, user_id: uuid.UUID, role_name: str, current_user_id: uuid.UUID) -> User:
        """
        Adds a role map binding to a user's role array.
        """
        logger.info(f"Assigning role '{role_name}' to user: {user_id}")

        async with self.session.begin():
            # Load user with roles
            user = await self.user_repository.get_with_roles_and_permissions(user_id)
            if not user:
                raise UserAlreadyExistsException("Target user was not found.")

            # Load role
            role = await self.role_repository.get_by_name(role_name)
            if not role:
                raise RoleNotFoundException(role_name)

            # Avoid duplicates
            if role not in user.roles:
                user.roles.append(role)
                user.updated_by = current_user_id
                user.updated_at = datetime.now(timezone.utc)
                await self.user_repository.update(user)

        logger.info(f"Role '{role_name}' successfully bound to user {user.email}.")
        return user

    async def remove_role(self, user_id: uuid.UUID, role_name: str, current_user_id: uuid.UUID) -> User:
        """
        Removes a role map binding from a user's role array.
        """
        logger.info(f"Removing role '{role_name}' from user: {user_id}")

        async with self.session.begin():
            user = await self.user_repository.get_with_roles_and_permissions(user_id)
            if not user:
                raise UserAlreadyExistsException("Target user was not found.")

            role = await self.role_repository.get_by_name(role_name)
            if not role:
                raise RoleNotFoundException(role_name)

            if role in user.roles:
                user.roles.remove(role)
                user.updated_by = current_user_id
                user.updated_at = datetime.now(timezone.utc)
                await self.user_repository.update(user)

        logger.info(f"Role '{role_name}' removed from user {user.email}.")
        return user

    async def verify_user_role(self, user_id: uuid.UUID, role_name: str) -> bool:
        """
        Checks if a user holds a specific role.
        """
        user = await self.user_repository.get_with_roles_and_permissions(user_id)
        if not user or not user.is_active:
            return False
        return any(role.name == role_name for role in user.roles)

    async def verify_user_permission(self, user_id: uuid.UUID, permission_code: str) -> bool:
        """
        Checks if a user holds a specific permission (inherited from any of their assigned roles).
        """
        user = await self.user_repository.get_with_roles_and_permissions(user_id)
        if not user or not user.is_active:
            return False
        
        # Aggregate all active permissions across all user roles
        for role in user.roles:
            if not role.is_active:
                continue
            for permission in role.permissions:
                if permission.is_active and permission.code == permission_code:
                    return True
        return False

    async def paginate_users(self, page: int, size: int) -> tuple[Sequence[User], int]:
        """
        Gets a paginated list of users.
        """
        # We need eager loaded roles here as well for proper listing
        # Since paginate inside SQLAlchemyBaseRepository does not selectinload roles,
        # we can perform pagination locally in UserService or keep it standard.
        # Let's perform selectinload paginate local call for user response completeness.
        offset = (page - 1) * size
        total = await self.user_repository.count()

        from sqlalchemy import select
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.deleted_at.is_(None))
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return items, total

    async def search_users(self, query: str, page: int, size: int) -> tuple[Sequence[User], int]:
        """
        Queries and filters users by matching strings.
        """
        return await self.user_repository.search_users(query, page, size)
