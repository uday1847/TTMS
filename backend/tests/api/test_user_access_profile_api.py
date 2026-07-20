import pytest
from httpx import ASGITransport, AsyncClient
import uuid
from app.main import app
from app.infrastructure.database.session import engine

@pytest.mark.asyncio
async def test_user_access_profile_endpoints() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Login as admin
        login_response = await ac.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Admin@123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # 2. Get list of users to find one
        users_response = await ac.get("/api/v1/users", headers=headers)
        assert users_response.status_code == 200
        users = users_response.json()["data"]["items"]
        if not users:
            pytest.skip("No users found to test access profile.")
        
        test_user_id = users[0]["id"]

        # 3. Test get access profile
        ap_response = await ac.get(f"/api/v1/users/{test_user_id}/access-profile", headers=headers)
        assert ap_response.status_code == 200
        ap_data = ap_response.json()["data"]
        assert "roles" in ap_data
        assert "effectivePermissions" in ap_data
        assert "directPermissions" in ap_data

        # 4. Test update roles (just routing test with dummy id)
        dummy_role_id = str(uuid.uuid4())
        role_response = await ac.put(
            f"/api/v1/users/{test_user_id}/roles",
            json={"role_ids": [dummy_role_id]},
            headers=headers
        )
        assert role_response.status_code in (200, 404, 422)

        # 5. Test update permissions
        perm_response = await ac.put(
            f"/api/v1/users/{test_user_id}/permissions",
            json={"grant_permissions": ["users:read"], "revoke_permissions": []},
            headers=headers
        )
        assert perm_response.status_code in (200, 404, 422)

    await engine.dispose()
