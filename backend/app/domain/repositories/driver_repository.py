import uuid
from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.driver import Driver
from app.domain.repositories.base_repository import BaseRepository


class DriverRepository(BaseRepository[Driver], ABC):
    """
    Driver Repository contract defining domain-specific database queries.
    """

    @abstractmethod
    async def get_by_employee_code(self, employee_code: str) -> Driver | None:
        """
        Retrieves a driver by their unique employee code.
        """
        pass

    @abstractmethod
    async def get_by_license_number(self, license_number: str) -> Driver | None:
        """
        Retrieves a driver by their unique driving license number.
        """
        pass

    @abstractmethod
    async def get_by_contact_phone(self, contact_phone: str) -> Driver | None:
        """
        Retrieves a driver by their unique contact phone/mobile number.
        """
        pass

    @abstractmethod
    async def has_active_trips(self, driver_id: uuid.UUID) -> bool:
        """
        Checks if the driver is linked to any active (is_active=True) trip.
        """
        pass

    @abstractmethod
    async def get_drivers(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Driver], int]:
        """
        Retrieves a page of drivers matching optional search, status, and deletion filter rules.
        """
        pass
