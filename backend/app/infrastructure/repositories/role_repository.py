from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.role import Role
from app.domain.repositories.role_repository import RoleRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyRoleRepository(SQLAlchemyBaseRepository[Role], RoleRepository):
    """
    SQLAlchemy implementation of the RoleRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Role)

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(
            Role.name == name,
            Role.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
