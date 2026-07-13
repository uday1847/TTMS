import uuid
from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.party import Party
from app.domain.repositories.base_repository import BaseRepository


class PartyRepository(BaseRepository[Party], ABC):
    """
    Party Repository contract defining domain-specific database queries.
    """

    @abstractmethod
    async def get_by_mobile(self, mobile_number: str) -> Party | None:
        """
        Retrieves a party by their unique mobile/contact number.
        """
        pass

    @abstractmethod
    async def get_by_gst(self, gst_number: str) -> Party | None:
        """
        Retrieves a party by their unique GSTIN number.
        """
        pass

    @abstractmethod
    async def get_by_pan(self, pan_number: str) -> Party | None:
        """
        Retrieves a party by their unique PAN number.
        """
        pass

    @abstractmethod
    async def has_active_trips(self, party_id: uuid.UUID) -> bool:
        """
        Checks if the party is linked to any active (is_active=True) trip.
        """
        pass

    @abstractmethod
    async def get_parties(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        party_type_filter: str | None = None,
        status_filter: str | None = None,
        city_filter: str | None = None,
        state_filter: str | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Party], int]:
        """
        Retrieves a page of parties matching search query, status filters,
        city, state, and created date range parameters.
        """
        pass
