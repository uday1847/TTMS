from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.domain.entities.permission import Permission
from app.domain.repositories.permission_repository import PermissionRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyPermissionRepository(SQLAlchemyBaseRepository[Permission], PermissionRepository):
    """
    SQLAlchemy implementation of the PermissionRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Permission)

    async def list_all(self) -> list[Permission]:
        stmt = select(Permission).where(Permission.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_ids(self, permission_ids: list[uuid.UUID]) -> list[Permission]:
        stmt = select(Permission).where(
            Permission.id.in_(permission_ids),
            Permission.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Permission | None:
        stmt = select(Permission).where(
            Permission.name == name,
            Permission.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
