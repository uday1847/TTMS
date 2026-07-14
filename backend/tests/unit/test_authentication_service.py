import uuid
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta

from app.application.services.authentication_service import AuthenticationService
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.entities.password_history import PasswordHistory
from app.application.dtos.auth import LoginRequest, ChangePasswordRequest
from app.domain.enums.user_status import UserStatus
from app.domain.enums.login_result import LoginResult
from app.domain.exceptions.base import UnauthorizedException, ValidationException

@pytest.fixture
def mock_user_repository():
    return AsyncMock()

@pytest.fixture
def mock_login_history_repository():
    return AsyncMock()

@pytest.fixture
def mock_password_history_repository():
    return AsyncMock()

@pytest.fixture
def mock_session_service():
    return AsyncMock()

@pytest.fixture
def auth_service(mock_user_repository, mock_login_history_repository, mock_password_history_repository, mock_session_service):
    return AuthenticationService(
        user_repository=mock_user_repository,
        login_history_repository=mock_login_history_repository,
        password_history_repository=mock_password_history_repository,
        session_service=mock_session_service
    )

@pytest.mark.asyncio
@patch("app.application.services.authentication_service.security_settings")
async def test_login_success(mock_security, auth_service, mock_user_repository, mock_login_history_repository, mock_session_service):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@example.com", password_hash="hash", status=UserStatus.ACTIVE, token_version=1)
    mock_user_repository.get_by_email.return_value = mock_user
    mock_user_repository.get_with_roles_and_permissions.return_value = mock_user
    mock_security.verify_password.return_value = True
    
    dto = LoginRequest(username_or_email="test@example.com", password="password")
    
    response = await auth_service.login(dto)
    
    mock_login_history_repository.create.assert_called_once()
    assert response.user_id == user_id
    assert response.access_token is not None
    assert response.refresh_token is not None
    mock_session_service.create_session.assert_called_once()

@pytest.mark.asyncio
async def test_login_invalid_user(auth_service, mock_user_repository):
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.get_by_username.return_value = None
    
    dto = LoginRequest(username_or_email="wrong", password="password")
    
    with pytest.raises(UnauthorizedException, match="Invalid credentials"):
        await auth_service.login(dto)

@pytest.mark.asyncio
async def test_login_inactive_user(auth_service, mock_user_repository, mock_login_history_repository):
    mock_user = User(email="test@example.com", status=UserStatus.INACTIVE)
    mock_user_repository.get_by_email.return_value = mock_user
    
    dto = LoginRequest(username_or_email="test@example.com", password="password")
    
    with pytest.raises(UnauthorizedException, match="Account is inactive"):
        await auth_service.login(dto)
    
    mock_login_history_repository.create.assert_called_once()
    args, _ = mock_login_history_repository.create.call_args
    assert args[0].result == LoginResult.FAILED_INACTIVE

@pytest.mark.asyncio
async def test_login_locked_user(auth_service, mock_user_repository, mock_login_history_repository):
    mock_user = User(
        email="test@example.com", 
        status=UserStatus.LOCKED,
        locked_until=datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    mock_user_repository.get_by_email.return_value = mock_user
    
    dto = LoginRequest(username_or_email="test@example.com", password="password")
    
    with pytest.raises(UnauthorizedException, match="Account is locked"):
        await auth_service.login(dto)
    
    mock_login_history_repository.create.assert_called_once()
    args, _ = mock_login_history_repository.create.call_args
    assert args[0].result == LoginResult.FAILED_LOCKED

@pytest.mark.asyncio
@patch("app.application.services.authentication_service.security_settings")
async def test_login_wrong_password_lockout(mock_security, auth_service, mock_user_repository):
    mock_user = User(email="test@example.com", password_hash="hash", status=UserStatus.ACTIVE, failed_login_attempts=4, token_version=1)
    mock_user_repository.get_by_email.return_value = mock_user
    mock_security.verify_password.return_value = False
    mock_security.MAX_LOGIN_ATTEMPTS = 5
    mock_security.ACCOUNT_LOCK_DURATION_MINUTES = 15
    
    dto = LoginRequest(username_or_email="test@example.com", password="wrong")
    
    with pytest.raises(UnauthorizedException, match="Invalid credentials"):
        await auth_service.login(dto)
        
    assert mock_user.failed_login_attempts == 5
    assert mock_user.status == UserStatus.LOCKED
    assert mock_user.locked_until is not None
    mock_user_repository.update.assert_called_once_with(mock_user)

@pytest.mark.asyncio
@patch("app.application.services.authentication_service.security_settings")
async def test_change_password_success(mock_security, auth_service, mock_user_repository, mock_password_history_repository, mock_session_service):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, password_hash="old_hash", token_version=1)
    mock_user_repository.get_by_id.return_value = mock_user
    mock_security.verify_password.side_effect = lambda given, stored: given == "old" and stored == "old_hash" or False
    mock_security.get_password_hash.return_value = "new_hash"
    mock_security.PASSWORD_HISTORY_COUNT = 3
    
    mock_password_history_repository.list_by_user.return_value = []
    
    dto = ChangePasswordRequest(old_password="old", new_password="new")
    
    await auth_service.change_password(user_id, dto)
    
    assert mock_user.password_hash == "new_hash"
    assert mock_user.token_version == 2
    mock_user_repository.update.assert_called_once_with(mock_user)
    mock_password_history_repository.create.assert_called_once()
    mock_session_service.revoke_all_sessions.assert_called_once_with(user_id)

@pytest.mark.asyncio
@patch("app.application.services.authentication_service.security_settings")
async def test_change_password_reuse_prevented(mock_security, auth_service, mock_user_repository, mock_password_history_repository):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, password_hash="old_hash", token_version=1)
    mock_user_repository.get_by_id.return_value = mock_user
    
    # Old password verified successfully, but new password matches history
    mock_security.verify_password.side_effect = lambda given, stored: True 
    mock_security.PASSWORD_HISTORY_COUNT = 3
    
    history_record = PasswordHistory(password_hash="recent_hash")
    mock_password_history_repository.list_by_user.return_value = [history_record]
    
    dto = ChangePasswordRequest(old_password="old", new_password="recent")
    
    with pytest.raises(ValidationException, match="Password was used recently"):
        await auth_service.change_password(user_id, dto)
