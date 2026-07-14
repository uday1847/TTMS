from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
        ).options(selectinload(Role.permissions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, role_id) -> Role | None:
        stmt = select(Role).where(
            Role.id == role_id,
            Role.deleted_at.is_(None)
        ).options(selectinload(Role.permissions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_roles(self, skip: int = 0, limit: int = 100) -> tuple[list[Role], int]:
        stmt_count = select(func.count(Role.id)).where(Role.deleted_at.is_(None))
        total = (await self.session.execute(stmt_count)).scalar_one()

        stmt_items = select(Role).where(Role.deleted_at.is_(None)).options(selectinload(Role.permissions)).offset(skip).limit(limit)
        items = list((await self.session.execute(stmt_items)).scalars().all())

        return items, total
