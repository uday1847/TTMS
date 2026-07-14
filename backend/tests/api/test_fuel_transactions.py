import pytest
import uuid
from httpx import AsyncClient

from app.domain.enums.fuel_station_type import FuelStationType
from app.domain.enums.fuel_type import FuelType
from app.domain.enums.fuel_payment_mode import FuelPaymentMode


@pytest.mark.asyncio
async def test_list_fuel_transactions_empty(async_client: AsyncClient, admin_token_headers: dict):
    response = await async_client.get(
        "/api/v1/fuel-transactions",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_tractor_analytics(async_client: AsyncClient, admin_token_headers: dict):
    tractor_id = str(uuid.uuid4())
    response = await async_client.get(
        f"/api/v1/fuel-transactions/analytics/tractor/{tractor_id}",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_fuel_amount" in data
    assert "average_kmpl" in data
