from typing import Sequence
import uuid

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


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
                selectinload(User.roles).selectinload(Role.permissions)
            )
            .where(
                User.id == user_id,
                User.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_users(self, query: str, page: int, size: int) -> tuple[Sequence[User], int]:
        offset = (page - 1) * size
        like_query = f"%{query}%"
        
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
                selectinload(User.roles).selectinload(Role.permissions)
            )
            .where(
                User.deleted_at.is_(None),
                filter_clause
            )
            .offset(offset)
            .limit(size)
        )
        items_result = await self.session.execute(stmt_items)
        items = items_result.scalars().all()

        return items, total
