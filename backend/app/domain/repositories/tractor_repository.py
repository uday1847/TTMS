import uuid
from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.tractor import Tractor
from app.domain.repositories.base_repository import BaseRepository


class TractorRepository(BaseRepository[Tractor], ABC):
    """
    Tractor Repository contract defining domain-specific database queries.
    """

    @abstractmethod
    async def get_by_tractor_number(self, tractor_number: str) -> Tractor | None:
        """
        Retrieves a tractor by its unique registration plate number.
        """
        pass

    @abstractmethod
    async def get_by_rc_number(self, rc_number: str) -> Tractor | None:
        """
        Retrieves a tractor by its unique RC certificate number.
        """
        pass

    @abstractmethod
    async def has_active_trips(self, tractor_id: uuid.UUID) -> bool:
        """
        Checks if the tractor is linked to any active (is_active=True) trip.
        """
        pass

    @abstractmethod
    async def get_tractors(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        insurance_expiring_days: int | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Tractor], int]:
        """
        Retrieves a page of tractors matching search query, status filters,
        insurance expiry alerting, date ranges, sorting, and pagination.
        """
        pass
