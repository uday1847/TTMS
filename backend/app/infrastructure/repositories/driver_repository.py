import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.driver import Driver
from app.domain.entities.trip import Trip
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

    async def get_by_contact_phone(self, contact_phone: str) -> Driver | None:
        stmt = select(Driver).where(
            Driver.contact_phone == contact_phone,
            Driver.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def has_active_trips(self, driver_id: uuid.UUID) -> bool:
        stmt = select(1).select_from(Trip).where(
            Trip.driver_id == driver_id,
            Trip.is_active == True,
            Trip.deleted_at.is_(None)
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def get_drivers(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Driver], int]:
        stmt = select(Driver)

        # 1. Soft-delete filter
        if not include_deleted:
            stmt = stmt.where(Driver.deleted_at.is_(None))

        # 2. Status filtering
        if status_filter == "ACTIVE":
            stmt = stmt.where(Driver.is_active == True)
        elif status_filter == "INACTIVE":
            stmt = stmt.where(Driver.is_active == False)

        # 3. Search query matching Name, Mobile (contact_phone), or License
        if search_query:
            q = f"%{search_query}%"
            stmt = stmt.where(
                (Driver.name.ilike(q)) |
                (Driver.contact_phone.ilike(q)) |
                (Driver.license_number.ilike(q))
            )

        # 4. Count total matching rows
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        # 5. Sorting
        sort_col = Driver.created_at
        if sort_by == "name":
            sort_col = Driver.name

        if order == "desc":
            stmt = stmt.order_by(sort_col.desc())
        else:
            stmt = stmt.order_by(sort_col.asc())

        # 6. Pagination offset/limit
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return items, total
