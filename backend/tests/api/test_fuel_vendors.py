import pytest
import uuid
from httpx import AsyncClient

from app.domain.enums.fuel_station_type import FuelStationType
from app.domain.enums.fuel_type import FuelType
from app.domain.enums.fuel_payment_mode import FuelPaymentMode


@pytest.mark.asyncio
async def test_create_fuel_vendor(async_client: AsyncClient, admin_token_headers: dict):
    response = await async_client.post(
        "/api/v1/fuel-vendors",
        headers=admin_token_headers,
        json={
            "name": "Reliance Petrol",
            "vendor_code": "REL-001",
            "city": "Mumbai",
            "is_company_owned": False,
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Reliance Petrol"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_fuel_vendors(async_client: AsyncClient, admin_token_headers: dict):
    # Create vendor first
    await async_client.post(
        "/api/v1/fuel-vendors",
        headers=admin_token_headers,
        json={"name": "Test Vendor", "vendor_code": "TEST-001"}
    )
    
    response = await async_client.get(
        "/api/v1/fuel-vendors?limit=10",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_update_fuel_vendor(async_client: AsyncClient, admin_token_headers: dict):
    # Create vendor first
    create_response = await async_client.post(
        "/api/v1/fuel-vendors",
        headers=admin_token_headers,
        json={"name": "Update Vendor", "vendor_code": "UPD-001"}
    )
    vendor_id = create_response.json()["id"]
    
    # Update vendor
    update_response = await async_client.put(
        f"/api/v1/fuel-vendors/{vendor_id}",
        headers=admin_token_headers,
        json={"name": "Updated Vendor Name"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Vendor Name"
