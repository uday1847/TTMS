from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.maintenance_report_repository import MaintenanceReportRepository
from app.domain.entities.tractor import Tractor
from app.domain.entities.maintenance import Maintenance


class SQLAlchemyMaintenanceReportRepository(MaintenanceReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_maintenance_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        stmt = select(
            Tractor.tractor_number.label("tractor"),
            func.count(Maintenance.id).label("maintenance_count"),
            func.sum(Maintenance.total_cost).label("maintenance_cost"),
            func.max(Maintenance.next_service_date).label("next_service")
        ).select_from(Tractor).outerjoin(Maintenance, Maintenance.tractor_id == Tractor.id).where(Tractor.deleted_at.is_(None))
        
        if start_date: stmt = stmt.where(Maintenance.start_date >= start_date)
        if end_date: stmt = stmt.where(Maintenance.start_date <= end_date)
        
        stmt = stmt.group_by(Tractor.id).order_by(func.sum(Maintenance.total_cost).desc())
        
        result = await self.session.execute(stmt)
        
        today = date.today()
        
        return [
            {
                "tractor": row.tractor,
                "maintenance_count": row.maintenance_count or 0,
                "maintenance_cost": row.maintenance_cost or 0,
                "downtime_days": 0, # Placeholder
                "next_service": row.next_service,
                "overdue": (row.next_service < today) if row.next_service else False
            }
            for row in result.fetchall()
        ]
