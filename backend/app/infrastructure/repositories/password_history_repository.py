from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.domain.entities.password_history import PasswordHistory
from app.domain.repositories.password_history_repository import PasswordHistoryRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository

class SQLAlchemyPasswordHistoryRepository(SQLAlchemyBaseRepository[PasswordHistory], PasswordHistoryRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PasswordHistory)

    async def list_by_user(self, user_id: uuid.UUID, limit: int = 5) -> list[PasswordHistory]:
        stmt = (
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user_id, PasswordHistory.deleted_at.is_(None))
            .order_by(PasswordHistory.created_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())
