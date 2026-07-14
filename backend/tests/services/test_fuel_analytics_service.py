import pytest
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

from app.application.services.fuel_analytics_service import FuelAnalyticsService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def fuel_analytics_service(mock_session):
    return FuelAnalyticsService(mock_session)


@pytest.mark.asyncio
async def test_calculate_tractor_stats(fuel_analytics_service, mock_session):
    mock_result = AsyncMock()
    mock_row = AsyncMock()
    mock_row.total_amount = Decimal("15000.50")
    mock_row.avg_kmpl = Decimal("4.2")
    mock_result.fetchone.return_value = mock_row
    
    mock_session.execute.return_value = mock_result
    
    stats = await fuel_analytics_service.calculate_tractor_stats(str(uuid.uuid4()))
    
    assert stats["total_fuel_amount"] == 15000.5
    assert stats["average_kmpl"] == 4.2


@pytest.mark.asyncio
async def test_calculate_trip_stats(fuel_analytics_service, mock_session):
    mock_result = AsyncMock()
    mock_row = AsyncMock()
    mock_row.total_amount = Decimal("25000.00")
    mock_row.transaction_count = 5
    mock_result.fetchone.return_value = mock_row
    
    mock_session.execute.return_value = mock_result
    
    stats = await fuel_analytics_service.calculate_trip_stats(str(uuid.uuid4()))
    
    assert stats["total_fuel_amount"] == 25000.0
    assert stats["fuel_transaction_count"] == 5
