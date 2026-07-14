from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone

from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository

class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    """
    SQLAlchemy implementation of the RefreshTokenRepository interface.
    (Note: RefreshToken is not a BaseEntity, it uses standard CRUD without soft deletes)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, token: RefreshToken) -> RefreshToken:
        # Entity is bound to session, flush is enough
        await self.session.flush()
        return token

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None)
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
