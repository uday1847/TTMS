from decimal import Decimal
from typing import List, Optional
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.fuel_transaction import FuelTransaction


class FuelAnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_tractor_stats(self, tractor_id: str) -> dict:
        stmt = select(
            func.sum(FuelTransaction.amount).label("total_amount"),
            func.avg(FuelTransaction.average_kmpl).label("avg_kmpl")
        ).where(
            and_(
                FuelTransaction.tractor_id == tractor_id,
                FuelTransaction.deleted_at.is_(None),
                FuelTransaction.average_kmpl.is_not(None)
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        
        return {
            "total_fuel_amount": float(row.total_amount) if row and row.total_amount else 0.0,
            "average_kmpl": float(row.avg_kmpl) if row and row.avg_kmpl else None
        }

    async def calculate_trip_stats(self, trip_id: str) -> dict:
        stmt = select(
            func.sum(FuelTransaction.amount).label("total_amount"),
            func.count(FuelTransaction.id).label("transaction_count")
        ).where(
            and_(
                FuelTransaction.trip_id == trip_id,
                FuelTransaction.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        
        return {
            "total_fuel_amount": float(row.total_amount) if row and row.total_amount else 0.0,
            "fuel_transaction_count": int(row.transaction_count) if row and row.transaction_count else 0
        }
