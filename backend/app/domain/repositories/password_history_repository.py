from typing import Protocol
import uuid
from app.domain.entities.password_history import PasswordHistory

class PasswordHistoryRepository(Protocol):
    async def create(self, history: PasswordHistory) -> PasswordHistory: ...
    async def list_by_user(self, user_id: uuid.UUID, limit: int = 5) -> list[PasswordHistory]: ...
