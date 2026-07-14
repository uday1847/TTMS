from typing import Protocol
import uuid
from app.domain.entities.user_preference import UserPreference

class UserPreferenceRepository(Protocol):
    async def get_by_user(self, user_id: uuid.UUID) -> UserPreference | None: ...
    async def create_or_update(self, preference: UserPreference) -> UserPreference: ...
