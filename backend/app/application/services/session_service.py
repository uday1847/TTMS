import uuid
from datetime import datetime, timezone, timedelta

from app.domain.entities.user_session import UserSession
from app.domain.repositories.session_repository import SessionRepository
from app.domain.enums.session_status import SessionStatus
from app.core.security import security_settings

class SessionService:
    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository

    async def create_session(self, user_id: uuid.UUID, jti: str, device_fingerprint: str | None, ip_address: str | None, user_agent: str | None) -> UserSession:
        expires_at = datetime.now(timezone.utc) + timedelta(days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        session = UserSession(
            user_id=user_id,
            refresh_token_jti=jti,
            device_fingerprint=device_fingerprint,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        return await self.session_repository.create(session)

    async def get_by_jti(self, jti: str) -> UserSession | None:
        return await self.session_repository.get_by_refresh_jti(jti)

    async def revoke_session(self, session_id: uuid.UUID) -> None:
        session = await self.session_repository.get_by_id(session_id)
        if session:
            session.status = SessionStatus.REVOKED
            await self.session_repository.update(session)

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        await self.session_repository.revoke_all_for_user(user_id)
