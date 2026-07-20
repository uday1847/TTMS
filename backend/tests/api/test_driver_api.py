import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from app.main import app
from app.infrastructure.database.session import engine, AsyncSessionLocal
from app.domain.entities.refresh_token import RefreshToken
import uuid

@pytest.mark.asyncio
async def test_driver_api_lifecycle() -> None:
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
        
        dyn_suffix = str(uuid.uuid4())[:8].upper()
        driver_code = f"DRV-{dyn_suffix}"
        license_num = f"LIC-{dyn_suffix}"

        import re
        phone_num = "+91 " + "".join(re.findall(r"\d+", str(uuid.uuid4().int)))[:10]
        
        # 1. Create a Driver
        create_payload = {
            "name": "API Test Driver",
            "employeeCode": driver_code,
            "licenseNumber": license_num,
            "licenseExpiry": "2030-12-31",
            "licenseClass": "Heavy Duty",
            "contactPhone": phone_num,
            "fixedSalary": "25000.00",
            "commissionPercentage": "5.0",
            "driverType": "SALARIED",
            "currentStatus": "available"
        }
        create_resp = await ac.post("/api/v1/drivers", json=create_payload, headers=headers)
        assert create_resp.status_code == 201, create_resp.text
        
        data = create_resp.json()["data"]
        assert data["name"] == "API Test Driver"
        assert data["employeeCode"] == driver_code
        driver_id = data["id"]
        
        # 2. Get Driver
        get_resp = await ac.get(f"/api/v1/drivers/{driver_id}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["id"] == driver_id

        # 3. List Drivers
        list_resp = await ac.get("/api/v1/drivers?size=50", headers=headers)
        assert list_resp.status_code == 200
        drivers = list_resp.json()["data"]["items"]
        assert any(d["id"] == driver_id for d in drivers)
        
        # 4. Update Driver
        update_payload = {
            "name": "API Test Driver Updated"
        }
        update_resp = await ac.put(f"/api/v1/drivers/{driver_id}", json=update_payload, headers=headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["data"]["name"] == "API Test Driver Updated"

        # 5. Delete Driver
        delete_resp = await ac.delete(f"/api/v1/drivers/{driver_id}", headers=headers)
        assert delete_resp.status_code == 200

    await engine.dispose()
