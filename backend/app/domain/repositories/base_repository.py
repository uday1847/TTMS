from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar
import uuid

from app.infrastructure.database.base import BaseEntity

# Generic type parameter bounded by our BaseEntity layout
T = TypeVar("T", bound=BaseEntity)


class BaseRepository(ABC, Generic[T]):
    """
    Generic Abstract Base Repository interface.
    Defines database-agnostic CRUD and pagination contracts.
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Persists a new entity in the database.
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> T | None:
        """
        Retrieves a single entity by its primary key ID.
        Returns None if not found or soft-deleted.
        """
        pass

    @abstractmethod
    async def get_all(self) -> Sequence[T]:
        """
        Retrieves all non-deleted entities.
        """
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Updates an existing entity's state.
        """
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID, soft: bool = True) -> bool:
        """
        Removes an entity by ID. Supports soft-delete by default.
        Returns True if successful, False if the entity was not found.
        """
        pass

    @abstractmethod
    async def exists(self, id: uuid.UUID) -> bool:
        """
        Checks if an active (non-deleted) entity exists by ID.
        """
        pass

    @abstractmethod
    async def count(self) -> int:
        """
        Returns the total count of active (non-deleted) records.
        """
        pass

    @abstractmethod
    async def paginate(self, page: int, size: int) -> tuple[Sequence[T], int]:
        """
        Returns a paginated slice of active records (items) and the total count.
        page: 1-indexed current page number.
        size: Page limit size.
        """
        pass
