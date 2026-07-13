from abc import ABC, abstractmethod

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
