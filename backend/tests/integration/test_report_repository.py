import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.fleet_report_repository import SQLAlchemyFleetReportRepository
from app.infrastructure.repositories.financial_report_repository import SQLAlchemyFinancialReportRepository

@pytest.mark.asyncio
async def test_fleet_profitability_empty(db_session: AsyncSession):
    repo = SQLAlchemyFleetReportRepository(db_session)
    result = await repo.get_tractor_profitability()
    
    assert isinstance(result, list)
    assert len(result) == 0

@pytest.mark.asyncio
async def test_expense_breakdown_empty(db_session: AsyncSession):
    repo = SQLAlchemyFinancialReportRepository(db_session)
    result = await repo.get_expense_breakdown()
    
    assert isinstance(result, list)
    assert len(result) == 0
