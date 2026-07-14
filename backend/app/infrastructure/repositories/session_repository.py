from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone

from app.domain.entities.user_session import UserSession
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository
from app.domain.enums.session_status import SessionStatus

class SQLAlchemySessionRepository(SQLAlchemyBaseRepository[UserSession], SessionRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserSession)

    async def get_by_refresh_jti(self, jti: str) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession.refresh_token_jti == jti,
            UserSession.deleted_at.is_(None)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[UserSession]:
        stmt = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.deleted_at.is_(None)
        ).order_by(UserSession.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.status == SessionStatus.ACTIVE,
                UserSession.deleted_at.is_(None)
            )
            .values(status=SessionStatus.REVOKED)
        )
        await self.session.execute(stmt)

    async def get_active_sessions_count(self) -> int:
        stmt = select(func.count(UserSession.id)).where(
            UserSession.status == SessionStatus.ACTIVE,
            UserSession.deleted_at.is_(None)
        )
        return (await self.session.execute(stmt)).scalar_one()
