import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.application.services.session_service import SessionService
from app.domain.entities.user_session import UserSession
from app.domain.enums.session_status import SessionStatus

@pytest.fixture
def mock_session_repository():
    return AsyncMock()

@pytest.fixture
def session_service(mock_session_repository):
    return SessionService(mock_session_repository)

@pytest.mark.asyncio
async def test_create_session(session_service, mock_session_repository):
    user_id = uuid.uuid4()
    jti = "test-jti-123"
    
    mock_session = UserSession(
        id=uuid.uuid4(),
        user_id=user_id,
        refresh_token_jti=jti,
        status=SessionStatus.ACTIVE,
        expires_at=datetime.now(timezone.utc)
    )
    mock_session_repository.create.return_value = mock_session
    
    session = await session_service.create_session(
        user_id=user_id,
        jti=jti,
        device_fingerprint="device1",
        ip_address="127.0.0.1",
        user_agent="pytest"
    )
    
    mock_session_repository.create.assert_called_once()
    args, _ = mock_session_repository.create.call_args
    created_session: UserSession = args[0]
    
    assert created_session.user_id == user_id
    assert created_session.refresh_token_jti == jti
    assert created_session.device_fingerprint == "device1"
    assert created_session.ip_address == "127.0.0.1"
    assert created_session.user_agent == "pytest"
    
    assert session.id == mock_session.id

@pytest.mark.asyncio
async def test_revoke_session_found(session_service, mock_session_repository):
    session_id = uuid.uuid4()
    mock_session = UserSession(id=session_id, user_id=uuid.uuid4(), refresh_token_jti="jti", status=SessionStatus.ACTIVE, expires_at=datetime.now(timezone.utc))
    
    mock_session_repository.get_by_id.return_value = mock_session
    
    await session_service.revoke_session(session_id)
    
    mock_session_repository.get_by_id.assert_called_once_with(session_id)
    mock_session_repository.delete.assert_called_once_with(mock_session)

@pytest.mark.asyncio
async def test_revoke_session_not_found(session_service, mock_session_repository):
    session_id = uuid.uuid4()
    mock_session_repository.get_by_id.return_value = None
    
    await session_service.revoke_session(session_id)
    
    mock_session_repository.get_by_id.assert_called_once_with(session_id)
    mock_session_repository.delete.assert_not_called()

@pytest.mark.asyncio
async def test_revoke_all_sessions(session_service, mock_session_repository):
    user_id = uuid.uuid4()
    
    await session_service.revoke_all_sessions(user_id)
    
    mock_session_repository.revoke_all_for_user.assert_called_once_with(user_id)
