from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.permission import Permission
from app.domain.repositories.permission_repository import PermissionRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyPermissionRepository(SQLAlchemyBaseRepository[Permission], PermissionRepository):
    """
    SQLAlchemy implementation of the PermissionRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Permission)

    async def get_by_code(self, code: str) -> Permission | None:
        stmt = select(Permission).where(
            Permission.code == code,
            Permission.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
