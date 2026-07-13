from datetime import datetime, timedelta, timezone
import logging
from typing import Any
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.domain.entities.refresh_token import RefreshToken
from app.domain.exceptions.auth import (
    InvalidCredentialsException,
    PermissionDeniedException,
    TokenExpiredException,
)
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.user_repository import UserRepository
from app.schemas.auth.change_password import ChangePassword
from app.schemas.auth.login_request import LoginRequest
from app.schemas.auth.login_response import LoginResponse
from app.schemas.auth.refresh_request import RefreshRequest
from app.schemas.auth.refresh_response import RefreshResponse
from app.schemas.auth.reset_password import ResetPassword
from app.application.validators.password_validator import validate_password_complexity

logger = logging.getLogger("ttms.auth_service")


class AuthService:
    """
    Service layer managing authentication, logins, logouts, token rotations,
    and password recovery procedures using async database transactions.
    """

    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def login(self, dto: LoginRequest) -> LoginResponse:
        """
        Authenticates user credentials and generates access/refresh tokens.
        """
        logger.info(f"Attempting login for user identifier: {dto.username_or_email}")

        # Transaction boundary
        async with self.session.begin():
            # Lookup user by email or username
            user = await self.user_repository.get_by_email(dto.username_or_email)
            if not user:
                user = await self.user_repository.get_by_username(dto.username_or_email)

            if not user:
                logger.warning(f"Login failed: User {dto.username_or_email} not found.")
                raise InvalidCredentialsException()

            if not user.is_active:
                logger.warning(f"Login failed: User {user.email} is inactive.")
                raise PermissionDeniedException("User account is disabled.")

            # Validate password
            if not verify_password(dto.password, user.password_hash):
                logger.warning(f"Login failed: Incorrect password for user {user.email}.")
                raise InvalidCredentialsException()

            # Generate tokens
            access_token = create_access_token(user.id)
            refresh_token_str = create_refresh_token(user.id)

            # Save refresh token
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            refresh_token_entity = RefreshToken(
                user_id=user.id,
                token=refresh_token_str,
                expires_at=expires_at,
            )
            await self.refresh_token_repository.create(refresh_token_entity)

        logger.info(f"User {user.email} successfully logged in.")
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
        )

    async def logout(self, user_id: uuid.UUID) -> None:
        """
        Logs out a user and revokes all active sessions/tokens.
        """
        logger.info(f"Logging out user: {user_id}")
        async with self.session.begin():
            await self.refresh_token_repository.revoke_user_tokens(user_id)
        logger.info(f"User {user_id} tokens successfully revoked.")

    async def refresh_token(self, dto: RefreshRequest) -> RefreshResponse:
        """
        Refreshes access tokens and rotates refresh tokens (Single Use Token pattern).
        """
        logger.info("Token rotation requested.")
        
        try:
            payload = decode_token(dto.refresh_token)
            if payload.get("type") != "refresh":
                raise InvalidCredentialsException("Invalid token type.")
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise InvalidCredentialsException("Missing token subject.")
            user_id = uuid.UUID(user_id_str)
        except Exception as e:
            logger.warning(f"Token refresh failed: invalid token signatures. Details: {e}")
            raise InvalidCredentialsException("Invalid token signature or expired.")

        async with self.session.begin():
            # Check db trace
            token_record = await self.refresh_token_repository.get_by_token(dto.refresh_token)
            if not token_record:
                logger.warning("Token refresh failed: token not found in registry (revoked/reused).")
                # Potential token reuse attack - revoke all user tokens for safety
                await self.refresh_token_repository.revoke_user_tokens(user_id)
                raise InvalidCredentialsException("Token has been revoked.")

            if token_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                logger.warning("Token refresh failed: token expired.")
                await self.refresh_token_repository.revoke_user_tokens(user_id)
                raise TokenExpiredException()

            # Revoke old tokens
            await self.refresh_token_repository.revoke_user_tokens(user_id)

            # Generate fresh token rotation pair
            new_access_token = create_access_token(user_id)
            new_refresh_token_str = create_refresh_token(user_id)

            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            new_refresh_token_entity = RefreshToken(
                user_id=user_id,
                token=new_refresh_token_str,
                expires_at=expires_at,
            )
            await self.refresh_token_repository.create(new_refresh_token_entity)

        logger.info(f"Successfully rotated tokens for user {user_id}.")
        return RefreshResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token_str,
        )

    async def change_password(self, user_id: uuid.UUID, dto: ChangePassword) -> None:
        """
        Updates account password after verifying current password.
        """
        logger.info(f"Password update requested for user: {user_id}")
        validate_password_complexity(dto.new_password)

        async with self.session.begin():
            user = await self.user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                raise InvalidCredentialsException("User account not found or disabled.")

            if not verify_password(dto.old_password, user.password_hash):
                raise InvalidCredentialsException("Incorrect current password.")

            user.password_hash = hash_password(dto.new_password)
            # Revoke all sessions on password alteration for security
            await self.refresh_token_repository.revoke_user_tokens(user_id)

        logger.info(f"Password successfully changed for user {user_id}.")

    async def forgot_password(self, email: str) -> None:
        """
        Initiates password reset flows. Generates a short-lived recovery token.
        """
        logger.info(f"Password recovery requested for email: {email}")
        
        user = await self.user_repository.get_by_email(email)
        if not user:
            # Prevent email enumeration disclosures
            logger.warning(f"Recovery request: email '{email}' not registered. Ignoring.")
            return

        # Generate a temporary 15-minute token
        reset_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=15),
        )

        # Structured log simulating email dispatch payload
        logger.info(
            f"[SYSTEM ACTION] PASSWORD RESET INITIATED\n"
            f"User ID: {user.id}\n"
            f"Email: {user.email}\n"
            f"Reset Token: {reset_token}\n"
            f"Expiry: 15 minutes\n"
        )

    async def reset_password(self, dto: ResetPassword) -> None:
        """
        Resets user password using a verified recovery token.
        """
        logger.info("Completing password recovery reset.")
        validate_password_complexity(dto.new_password)

        try:
            payload = decode_token(dto.token)
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise InvalidCredentialsException("Invalid reset token subject.")
            user_id = uuid.UUID(user_id_str)
        except Exception:
            raise InvalidCredentialsException("Reset token is invalid or has expired.")

        async with self.session.begin():
            user = await self.user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                raise InvalidCredentialsException("User account not found or disabled.")

            user.password_hash = hash_password(dto.new_password)
            await self.refresh_token_repository.revoke_user_tokens(user_id)

        logger.info(f"Password successfully reset for user {user_id}.")
