from typing import Protocol
import uuid
from app.domain.entities.permission import Permission

class PermissionRepository(Protocol):
    async def list_all(self) -> list[Permission]: ...
    async def get_by_ids(self, permission_ids: list[uuid.UUID]) -> list[Permission]: ...
