from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.domain.entities.user_preference import UserPreference
from app.domain.repositories.user_preference_repository import UserPreferenceRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository

class SQLAlchemyUserPreferenceRepository(SQLAlchemyBaseRepository[UserPreference], UserPreferenceRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserPreference)

    async def get_by_user(self, user_id: uuid.UUID) -> UserPreference | None:
        stmt = select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.deleted_at.is_(None)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_or_update(self, preference: UserPreference) -> UserPreference:
        existing = await self.get_by_user(preference.user_id)
        if existing:
            # Update fields
            existing.theme = preference.theme
            existing.language = preference.language
            existing.timezone = preference.timezone
            existing.date_format = preference.date_format
            existing.number_format = preference.number_format
            existing.dashboard_layout = preference.dashboard_layout
            existing.notification_settings = preference.notification_settings
            await self.session.flush()
            return existing
        else:
            self.session.add(preference)
            await self.session.flush()
            return preference
