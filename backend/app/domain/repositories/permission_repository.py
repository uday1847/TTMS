from abc import ABC, abstractmethod

from app.domain.entities.permission import Permission
from app.domain.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[Permission], ABC):
    """
    Permission Repository interface detailing permission query behaviors.
    """

    @abstractmethod
    async def get_by_code(self, code: str) -> Permission | None:
        """
        Retrieves a permission definition by permission code name.
        """
        pass
