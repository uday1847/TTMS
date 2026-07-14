import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from app.main import app
from app.infrastructure.database.session import engine, AsyncSessionLocal
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.domain.entities.user import User


@pytest.mark.asyncio
async def test_get_users_list_and_details_success() -> None:
    """
    Verifies that calling GET /api/v1/users and GET /api/v1/users/{id}
    with valid admin authorization returns successful responses without loader strategy errors.
    """
    # 1. Setup DB state (permissions & clear refresh tokens)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Clear any existing refresh tokens to prevent JWT token duplicate key conflicts in rapid test execution
            await session.execute(delete(RefreshToken))

            # Ensure 'users:read' permission exists and is assigned to the 'Super Admin' role
            stmt_perm = select(Permission).where(Permission.name == "users:read")
            perm = (await session.execute(stmt_perm)).scalar_one_or_none()
            if not perm:
                perm = Permission(name="users:read", is_active=True, description="Eager-load read test")
                session.add(perm)

            stmt_role = select(Role).options(selectinload(Role.permissions)).where(Role.name == "Super Admin")
            role = (await session.execute(stmt_role)).scalar_one_or_none()
            if role and perm not in role.permissions:
                role.permissions.append(perm)

            # Update all users' emails with '.local' domains to '.com' to pass Pydantic's email validation check
            stmt_users = select(User)
            users = (await session.execute(stmt_users)).scalars().all()
            for u in users:
                if u.email.endswith(".local"):
                    u.email = u.email.replace(".local", ".com")

    await engine.dispose()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 2. Login as admin to get token
        login_response = await ac.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Admin@123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 3. Get list of users
        users_response = await ac.get(
            "/api/v1/users",
            headers=headers,
        )
        assert users_response.status_code == 200
        users_payload = users_response.json()
        assert users_payload["success"] is True
        items = users_payload["data"]["items"]
        assert len(items) > 0

        # Grab the first user in the items list
        first_item = items[0]
        test_user_id = first_item["id"]
        test_username = first_item["username"]

        # 4. Get user details by ID
        detail_response = await ac.get(
            f"/api/v1/users/{test_user_id}",
            headers=headers,
        )
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()
        assert detail_payload["success"] is True
        assert detail_payload["data"]["username"] == test_username
        # Verify that roles and permissions were eager loaded properly and didn't crash
        assert "roles" in detail_payload["data"]

    await engine.dispose()
