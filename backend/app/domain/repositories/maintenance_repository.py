import uuid
from abc import ABC, abstractmethod
from typing import Any, Tuple

from app.domain.entities.maintenance import Maintenance
from app.domain.entities.maintenance_history import MaintenanceHistory


class MaintenanceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, maintenance_id: uuid.UUID) -> Maintenance | None:
        pass

    @abstractmethod
    async def get_by_number(self, maintenance_number: str) -> Maintenance | None:
        pass

    @abstractmethod
    async def get_active_for_tractor(self, tractor_id: uuid.UUID) -> Maintenance | None:
        """Returns SCHEDULED or IN_PROGRESS maintenance for a tractor."""
        pass

    @abstractmethod
    async def search(self, filters: dict[str, Any], page: int, size: int) -> Tuple[list[Maintenance], int]:
        pass

    @abstractmethod
    async def get_dashboard_stats(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_upcoming_services(self, limit: int = 10) -> list[Maintenance]:
        pass

    @abstractmethod
    async def get_overdue_services(self, limit: int = 10) -> list[Maintenance]:
        pass

    @abstractmethod
    async def get_history(self, maintenance_id: uuid.UUID) -> list[MaintenanceHistory]:
        pass

    @abstractmethod
    async def save(self, maintenance: Maintenance) -> Maintenance:
        pass
