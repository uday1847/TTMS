import pytest
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


@pytest.mark.asyncio
async def test_sqlalchemy_user_repository_create_and_retrieve(db_session: AsyncSession) -> None:
    """
    Integration test asserting User creation and retrieval transactions in PostgreSQL.
    """
    # 1. Arrange
    user_repo = SQLAlchemyUserRepository(db_session)
    user = User(
        email="integration@ttms.com",
        username="integration_user",
        password_hash="mocked_hash",
        first_name="Integration",
        last_name="Tester",
        is_active=True,
    )

    # 2. Act
    # Inside transaction
    async with db_session.begin():
        await user_repo.create(user)

    # 3. Assert
    retrieved = await user_repo.get_by_email("integration@ttms.com")
    assert retrieved is not None
    assert retrieved.username == "integration_user"
    assert retrieved.id == user.id


@pytest.mark.asyncio
async def test_sqlalchemy_user_repository_get_with_roles_and_permissions(db_session: AsyncSession) -> None:
    """
    Test verifying that we can retrieve a user with their associated roles and permissions using selectinload.
    """
    user_repo = SQLAlchemyUserRepository(db_session)
    
    # 1. Arrange
    permission_code = f"integration_perm_{uuid.uuid4().hex[:8]}"
    role_name = f"integration_role_{uuid.uuid4().hex[:8]}"
    user_email = f"integration_user_{uuid.uuid4().hex[:8]}@ttms.com"
    
    permission = Permission(code=permission_code, is_active=True)
    role = Role(name=role_name, display_name="Integration Role", is_active=True, permissions=[permission])
    user = User(
        email=user_email,
        username=f"int_user_{uuid.uuid4().hex[:8]}",
        password_hash="mocked_hash",
        first_name="Integration",
        last_name="Tester",
        is_active=True,
        roles=[role]
    )

    try:
        # 2. Act
        async with db_session.begin():
            db_session.add(permission)
            db_session.add(role)
            await user_repo.create(user)

        # 3. Assert
        retrieved = await user_repo.get_with_roles_and_permissions(user.id)
        assert retrieved is not None
        assert retrieved.email == user_email
        assert len(retrieved.roles) == 1
        assert retrieved.roles[0].name == role_name
        assert len(retrieved.roles[0].permissions) == 1
        assert retrieved.roles[0].permissions[0].code == permission_code
    finally:
        # Cleanup
        await db_session.execute(delete(User).where(User.id == user.id))
        await db_session.execute(delete(Role).where(Role.id == role.id))
        await db_session.execute(delete(Permission).where(Permission.id == permission.id))
        await db_session.commit()


@pytest.mark.asyncio
async def test_sqlalchemy_user_repository_search_users(db_session: AsyncSession) -> None:
    """
    Test verifying that we can search for users and get roles loaded successfully.
    """
    user_repo = SQLAlchemyUserRepository(db_session)
    
    user_email = f"integration_search_{uuid.uuid4().hex[:8]}@ttms.com"
    user = User(
        email=user_email,
        username=f"search_{uuid.uuid4().hex[:8]}",
        password_hash="mocked_hash",
        first_name="SearchFirst",
        last_name="Tester",
        is_active=True,
    )

    try:
        async with db_session.begin():
            await user_repo.create(user)

        # Search for this user
        items, total = await user_repo.search_users(query="SearchFirst", page=1, size=10)
        assert total >= 1
        found = next((item for item in items if item.id == user.id), None)
        assert found is not None
        assert found.email == user_email
    finally:
        await db_session.execute(delete(User).where(User.id == user.id))
        await db_session.commit()

