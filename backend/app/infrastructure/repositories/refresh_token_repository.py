import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository


class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    """
    SQLAlchemy implementation of the RefreshTokenRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_user_tokens(self, user_id: uuid.UUID) -> None:
        # Securely deletes all existing refresh tokens for a user (hard delete to clear session state)
        stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.flush()
