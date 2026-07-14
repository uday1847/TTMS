import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_export_dashboard_csv(async_client: AsyncClient, admin_token_headers: dict):
    response = await async_client.get(
        "/api/v1/reports/export/dashboard?format=csv",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=\"dashboard_export_" in response.headers["content-disposition"]
    content = response.content.decode("utf-8")
    assert "total_trips" in content

@pytest.mark.asyncio
async def test_export_profitability_excel(async_client: AsyncClient, admin_token_headers: dict):
    response = await async_client.get(
        "/api/v1/reports/export/profitability?format=xlsx",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.content.startswith(b'PK')
