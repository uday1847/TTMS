import pytest
from unittest.mock import AsyncMock
from decimal import Decimal
from app.application.services.report_service import ReportService


@pytest.fixture
def mock_repos():
    return {
        "dashboard_repo": AsyncMock(),
        "financial_repo": AsyncMock(),
        "fleet_repo": AsyncMock(),
        "fuel_repo": AsyncMock(),
        "maintenance_repo": AsyncMock(),
        "trip_repo": AsyncMock(),
        "party_repo": AsyncMock()
    }

@pytest.fixture
def report_service(mock_repos):
    return ReportService(**mock_repos)

@pytest.mark.asyncio
async def test_get_dashboard_kpis_calculation(report_service, mock_repos):
    mock_repos["dashboard_repo"].get_kpis.return_value = {
        "total_trips": 100,
        "completed_trips": 80,
        "cancelled_trips": 5,
        "running_trips": 15,
        "total_income": Decimal("10000.0"),
        "total_expenses": Decimal("4000.0"),
        "gross_profit": Decimal("6000.0"),
        "active_tractors": 10
    }
    
    kpis = await report_service.get_dashboard_kpis()
    
    assert kpis["net_profit"] == Decimal("6000.0")
    assert kpis["profit_margin"] == 60.0 # (6000/10000) * 100
    # Fleet util = ((15 + 80) / (10 * 5)) * 100 = (95 / 50) * 100 = 190 -> capped at 100.0
    assert kpis["fleet_utilization"] == 100.0

@pytest.mark.asyncio
async def test_get_tractor_profitability(report_service, mock_repos):
    mock_repos["fleet_repo"].get_tractor_profitability.return_value = [
        {"tractor": "T1", "trip_count": 5, "income": Decimal("5000.0"), "trip_expense": Decimal("500.0")}
    ]
    mock_repos["fuel_repo"].get_fuel_analytics.return_value = [
        {"tractor": "T1", "fuel_cost": Decimal("1000.0")}
    ]
    mock_repos["maintenance_repo"].get_maintenance_analytics.return_value = [
        {"tractor": "T1", "maintenance_cost": Decimal("200.0")}
    ]
    
    result = await report_service.get_tractor_profitability()
    
    assert len(result) == 1
    assert result[0]["tractor"] == "T1"
    assert result[0]["fuel_cost"] == Decimal("1000.0")
    assert result[0]["maintenance_cost"] == Decimal("200.0")
    # Profit = 5000 - (1000 + 200 + 500) = 3300
    assert result[0]["profit"] == Decimal("3300.0")
