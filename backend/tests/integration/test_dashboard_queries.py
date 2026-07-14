import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.dashboard_repository import SQLAlchemyDashboardRepository

@pytest.mark.asyncio
async def test_dashboard_kpis_empty(db_session: AsyncSession):
    repo = SQLAlchemyDashboardRepository(db_session)
    kpis = await repo.get_kpis()
    
    assert kpis["total_trips"] == 0
    assert kpis["total_income"] == 0
    assert kpis["outstanding_receivables"] == 0
    assert kpis["active_tractors"] == 0

@pytest.mark.asyncio
async def test_dashboard_revenue_chart_empty(db_session: AsyncSession):
    repo = SQLAlchemyDashboardRepository(db_session)
    chart = await repo.get_revenue_chart()
    
    assert isinstance(chart, list)
    assert len(chart) == 0
