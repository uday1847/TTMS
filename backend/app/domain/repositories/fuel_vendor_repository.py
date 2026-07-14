from abc import ABC, abstractmethod
import uuid
from typing import List, Optional

from app.domain.entities.fuel_vendor import FuelVendor
from app.application.dtos.fuel_vendor import FuelVendorCreate, FuelVendorUpdate


class FuelVendorRepository(ABC):
    @abstractmethod
    async def create(self, vendor: FuelVendor) -> FuelVendor:
        pass

    @abstractmethod
    async def get_by_id(self, vendor_id: uuid.UUID) -> Optional[FuelVendor]:
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[FuelVendor]:
        pass

    @abstractmethod
    async def count(self, is_active: Optional[bool] = None, search: Optional[str] = None) -> int:
        pass

    @abstractmethod
    async def update(self, vendor: FuelVendor) -> FuelVendor:
        pass

    @abstractmethod
    async def soft_delete(self, vendor_id: uuid.UUID, deleted_by: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def check_duplicate(self, vendor_code: str, gst_number: Optional[str] = None, exclude_id: Optional[uuid.UUID] = None) -> bool:
        pass
