import uuid
from datetime import datetime, timezone, timedelta

from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.login_history_repository import LoginHistoryRepository
from app.domain.repositories.password_history_repository import PasswordHistoryRepository
from app.application.services.jwt_service import JWTService
from app.application.services.session_service import SessionService
from app.core.security import security_settings
from app.application.dtos.auth import LoginRequest, LoginResponse, RefreshTokenRequest, ChangePasswordRequest
from app.domain.exceptions.base import UnauthorizedException, ValidationException
from app.domain.enums.user_status import UserStatus
from app.domain.enums.login_result import LoginResult
from app.domain.entities.login_history import LoginHistory
from app.domain.entities.password_history import PasswordHistory

class AuthenticationService:
    def __init__(
        self,
        user_repository: UserRepository,
        login_history_repository: LoginHistoryRepository,
        password_history_repository: PasswordHistoryRepository,
        session_service: SessionService
    ):
        self.user_repository = user_repository
        self.login_history_repository = login_history_repository
        self.password_history_repository = password_history_repository
        self.session_service = session_service

    async def login(self, dto: LoginRequest, ip_address: str | None = None, user_agent: str | None = None) -> LoginResponse:
        user = await self.user_repository.get_by_email(dto.username_or_email)
        if not user:
            user = await self.user_repository.get_by_username(dto.username_or_email)

        if not user:
            raise UnauthorizedException("Invalid credentials")

        # Record login attempt baseline
        login_history = LoginHistory(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=dto.device_fingerprint,
            result=LoginResult.SUCCESS
        )

        if user.status == UserStatus.INACTIVE:
            login_history.result = LoginResult.FAILED_INACTIVE
            await self.login_history_repository.create(login_history)
            raise UnauthorizedException("Account is inactive")

        if user.status == UserStatus.LOCKED:
            if user.locked_until and user.locked_until > datetime.now(timezone.utc):
                login_history.result = LoginResult.FAILED_LOCKED
                await self.login_history_repository.create(login_history)
                raise UnauthorizedException("Account is locked")
            else:
                # Lock expired
                user.status = UserStatus.ACTIVE
                user.failed_login_attempts = 0
                user.locked_until = None
                await self.user_repository.update(user)

        is_valid = security_settings.verify_password(dto.password, user.password_hash)
        if not is_valid:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= security_settings.MAX_LOGIN_ATTEMPTS:
                user.status = UserStatus.LOCKED
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=security_settings.ACCOUNT_LOCK_DURATION_MINUTES)
                user.token_version += 1
            await self.user_repository.update(user)
            login_history.result = LoginResult.FAILED_BAD_CREDENTIALS
            await self.login_history_repository.create(login_history)
            raise UnauthorizedException("Invalid credentials")

        # Success
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        await self.user_repository.update(user)
        
        await self.login_history_repository.create(login_history)

        user_with_perms = await self.user_repository.get_with_roles_and_permissions(user.id)
        permissions = []
        if user_with_perms:
            for role in user_with_perms.roles:
                for perm in role.permissions:
                    permissions.append(perm.name)
        
        access_token = JWTService.create_access_token(user.id, user.email, user.token_version, permissions)
        jti = str(uuid.uuid4())
        refresh_token = JWTService.create_refresh_token(user.id, jti)

        await self.session_service.create_session(
            user_id=user.id,
            jti=jti,
            device_fingerprint=dto.device_fingerprint,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id
        )

    async def change_password(self, user_id: uuid.UUID, dto: ChangePasswordRequest) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        if not security_settings.verify_password(dto.old_password, user.password_hash):
            raise UnauthorizedException("Invalid current password")
            
        history_records = await self.password_history_repository.list_by_user(user_id, limit=security_settings.PASSWORD_HISTORY_COUNT)
        for record in history_records:
            if security_settings.verify_password(dto.new_password, record.password_hash):
                raise ValidationException("Password was used recently")

        hashed_password = security_settings.get_password_hash(dto.new_password)
        
        # Save old password to history
        await self.password_history_repository.create(PasswordHistory(
            user_id=user.id,
            password_hash=user.password_hash
        ))

        user.password_hash = hashed_password
        user.token_version += 1 # Invalidate all sessions
        await self.user_repository.update(user)
        
        # Revoke all sessions since password changed
        await self.session_service.revoke_all_sessions(user.id)
