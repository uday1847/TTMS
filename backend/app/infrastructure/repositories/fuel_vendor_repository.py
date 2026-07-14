import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, or_, func, and_
from sqlalchemy.orm import Session

from app.domain.entities.fuel_vendor import FuelVendor
from app.domain.repositories.fuel_vendor_repository import FuelVendorRepository


class SQLAlchemyFuelVendorRepository(FuelVendorRepository):
    def __init__(self, session: Session):
        self.session = session

    async def create(self, vendor: FuelVendor) -> FuelVendor:
        self.session.add(vendor)
        await self.session.flush()
        return vendor

    async def get_by_id(self, vendor_id: uuid.UUID) -> Optional[FuelVendor]:
        stmt = select(FuelVendor).where(
            and_(FuelVendor.id == vendor_id, FuelVendor.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[FuelVendor]:
        stmt = select(FuelVendor).where(FuelVendor.deleted_at.is_(None))

        if is_active is not None:
            stmt = stmt.where(FuelVendor.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(
                or_(
                    FuelVendor.name.ilike(search_filter),
                    FuelVendor.vendor_code.ilike(search_filter),
                    FuelVendor.contact_person.ilike(search_filter),
                    FuelVendor.mobile.ilike(search_filter)
                )
            )

        stmt = stmt.order_by(FuelVendor.name.asc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, is_active: Optional[bool] = None, search: Optional[str] = None) -> int:
        stmt = select(func.count(FuelVendor.id)).where(FuelVendor.deleted_at.is_(None))

        if is_active is not None:
            stmt = stmt.where(FuelVendor.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(
                or_(
                    FuelVendor.name.ilike(search_filter),
                    FuelVendor.vendor_code.ilike(search_filter),
                    FuelVendor.contact_person.ilike(search_filter),
                    FuelVendor.mobile.ilike(search_filter)
                )
            )

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(self, vendor: FuelVendor) -> FuelVendor:
        await self.session.flush()
        return vendor

    async def soft_delete(self, vendor_id: uuid.UUID, deleted_by: uuid.UUID) -> None:
        vendor = await self.get_by_id(vendor_id)
        if vendor:
            vendor.deleted_at = datetime.utcnow()
            vendor.updated_by = deleted_by
            vendor.is_active = False
            await self.session.flush()

    async def check_duplicate(self, vendor_code: str, gst_number: Optional[str] = None, exclude_id: Optional[uuid.UUID] = None) -> bool:
        conditions = [FuelVendor.deleted_at.is_(None)]
        
        duplicate_conditions = [FuelVendor.vendor_code == vendor_code]
        if gst_number:
            duplicate_conditions.append(FuelVendor.gst_number == gst_number)
            
        conditions.append(or_(*duplicate_conditions))
        
        if exclude_id:
            conditions.append(FuelVendor.id != exclude_id)
            
        stmt = select(func.count(FuelVendor.id)).where(and_(*conditions))
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count > 0
