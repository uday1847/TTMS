from datetime import date, datetime, timedelta
import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.enums.trip_status import TripStatus
from app.domain.repositories.trip_repository import TripRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyTripRepository(SQLAlchemyBaseRepository[Trip], TripRepository):
    """
    SQLAlchemy implementation of the TripRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Trip)

    async def get_by_id(self, id: uuid.UUID) -> Trip | None:
        stmt = select(Trip).options(
            selectinload(Trip.driver),
            selectinload(Trip.tractor),
            selectinload(Trip.party)
        ).where(
            Trip.id == id,
            Trip.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_trip_number(self, trip_number: str) -> Trip | None:
        stmt = select(Trip).options(
            selectinload(Trip.driver),
            selectinload(Trip.tractor),
            selectinload(Trip.party)
        ).where(
            Trip.trip_number == trip_number,
            Trip.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_trip_by_driver(self, driver_id: uuid.UUID) -> Trip | None:
        stmt = select(Trip).where(
            Trip.driver_id == driver_id,
            Trip.status.in_([TripStatus.PENDING, TripStatus.DISPATCHED, TripStatus.IN_PROGRESS]),
            Trip.deleted_at.is_(None)
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_trip_by_tractor(self, tractor_id: uuid.UUID) -> Trip | None:
        stmt = select(Trip).where(
            Trip.tractor_id == tractor_id,
            Trip.status.in_([TripStatus.PENDING, TripStatus.DISPATCHED, TripStatus.IN_PROGRESS]),
            Trip.deleted_at.is_(None)
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_max_sequence_for_year(self, year: int) -> int:
        prefix = f"TRIP-{year}-%"
        stmt = select(func.count()).select_from(Trip).where(
            Trip.trip_number.like(prefix)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_trips(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        driver_id: uuid.UUID | None = None,
        party_id: uuid.UUID | None = None,
        tractor_id: uuid.UUID | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Trip], int]:
        stmt = select(Trip).options(
            selectinload(Trip.driver),
            selectinload(Trip.tractor),
            selectinload(Trip.party)
        )

        # 1. Soft-delete filter
        if not include_deleted:
            stmt = stmt.where(Trip.deleted_at.is_(None))

        # 2. Status filtering
        if status_filter:
            stmt = stmt.where(Trip.status == status_filter.upper())

        # 3. Linked assets filters
        if driver_id:
            stmt = stmt.where(Trip.driver_id == driver_id)
        if party_id:
            stmt = stmt.where(Trip.party_id == party_id)
        if tractor_id:
            stmt = stmt.where(Trip.tractor_id == tractor_id)

        # 4. Trip Date Ranges filtering
        if date_start:
            try:
                stmt = stmt.where(Trip.trip_date >= date.fromisoformat(date_start))
            except ValueError:
                pass
        if date_end:
            try:
                stmt = stmt.where(Trip.trip_date <= date.fromisoformat(date_end))
            except ValueError:
                pass

        # 5. Created Date Range filtering
        if created_date_start:
            try:
                start_dt = datetime.combine(date.fromisoformat(created_date_start), datetime.min.time())
                stmt = stmt.where(Trip.created_at >= start_dt)
            except ValueError:
                pass
        if created_date_end:
            try:
                end_dt = datetime.combine(date.fromisoformat(created_date_end), datetime.max.time())
                stmt = stmt.where(Trip.created_at <= end_dt)
            except ValueError:
                pass

        # 6. Search query matching trip_number, source_location, destination_location, remarks,
        # or joined properties: party.name, driver.name, tractor.tractor_number
        if search_query:
            q = f"%{search_query}%"
            # Join for search
            stmt = stmt.outerjoin(Trip.driver).outerjoin(Trip.tractor).outerjoin(Trip.party)
            stmt = stmt.where(
                (Trip.trip_number.ilike(q)) |
                (Trip.source_location.ilike(q)) |
                (Trip.destination_location.ilike(q)) |
                (Trip.remarks.ilike(q)) |
                (Driver.name.ilike(q)) |
                (Tractor.tractor_number.ilike(q)) |
                (Party.name.ilike(q))
            )

        # 7. Count total matching rows
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        # 8. Sorting
        sort_col = Trip.created_at
        if sort_by == "trip_date":
            sort_col = Trip.trip_date
        elif sort_by == "trip_number":
            sort_col = Trip.trip_number
        elif sort_by == "freight_amount":
            sort_col = Trip.freight_amount

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

    async def count_active_trips(self) -> int:
        stmt = select(func.count()).select_from(Trip).where(
            Trip.status.in_([TripStatus.DISPATCHED, TripStatus.IN_PROGRESS]),
            Trip.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_completed_today(self) -> int:
        today_date = date.today()
        stmt = select(func.count()).select_from(Trip).where(
            Trip.status == TripStatus.COMPLETED,
            Trip.actual_delivery_date == today_date,
            Trip.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_pending(self) -> int:
        stmt = select(func.count()).select_from(Trip).where(
            Trip.status == TripStatus.PENDING,
            Trip.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_in_progress(self) -> int:
        stmt = select(func.count()).select_from(Trip).where(
            Trip.status == TripStatus.IN_PROGRESS,
            Trip.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_trips_count_by_date_range(self, start_date: date, end_date: date) -> int:
        stmt = select(func.count()).select_from(Trip).where(
            Trip.trip_date >= start_date,
            Trip.trip_date <= end_date,
            Trip.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_revenue_by_date_range(self, start_date: date, end_date: date) -> float:
        stmt = select(func.sum(Trip.freight_amount)).where(
            Trip.trip_date >= start_date,
            Trip.trip_date <= end_date,
            Trip.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        res_val = result.scalar()
        return float(res_val) if res_val is not None else 0.0

    # Placeholders for future sub-modules
    async def has_expenses(self, trip_id: uuid.UUID) -> bool:
        return False

    async def has_invoice(self, trip_id: uuid.UUID) -> bool:
        return False

    async def has_settlement(self, trip_id: uuid.UUID) -> bool:
        return False
