from abc import ABC, abstractmethod
import uuid

from app.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(ABC):
    """
    RefreshToken Repository interface detailing token lifecycle controls.
    """

    @abstractmethod
    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """
        Stores a newly generated refresh token.
        """
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> RefreshToken | None:
        """
        Retrieves a token record for rotation or validation checks.
        """
        pass

    @abstractmethod
    async def revoke_user_tokens(self, user_id: uuid.UUID) -> None:
        """
        Revokes all active refresh tokens belonging to a user (e.g. on logout/security breach).
        """
        pass
