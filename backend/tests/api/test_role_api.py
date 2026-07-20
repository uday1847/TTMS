import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from app.main import app
from app.infrastructure.database.session import engine, AsyncSessionLocal
from app.domain.entities.refresh_token import RefreshToken

@pytest.mark.asyncio
async def test_create_and_list_roles() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(delete(RefreshToken))
    await engine.dispose()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_response = await ac.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Admin@123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        import uuid
        dynamic_name = f"api_test_role_{str(uuid.uuid4())[:8]}"
        
        # 1. Create a Role
        create_payload = {
            "name": dynamic_name,
            "displayName": "API Test Role",
            "description": "A role created for API tests"
        }
        create_resp = await ac.post("/api/v1/roles", json=create_payload, headers=headers)
        assert create_resp.status_code == 201
        
        data = create_resp.json()["data"]
        assert data["name"] == dynamic_name
        assert data["displayName"] == "API Test Role"
        role_id = data["id"]
        
        # 2. List Roles
        list_resp = await ac.get("/api/v1/roles", headers=headers)
        assert list_resp.status_code == 200
        
        roles = list_resp.json()["data"]
        assert len(roles) > 0
        if not any(r["id"] == role_id for r in roles):
            print(f"Role IDs found: {[r['id'] for r in roles]}")
            print(f"Expected role ID: {role_id}")
            assert False, "Role not found in list"
        
        # 3. Delete Role
        delete_resp = await ac.delete(f"/api/v1/roles/{role_id}", headers=headers)
        assert delete_resp.status_code == 200
    await engine.dispose()
