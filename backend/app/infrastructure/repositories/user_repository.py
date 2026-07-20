from typing import Sequence
import uuid

from sqlalchemy import func, select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.domain.entities.user_permission import UserPermission
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository
from app.domain.enums.user_status import UserStatus

class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[User], UserRepository):
    """
    SQLAlchemy implementation of the UserRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(
            User.email == email,
            User.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(
            User.username == username,
            User.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_roles_and_permissions(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.direct_permissions).selectinload(UserPermission.permission)
            )
            .where(
                User.id == user_id,
                User.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(self, skip: int = 0, limit: int = 100, search: str | None = None) -> tuple[list[User], int]:
        filter_clause = True
        if search:
            like_query = f"%{search}%"
            filter_clause = or_(
                User.email.ilike(like_query),
                User.username.ilike(like_query),
                User.first_name.ilike(like_query),
                User.last_name.ilike(like_query)
            )

        stmt_count = (
            select(func.count(User.id))
            .where(
                User.deleted_at.is_(None),
                filter_clause
            )
        )
        total_result = await self.session.execute(stmt_count)
        total = total_result.scalar_one()

        stmt_items = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.direct_permissions).selectinload(UserPermission.permission)
            )
            .where(
                User.deleted_at.is_(None),
                filter_clause
            )
            .offset(skip)
            .limit(limit)
        )
        items_result = await self.session.execute(stmt_items)
        items = list(items_result.scalars().all())

        return items, total

    async def search_users(self, query: str, page: int, size: int) -> tuple[Sequence[User], int]:
        return await self.list_users(skip=(page-1)*size, limit=size, search=query)

    async def bulk_update_status(self, user_ids: list[uuid.UUID], status: UserStatus, updated_by: uuid.UUID | None = None) -> None:
        stmt = (
            update(User)
            .where(User.id.in_(user_ids))
            .values(status=status, updated_by=updated_by)
        )
        await self.session.execute(stmt)

    async def get_total_count(self) -> int:
        stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
        return (await self.session.execute(stmt)).scalar_one()

    async def get_active_count(self) -> int:
        stmt = select(func.count(User.id)).where(User.deleted_at.is_(None), User.status == UserStatus.ACTIVE)
        return (await self.session.execute(stmt)).scalar_one()

    async def get_locked_count(self) -> int:
        stmt = select(func.count(User.id)).where(User.deleted_at.is_(None), User.status == UserStatus.LOCKED)
        return (await self.session.execute(stmt)).scalar_one()
