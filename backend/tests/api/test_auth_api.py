import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.infrastructure.database.session import engine


@pytest.mark.asyncio
async def test_api_login_invalid_credentials_returns_401() -> None:
    """
    Asserts calling /api/v1/auth/login with wrong details returns a 401 Unauthorized status.
    """
    await engine.dispose()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login",
            json={"username_or_email": "invalid_user", "password": "wrongpassword123"},
        )
    
    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False
    assert payload["data"] is None
    await engine.dispose()


@pytest.mark.asyncio
async def test_api_token_endpoint_form_data_login_success() -> None:
    """
    Asserts calling /api/v1/auth/token with valid form data credentials returns access_token.
    """
    await engine.dispose()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Admin@123"},
        )
    
    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"
    await engine.dispose()


@pytest.mark.asyncio
async def test_api_token_endpoint_invalid_credentials_returns_401() -> None:
    """
    Asserts calling /api/v1/auth/token with invalid credentials returns a 401 status.
    """
    await engine.dispose()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/token",
            data={"username": "invalid_user", "password": "wrongpassword123"},
        )
    
    assert response.status_code == 401
    await engine.dispose()
