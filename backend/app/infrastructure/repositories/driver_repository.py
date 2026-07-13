from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.driver import Driver
from app.domain.repositories.driver_repository import DriverRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyDriverRepository(SQLAlchemyBaseRepository[Driver], DriverRepository):
    """
    SQLAlchemy implementation of the DriverRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Driver)

    async def get_by_employee_code(self, employee_code: str) -> Driver | None:
        stmt = select(Driver).where(
            Driver.employee_code == employee_code,
            Driver.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_license_number(self, license_number: str) -> Driver | None:
        stmt = select(Driver).where(
            Driver.license_number == license_number,
            Driver.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
