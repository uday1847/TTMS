from datetime import date, datetime, timedelta
import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.tractor import Tractor
from app.domain.entities.trip import Trip
from app.domain.repositories.tractor_repository import TractorRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyTractorRepository(SQLAlchemyBaseRepository[Tractor], TractorRepository):
    """
    SQLAlchemy implementation of the TractorRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Tractor)

    async def get_by_tractor_number(self, tractor_number: str) -> Tractor | None:
        stmt = select(Tractor).where(
            Tractor.tractor_number == tractor_number,
            Tractor.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_rc_number(self, rc_number: str) -> Tractor | None:
        stmt = select(Tractor).where(
            Tractor.rc_number == rc_number,
            Tractor.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def has_active_trips(self, tractor_id: uuid.UUID) -> bool:
        stmt = select(1).select_from(Trip).where(
            Trip.tractor_id == tractor_id,
            Trip.is_active == True,
            Trip.deleted_at.is_(None)
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def get_tractors(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        insurance_expiring_days: int | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Tractor], int]:
        stmt = select(Tractor)

        # 1. Soft-delete filter
        if not include_deleted:
            stmt = stmt.where(Tractor.deleted_at.is_(None))

        # 2. Status filtering
        if status_filter == "ACTIVE":
            stmt = stmt.where(Tractor.is_active == True)
        elif status_filter == "INACTIVE":
            stmt = stmt.where(Tractor.is_active == False)

        # 3. Insurance expiring filter
        if insurance_expiring_days is not None:
            max_expiry_date = date.today() + timedelta(days=insurance_expiring_days)
            stmt = stmt.where(Tractor.insurance_expiry <= max_expiry_date)

        # 4. Created Date Range filtering
        if created_date_start:
            try:
                start_dt = datetime.combine(date.fromisoformat(created_date_start), datetime.min.time())
                stmt = stmt.where(Tractor.created_at >= start_dt)
            except ValueError:
                pass
        if created_date_end:
            try:
                end_dt = datetime.combine(date.fromisoformat(created_date_end), datetime.max.time())
                stmt = stmt.where(Tractor.created_at <= end_dt)
            except ValueError:
                pass

        # 5. Search query matching Tractor Number, Owner Name, or RC Number
        if search_query:
            q = f"%{search_query}%"
            stmt = stmt.where(
                (Tractor.tractor_number.ilike(q)) |
                (Tractor.owner_name.ilike(q)) |
                (Tractor.rc_number.ilike(q))
            )

        # 6. Count total matching rows
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        # 7. Sorting
        sort_col = Tractor.created_at
        if sort_by == "tractor_number":
            sort_col = Tractor.tractor_number
        elif sort_by == "owner_name":
            sort_col = Tractor.owner_name
        elif sort_by == "insurance_expiry":
            sort_col = Tractor.insurance_expiry

        if order == "desc":
            stmt = stmt.order_by(sort_col.desc())
        else:
            stmt = stmt.order_by(sort_col.asc())

        # 8. Pagination offset/limit
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return items, total
