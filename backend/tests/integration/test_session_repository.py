import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.entities.user_session import UserSession
from app.domain.enums.session_status import SessionStatus
from app.infrastructure.repositories.session_repository import SQLAlchemySessionRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

@pytest.mark.asyncio
async def test_sqlalchemy_session_repository_crud(db_session: AsyncSession) -> None:
    session_repo = SQLAlchemySessionRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    
    # 1. Arrange User
    user = User(
        email=f"session_test_{uuid.uuid4().hex[:8]}@ttms.com",
        username=f"session_user_{uuid.uuid4().hex[:8]}",
        password_hash="hash",
        first_name="Session",
        last_name="Tester",
        is_active=True,
    )
    
    async with db_session.begin():
        created_user = await user_repo.create(user)
    
    # 2. Arrange Session
    jti = f"jti_{uuid.uuid4().hex[:8]}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=1)
    
    session = UserSession(
        user_id=created_user.id,
        refresh_token_jti=jti,
        device_fingerprint="device123",
        ip_address="127.0.0.1",
        user_agent="pytest",
        expires_at=expires_at,
        status=SessionStatus.ACTIVE
    )
    
    # 3. Act
    async with db_session.begin():
        created_session = await session_repo.create(session)
        
    # 4. Assert
    retrieved = await session_repo.get_by_id(created_session.id)
    assert retrieved is not None
    assert retrieved.refresh_token_jti == jti
    assert retrieved.user_id == created_user.id
    
    # Test revoke all for user
    await session_repo.revoke_all_for_user(created_user.id)
    await db_session.commit()
    
    revoked = await session_repo.get_by_id(created_session.id)
    assert revoked.status == SessionStatus.REVOKED
    
    # Cleanup
    await session_repo.delete(revoked.id)
    await user_repo.delete(created_user.id)
    await db_session.commit()
