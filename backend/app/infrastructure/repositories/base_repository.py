from datetime import datetime, timezone
from typing import Generic, Sequence, Type, TypeVar
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.base import BaseEntity
from app.domain.repositories.base_repository import BaseRepository

T = TypeVar("T", bound=BaseEntity)


class SQLAlchemyBaseRepository(BaseRepository[T], Generic[T]):
    """
    SQLAlchemy 2.0 Async implementation of the BaseRepository interface.
    """

    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        self.session = session
        self.model = model

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, id: uuid.UUID) -> T | None:
        stmt = select(self.model).where(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[T]:
        stmt = select(self.model).where(self.model.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, entity: T) -> T:
        # SQLAlchemy tracks state changes on flushed objects.
        # Session merge or update is handled on session flush/commit.
        await self.session.flush()
        return entity

    async def delete(self, id: uuid.UUID, soft: bool = True) -> bool:
        entity = await self.get_by_id(id)
        if not entity:
            return False

        if soft:
            entity.deleted_at = datetime.now(timezone.utc)
            entity.is_active = False
        else:
            await self.session.delete(entity)

        await self.session.flush()
        return True

    async def exists(self, id: uuid.UUID) -> bool:
        stmt = select(1).where(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def count(self) -> int:
        stmt = select(func.count(self.model.id)).where(self.model.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def paginate(self, page: int, size: int) -> tuple[Sequence[T], int]:
        offset = (page - 1) * size
        total = await self.count()

        stmt = (
            select(self.model)
            .where(self.model.deleted_at.is_(None))
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return items, total
