from datetime import date, datetime
import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.party import Party
from app.domain.entities.trip import Trip
from app.domain.repositories.party_repository import PartyRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyPartyRepository(SQLAlchemyBaseRepository[Party], PartyRepository):
    """
    SQLAlchemy implementation of the PartyRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Party)

    async def get_by_mobile(self, mobile_number: str) -> Party | None:
        stmt = select(Party).where(
            Party.mobile_number == mobile_number,
            Party.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_gst(self, gst_number: str) -> Party | None:
        stmt = select(Party).where(
            Party.gst_number == gst_number,
            Party.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_pan(self, pan_number: str) -> Party | None:
        stmt = select(Party).where(
            Party.pan_number == pan_number,
            Party.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def has_active_trips(self, party_id: uuid.UUID) -> bool:
        stmt = select(1).select_from(Trip).where(
            Trip.party_id == party_id,
            Trip.is_active == True,
            Trip.deleted_at.is_(None)
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def get_parties(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        party_type_filter: str | None = None,
        status_filter: str | None = None,
        city_filter: str | None = None,
        state_filter: str | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Party], int]:
        stmt = select(Party)

        # 1. Soft-delete filter
        if not include_deleted:
            stmt = stmt.where(Party.deleted_at.is_(None))

        # 2. Status filtering
        if status_filter == "ACTIVE":
            stmt = stmt.where(Party.is_active == True)
        elif status_filter == "INACTIVE":
            stmt = stmt.where(Party.is_active == False)

        # 3. Party type filtering
        if party_type_filter:
            stmt = stmt.where(Party.party_type == party_type_filter.upper())

        # 4. City and State filtering
        if city_filter:
            stmt = stmt.where(Party.city.ilike(city_filter))
        if state_filter:
            stmt = stmt.where(Party.state.ilike(state_filter))

        # 5. Created Date Range filtering
        if created_date_start:
            try:
                start_dt = datetime.combine(date.fromisoformat(created_date_start), datetime.min.time())
                stmt = stmt.where(Party.created_at >= start_dt)
            except ValueError:
                pass
        if created_date_end:
            try:
                end_dt = datetime.combine(date.fromisoformat(created_date_end), datetime.max.time())
                stmt = stmt.where(Party.created_at <= end_dt)
            except ValueError:
                pass

        # 6. Search query matching Name, Mobile, GST, City, or Contact Person
        if search_query:
            q = f"%{search_query}%"
            stmt = stmt.where(
                (Party.name.ilike(q)) |
                (Party.mobile_number.ilike(q)) |
                (Party.gst_number.ilike(q)) |
                (Party.city.ilike(q)) |
                (Party.contact_person.ilike(q))
            )

        # 7. Count total matching rows
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        # 8. Sorting
        sort_col = Party.created_at
        if sort_by == "name":
            sort_col = Party.name
        elif sort_by == "opening_balance":
            sort_col = Party.opening_balance

        if order == "desc":
            stmt = stmt.order_by(sort_col.desc())
        else:
            stmt = stmt.order_by(sort_col.asc())

        # 9. Pagination offset/limit
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return items, total
