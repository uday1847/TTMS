import datetime
import uuid
from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.trip import Trip
from app.domain.repositories.base_repository import BaseRepository


class TripRepository(BaseRepository[Trip], ABC):
    """
    Trip Repository contract defining domain-specific database queries.
    """

    @abstractmethod
    async def get_by_trip_number(self, trip_number: str) -> Trip | None:
        """
        Retrieves a trip by its unique trip number.
        """
        pass

    @abstractmethod
    async def get_active_trip_by_driver(self, driver_id: uuid.UUID) -> Trip | None:
        """
        Retrieves the active trip (PENDING, DISPATCHED, IN_PROGRESS) assigned to a driver.
        """
        pass

    @abstractmethod
    async def get_active_trip_by_tractor(self, tractor_id: uuid.UUID) -> Trip | None:
        """
        Retrieves the active trip (PENDING, DISPATCHED, IN_PROGRESS) assigned to a tractor.
        """
        pass

    @abstractmethod
    async def get_max_sequence_for_year(self, year: int) -> int:
        """
        Calculates the maximum sequential index counter for trips registered in the given year.
        """
        pass

    @abstractmethod
    async def get_trips(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        driver_id: uuid.UUID | None = None,
        party_id: uuid.UUID | None = None,
        tractor_id: uuid.UUID | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Trip], int]:
        """
        Retrieves a page of trips matching filters.
        """
        pass

    # Dashboard analytic queries
    @abstractmethod
    async def count_active_trips(self) -> int:
        """
        Counts active trips (DISPATCHED, IN_PROGRESS).
        """
        pass

    @abstractmethod
    async def count_completed_today(self) -> int:
        """
        Counts trips completed today.
        """
        pass

    @abstractmethod
    async def count_pending(self) -> int:
        """
        Counts pending trips.
        """
        pass

    @abstractmethod
    async def count_in_progress(self) -> int:
        """
        Counts in progress trips.
        """
        pass

    @abstractmethod
    async def get_trips_count_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Dashboard helper counting total trips within date bounds.
        """
        pass

    @abstractmethod
    async def get_revenue_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> float:
        """
        Dashboard helper summing freight revenue amount within date bounds.
        """
        pass

    # Placeholders
    @abstractmethod
    async def has_expenses(self, trip_id: uuid.UUID) -> bool:
        """
        Placeholder check for downstream billing expenses. Returns False.
        """
        pass

    @abstractmethod
    async def has_invoice(self, trip_id: uuid.UUID) -> bool:
        """
        Placeholder check for downstream invoice settlement. Returns False.
        """
        pass

    @abstractmethod
    async def has_settlement(self, trip_id: uuid.UUID) -> bool:
        """
        Placeholder check for downstream cash settlement. Returns False.
        """
        pass
