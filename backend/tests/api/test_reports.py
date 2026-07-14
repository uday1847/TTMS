import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_dashboard_kpis(async_client: AsyncClient, admin_token_headers: dict):
    response = await async_client.get(
        "/api/v1/reports/dashboard/kpi",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_trips" in data
    assert "net_profit" in data
    assert "fleet_utilization" in data

@pytest.mark.asyncio
async def test_get_dashboard_summary(async_client: AsyncClient, admin_token_headers: dict):
    response = await async_client.get(
        "/api/v1/reports/dashboard/summary",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "revenue_chart" in data
    assert "tractor_profitability" in data

@pytest.mark.asyncio
async def test_get_tractor_profitability(async_client: AsyncClient, admin_token_headers: dict):
    response = await async_client.get(
        "/api/v1/reports/profitability",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
