from abc import ABC, abstractmethod
from typing import Sequence
import uuid

from app.domain.entities.user import User
from app.domain.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User], ABC):
    """
    User Repository interface detailing user query behaviors.
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieves a user profile by email address.
        """
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """
        Retrieves a user profile by username.
        """
        pass

    @abstractmethod
    async def get_with_roles_and_permissions(self, user_id: uuid.UUID) -> User | None:
        """
        Loads a user eager-loading relationship mappings (roles & permissions).
        """
        pass

    @abstractmethod
    async def search_users(self, query: str, page: int, size: int) -> tuple[Sequence[User], int]:
        """
        Searches users matching query against email, username, first_name, and last_name.
        Returns paginated results (items, total).
        """
        pass
