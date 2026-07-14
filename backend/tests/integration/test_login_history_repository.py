import pytest
import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.entities.login_history import LoginHistory
from app.domain.enums.login_result import LoginResult
from app.infrastructure.repositories.login_history_repository import SQLAlchemyLoginHistoryRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

@pytest.mark.asyncio
async def test_sqlalchemy_login_history_repository_crud(db_session: AsyncSession) -> None:
    history_repo = SQLAlchemyLoginHistoryRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    
    # 1. Arrange User
    user = User(
        email=f"login_test_{uuid.uuid4().hex[:8]}@ttms.com",
        username=f"login_user_{uuid.uuid4().hex[:8]}",
        password_hash="hash",
        first_name="Login",
        last_name="Tester",
        is_active=True,
    )
    
    created_user = await user_repo.create(user)
    await db_session.commit()
    
    # 2. Arrange Login History
    history1 = LoginHistory(
        user_id=created_user.id,
        ip_address="192.168.1.1",
        user_agent="pytest",
        result=LoginResult.SUCCESS
    )
    
    history2 = LoginHistory(
        user_id=created_user.id,
        ip_address="192.168.1.1",
        user_agent="pytest",
        result=LoginResult.FAILED_BAD_CREDENTIALS
    )
    
    # 3. Act
    h1 = await history_repo.create(history1)
    h2 = await history_repo.create(history2)
    await db_session.commit()
        
    # 4. Assert
    items, total = await history_repo.list_by_user(user_id=created_user.id)
    assert total == 2
    assert len(items) == 2
    
    # Cleanup
    await history_repo.delete(h1.id)
    await history_repo.delete(h2.id)
    await user_repo.delete(created_user.id)
    await db_session.commit()
