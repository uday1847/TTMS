import pytest
import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.entities.password_history import PasswordHistory
from app.infrastructure.repositories.password_history_repository import SQLAlchemyPasswordHistoryRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

@pytest.mark.asyncio
async def test_sqlalchemy_password_history_repository_crud(db_session: AsyncSession) -> None:
    history_repo = SQLAlchemyPasswordHistoryRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    
    # 1. Arrange User
    user = User(
        email=f"pass_test_{uuid.uuid4().hex[:8]}@ttms.com",
        username=f"pass_user_{uuid.uuid4().hex[:8]}",
        password_hash="hash",
        first_name="Pass",
        last_name="Tester",
        is_active=True,
    )
    
    async with db_session.begin():
        created_user = await user_repo.create(user)
    
    # 2. Arrange Password History
    history1 = PasswordHistory(
        user_id=created_user.id,
        password_hash="hash_old_1"
    )
    
    history2 = PasswordHistory(
        user_id=created_user.id,
        password_hash="hash_old_2"
    )
    
    # 3. Act
    h1 = await history_repo.create(history1)
    h2 = await history_repo.create(history2)
    await db_session.commit()
        
    # 4. Assert
    items = await history_repo.list_by_user(user_id=created_user.id, limit=3)
    assert len(items) == 2
    hashes = [i.password_hash for i in items]
    assert "hash_old_1" in hashes
    assert "hash_old_2" in hashes
    
    # Cleanup
    await db_session.execute(delete(PasswordHistory).where(PasswordHistory.id.in_([h1.id, h2.id])))
    await user_repo.delete(created_user.id)
    await db_session.commit()
