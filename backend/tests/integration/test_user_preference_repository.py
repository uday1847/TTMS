import pytest
import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.entities.user_preference import UserPreference
from app.infrastructure.repositories.user_preference_repository import SQLAlchemyUserPreferenceRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

@pytest.mark.asyncio
async def test_sqlalchemy_user_preference_repository_crud(db_session: AsyncSession) -> None:
    pref_repo = SQLAlchemyUserPreferenceRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    
    # 1. Arrange User
    user = User(
        email=f"pref_test_{uuid.uuid4().hex[:8]}@ttms.com",
        username=f"pref_user_{uuid.uuid4().hex[:8]}",
        password_hash="hash",
        first_name="Pref",
        last_name="Tester",
        is_active=True,
    )
    
    created_user = await user_repo.create(user)
    await db_session.commit()
    
    # 2. Arrange Preference
    pref = UserPreference(
        user_id=created_user.id,
        theme="dark",
        language="en",
        timezone="UTC",
        date_format="YYYY-MM-DD",
        number_format="en-US"
    )
    
    # 3. Act
    created_pref = await pref_repo.create(pref)
    await db_session.commit()
        
    # 4. Assert
    retrieved = await pref_repo.get_by_user(created_user.id)
    assert retrieved is not None
    assert retrieved.theme == "dark"
    assert retrieved.language == "en"
    
    # Update
    retrieved.theme = "light"
    await pref_repo.update(retrieved)
    await db_session.commit()
        
    updated = await pref_repo.get_by_user(created_user.id)
    assert updated.theme == "light"
    
    # Cleanup
    await pref_repo.delete(updated.id)
    await user_repo.delete(created_user.id)
    await db_session.commit()
