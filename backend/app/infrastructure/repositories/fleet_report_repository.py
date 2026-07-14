from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.fleet_report_repository import FleetReportRepository
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.trip import Trip
from app.domain.entities.fuel_transaction import FuelTransaction
from app.domain.entities.invoice import Invoice


class SQLAlchemyFleetReportRepository(FleetReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_fleet_utilization(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        # Fleet utilization placeholder
        return []

    async def get_driver_performance(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        # Driver stats: trips, average kmpl, revenue
        stmt = select(
            Driver.name.label("driver"),
            func.count(Trip.id).label("trip_count"),
            func.sum(Invoice.total_amount).label("revenue")
        ).select_from(Driver).outerjoin(Trip, Trip.driver_id == Driver.id).outerjoin(Invoice, Invoice.trip_id == Trip.id).where(Driver.deleted_at.is_(None))
        
        if start_date: stmt = stmt.where(Trip.trip_date >= start_date)
        if end_date: stmt = stmt.where(Trip.trip_date <= end_date)
        
        stmt = stmt.group_by(Driver.id).order_by(func.count(Trip.id).desc())
        
        result = await self.session.execute(stmt)
        return [{"driver": row.driver, "trip_count": row.trip_count, "revenue": row.revenue or 0, "average_kmpl": 0, "profit": 0, "on_time_delivery": 0, "fuel_efficiency": 0} for row in result.fetchall()]

    async def get_tractor_profitability(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        stmt = select(
            Tractor.tractor_number.label("tractor"),
            func.count(Trip.id).label("trip_count"),
            func.sum(Invoice.total_amount).label("income")
        ).select_from(Tractor).outerjoin(Trip, Trip.tractor_id == Tractor.id).outerjoin(Invoice, Invoice.trip_id == Trip.id).where(Tractor.deleted_at.is_(None))
        
        if start_date: stmt = stmt.where(Trip.trip_date >= start_date)
        if end_date: stmt = stmt.where(Trip.trip_date <= end_date)
        
        stmt = stmt.group_by(Tractor.id).order_by(func.sum(Invoice.total_amount).desc())
        
        result = await self.session.execute(stmt)
        return [{"tractor": row.tractor, "trip_count": row.trip_count, "income": row.income or 0, "fuel_cost": 0, "maintenance_cost": 0, "trip_expense": 0, "profit": 0} for row in result.fetchall()]
