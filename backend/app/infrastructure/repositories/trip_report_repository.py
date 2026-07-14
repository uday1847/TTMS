from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.trip_report_repository import TripReportRepository
from app.domain.entities.trip import Trip


class SQLAlchemyTripReportRepository(TripReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_trip_statistics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        # Count trips by status
        stmt = select(
            Trip.status,
            func.count(Trip.id).label("count")
        ).where(Trip.deleted_at.is_(None))
        
        if start_date: stmt = stmt.where(Trip.trip_date >= start_date)
        if end_date: stmt = stmt.where(Trip.trip_date <= end_date)
        
        stmt = stmt.group_by(Trip.status).order_by(func.count(Trip.id).desc())
        
        result = await self.session.execute(stmt)
        return [{"status": row.status.value, "count": row.count} for row in result.fetchall()]
