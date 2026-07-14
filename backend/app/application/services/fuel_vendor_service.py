import uuid
from typing import List, Optional

from app.domain.entities.fuel_vendor import FuelVendor
from app.domain.exceptions.fuel import FuelVendorNotFoundException, FuelDuplicateException
from app.domain.repositories.fuel_vendor_repository import FuelVendorRepository
from app.application.dtos.fuel_vendor import FuelVendorCreate, FuelVendorUpdate


class FuelVendorService:
    def __init__(self, repository: FuelVendorRepository):
        self.repository = repository

    async def create_vendor(self, data: FuelVendorCreate, created_by: uuid.UUID) -> FuelVendor:
        # Check duplicate by vendor_code or gst_number
        is_duplicate = await self.repository.check_duplicate(data.vendor_code, data.gst_number)
        if is_duplicate:
            raise FuelDuplicateException("A fuel vendor with this code or GST number already exists.")

        vendor = FuelVendor(
            vendor_code=data.vendor_code,
            name=data.name,
            contact_person=data.contact_person,
            mobile=data.mobile,
            email=data.email,
            gst_number=data.gst_number,
            address=data.address,
            city=data.city,
            state=data.state,
            latitude=data.latitude,
            longitude=data.longitude,
            opening_time=data.opening_time,
            closing_time=data.closing_time,
            is_company_owned=data.is_company_owned,
            notes=data.notes,
            is_active=data.is_active,
            created_by=created_by,
            updated_by=created_by,
        )

        return await self.repository.create(vendor)

    async def get_vendor(self, vendor_id: uuid.UUID) -> FuelVendor:
        vendor = await self.repository.get_by_id(vendor_id)
        if not vendor:
            raise FuelVendorNotFoundException()
        return vendor

    async def get_vendors(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[FuelVendor]:
        return await self.repository.get_all(skip=skip, limit=limit, is_active=is_active, search=search)

    async def count_vendors(self, is_active: Optional[bool] = None, search: Optional[str] = None) -> int:
        return await self.repository.count(is_active=is_active, search=search)

    async def update_vendor(self, vendor_id: uuid.UUID, data: FuelVendorUpdate, updated_by: uuid.UUID) -> FuelVendor:
        vendor = await self.get_vendor(vendor_id)

        if data.vendor_code or data.gst_number:
            v_code = data.vendor_code if data.vendor_code is not None else vendor.vendor_code
            v_gst = data.gst_number if data.gst_number is not None else vendor.gst_number
            is_duplicate = await self.repository.check_duplicate(v_code, v_gst, exclude_id=vendor_id)
            if is_duplicate:
                raise FuelDuplicateException("Another fuel vendor with this code or GST number already exists.")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)

        vendor.updated_by = updated_by
        return await self.repository.update(vendor)

    async def delete_vendor(self, vendor_id: uuid.UUID, deleted_by: uuid.UUID) -> None:
        vendor = await self.get_vendor(vendor_id)
        # Perform soft delete
        await self.repository.soft_delete(vendor_id, deleted_by)
