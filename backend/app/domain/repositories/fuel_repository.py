from abc import ABC, abstractmethod
import uuid
from typing import List, Optional
from datetime import date

from app.domain.entities.fuel_transaction import FuelTransaction
from app.domain.entities.fuel_history import FuelHistory


class FuelRepository(ABC):
    @abstractmethod
    async def create(self, transaction: FuelTransaction) -> FuelTransaction:
        pass

    @abstractmethod
    async def get_by_id(self, transaction_id: uuid.UUID) -> Optional[FuelTransaction]:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count(
        self,
        tractor_id: Optional[uuid.UUID] = None,
        trip_id: Optional[uuid.UUID] = None,
        vendor_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        pass

    @abstractmethod
    async def update(self, transaction: FuelTransaction) -> FuelTransaction:
        pass

    @abstractmethod
    async def check_duplicate(self, tractor_id: uuid.UUID, vendor_id: uuid.UUID, fuel_date: date, amount: float, liters: float) -> bool:
        pass

    @abstractmethod
    async def get_previous_transaction(self, tractor_id: uuid.UUID, current_date: date) -> Optional[FuelTransaction]:
        pass

    @abstractmethod
    async def get_latest_odometer(self, tractor_id: uuid.UUID) -> int:
        pass
    
    @abstractmethod
    async def add_history(self, history: FuelHistory) -> None:
        pass
