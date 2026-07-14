from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.fuel_report_repository import FuelReportRepository
from app.domain.entities.tractor import Tractor
from app.domain.entities.fuel_transaction import FuelTransaction


class SQLAlchemyFuelReportRepository(FuelReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_fuel_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        stmt = select(
            Tractor.tractor_number.label("tractor"),
            func.sum(FuelTransaction.liters).label("total_liters"),
            func.avg(FuelTransaction.average_kmpl).label("average_kmpl"),
            func.sum(FuelTransaction.amount).label("fuel_cost"),
            func.sum(func.cast(FuelTransaction.is_suspicious, func.Integer)).label("suspicious_transactions")
        ).select_from(Tractor).outerjoin(FuelTransaction, FuelTransaction.tractor_id == Tractor.id).where(Tractor.deleted_at.is_(None))
        
        if start_date: stmt = stmt.where(FuelTransaction.fuel_date >= start_date)
        if end_date: stmt = stmt.where(FuelTransaction.fuel_date <= end_date)
        
        stmt = stmt.group_by(Tractor.id).order_by(func.sum(FuelTransaction.amount).desc())
        
        result = await self.session.execute(stmt)
        return [
            {
                "tractor": row.tractor,
                "total_liters": row.total_liters or 0,
                "average_kmpl": row.average_kmpl or 0,
                "cost_per_km": (row.fuel_cost / (row.total_liters * row.average_kmpl)) if row.total_liters and row.average_kmpl else 0,
                "fuel_cost": row.fuel_cost or 0,
                "suspicious_transactions": row.suspicious_transactions or 0
            }
            for row in result.fetchall()
        ]
