from abc import ABC, abstractmethod

from app.domain.entities.role import Role
from app.domain.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role], ABC):
    """
    Role Repository interface detailing role query behaviors.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None:
        """
        Retrieves a role definition by role code name.
        """
        pass
