from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.party_report_repository import PartyReportRepository
from app.domain.entities.party import Party
from app.domain.entities.trip import Trip
from app.domain.entities.invoice import Invoice


class SQLAlchemyPartyReportRepository(PartyReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_party_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        stmt = select(
            Party.name.label("party"),
            func.count(Trip.id).label("trip_count"),
            func.sum(Invoice.total_amount).label("revenue"),
            func.sum(Invoice.balance_amount).label("outstanding")
        ).select_from(Party).outerjoin(Trip, Trip.party_id == Party.id).outerjoin(Invoice, Invoice.trip_id == Trip.id).where(Party.deleted_at.is_(None))
        
        if start_date: stmt = stmt.where(Trip.trip_date >= start_date)
        if end_date: stmt = stmt.where(Trip.trip_date <= end_date)
        
        stmt = stmt.group_by(Party.id).order_by(func.sum(Invoice.total_amount).desc())
        
        result = await self.session.execute(stmt)
        return [
            {
                "party": row.party,
                "trip_count": row.trip_count or 0,
                "revenue": row.revenue or 0,
                "pending_invoice": row.outstanding or 0,
                "received_payment": (row.revenue or 0) - (row.outstanding or 0),
                "outstanding": row.outstanding or 0
            }
            for row in result.fetchall()
        ]
