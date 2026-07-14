import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import select, or_, func, and_, desc
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.fuel_transaction import FuelTransaction
from app.domain.entities.fuel_history import FuelHistory
from app.domain.repositories.fuel_repository import FuelRepository


class SQLAlchemyFuelRepository(FuelRepository):
    def __init__(self, session: Session):
        self.session = session

    async def create(self, transaction: FuelTransaction) -> FuelTransaction:
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_by_id(self, transaction_id: uuid.UUID) -> Optional[FuelTransaction]:
        stmt = (
            select(FuelTransaction)
            .options(
                selectinload(FuelTransaction.tractor),
                selectinload(FuelTransaction.driver),
                selectinload(FuelTransaction.vendor),
                selectinload(FuelTransaction.trip),
                selectinload(FuelTransaction.histories)
            )
            .where(
                and_(
                    FuelTransaction.id == transaction_id, 
                    FuelTransaction.deleted_at.is_(None)
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        tractor_id: Optional[uuid.UUID] = None,
        trip_id: Optional[uuid.UUID] = None,
        vendor_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[FuelTransaction]:
        stmt = (
            select(FuelTransaction)
            .options(
                selectinload(FuelTransaction.tractor),
                selectinload(FuelTransaction.driver),
                selectinload(FuelTransaction.vendor)
            )
            .where(FuelTransaction.deleted_at.is_(None))
        )

        if tractor_id:
            stmt = stmt.where(FuelTransaction.tractor_id == tractor_id)
        if trip_id:
            stmt = stmt.where(FuelTransaction.trip_id == trip_id)
        if vendor_id:
            stmt = stmt.where(FuelTransaction.vendor_id == vendor_id)
        if status:
            stmt = stmt.where(FuelTransaction.status == status)
        if start_date:
            stmt = stmt.where(FuelTransaction.fuel_date >= start_date)
        if end_date:
            stmt = stmt.where(FuelTransaction.fuel_date <= end_date)

        stmt = stmt.order_by(FuelTransaction.fuel_date.desc(), FuelTransaction.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        tractor_id: Optional[uuid.UUID] = None,
        trip_id: Optional[uuid.UUID] = None,
        vendor_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        stmt = select(func.count(FuelTransaction.id)).where(FuelTransaction.deleted_at.is_(None))

        if tractor_id:
            stmt = stmt.where(FuelTransaction.tractor_id == tractor_id)
        if trip_id:
            stmt = stmt.where(FuelTransaction.trip_id == trip_id)
        if vendor_id:
            stmt = stmt.where(FuelTransaction.vendor_id == vendor_id)
        if status:
            stmt = stmt.where(FuelTransaction.status == status)
        if start_date:
            stmt = stmt.where(FuelTransaction.fuel_date >= start_date)
        if end_date:
            stmt = stmt.where(FuelTransaction.fuel_date <= end_date)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(self, transaction: FuelTransaction) -> FuelTransaction:
        await self.session.flush()
        return transaction

    async def check_duplicate(self, tractor_id: uuid.UUID, vendor_id: uuid.UUID, fuel_date: date, amount: float, liters: float) -> bool:
        stmt = select(func.count(FuelTransaction.id)).where(
            and_(
                FuelTransaction.tractor_id == tractor_id,
                FuelTransaction.vendor_id == vendor_id,
                FuelTransaction.fuel_date == fuel_date,
                FuelTransaction.amount == amount,
                FuelTransaction.liters == liters,
                FuelTransaction.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def get_previous_transaction(self, tractor_id: uuid.UUID, current_date: date) -> Optional[FuelTransaction]:
        stmt = (
            select(FuelTransaction)
            .where(
                and_(
                    FuelTransaction.tractor_id == tractor_id,
                    FuelTransaction.fuel_date <= current_date,
                    FuelTransaction.deleted_at.is_(None)
                )
            )
            .order_by(FuelTransaction.fuel_date.desc(), FuelTransaction.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_latest_odometer(self, tractor_id: uuid.UUID) -> int:
        # Note: typically would get this from Tractor directly, but sometimes from last fuel record
        from app.domain.entities.tractor import Tractor
        stmt = select(Tractor.current_odometer).where(Tractor.id == tractor_id)
        result = await self.session.execute(stmt)
        val = result.scalar_one_or_none()
        return val if val is not None else 0
    
    async def add_history(self, history: FuelHistory) -> None:
        self.session.add(history)
        await self.session.flush()
