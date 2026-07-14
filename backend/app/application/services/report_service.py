from typing import Any, Dict, List, Optional
from datetime import date
from decimal import Decimal

from app.domain.repositories.dashboard_repository import DashboardRepository
from app.domain.repositories.financial_report_repository import FinancialReportRepository
from app.domain.repositories.fleet_report_repository import FleetReportRepository
from app.domain.repositories.fuel_report_repository import FuelReportRepository
from app.domain.repositories.maintenance_report_repository import MaintenanceReportRepository
from app.domain.repositories.trip_report_repository import TripReportRepository
from app.domain.repositories.party_report_repository import PartyReportRepository
from app.application.services.dashboard_cache_service import DashboardCacheService


class ReportService:
    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        financial_repo: FinancialReportRepository,
        fleet_repo: FleetReportRepository,
        fuel_repo: FuelReportRepository,
        maintenance_repo: MaintenanceReportRepository,
        trip_repo: TripReportRepository,
        party_repo: PartyReportRepository
    ):
        self.dashboard_repo = dashboard_repo
        self.financial_repo = financial_repo
        self.fleet_repo = fleet_repo
        self.fuel_repo = fuel_repo
        self.maintenance_repo = maintenance_repo
        self.trip_repo = trip_repo
        self.party_repo = party_repo

    async def get_dashboard_kpis(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        # Cache key based on date
        cache_key = f"dashboard:kpi:{start_date}:{end_date}"
        cached = DashboardCacheService.get(cache_key)
        if cached:
            return cached

        kpis = await self.dashboard_repo.get_kpis(start_date, end_date)
        
        # Calculate derived metrics
        # Net profit = Gross profit - Maintenance cost (mock integration for now)
        # Fleet utilization = (Running + Completed trips) / (Active Tractors * 30 days) approx
        
        # Just simple calculations
        kpis["net_profit"] = kpis["gross_profit"]
        
        if kpis["total_income"] > 0:
            kpis["profit_margin"] = (kpis["net_profit"] / kpis["total_income"]) * 100
        else:
            kpis["profit_margin"] = 0.0

        if kpis["active_tractors"] > 0:
            # simple mock utilization formula for phase 1
            trips = kpis["running_trips"] + kpis["completed_trips"]
            kpis["fleet_utilization"] = min((trips / (kpis["active_tractors"] * 5)) * 100, 100.0)

        DashboardCacheService.set(cache_key, kpis)
        return kpis

    async def get_revenue_chart(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        return await self.dashboard_repo.get_revenue_chart(start_date, end_date)

    async def get_expense_chart(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        return await self.financial_repo.get_expense_breakdown(start_date, end_date)

    async def get_fuel_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        return await self.fuel_repo.get_fuel_analytics(start_date, end_date)

    async def get_maintenance_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        return await self.maintenance_repo.get_maintenance_analytics(start_date, end_date)

    async def get_tractor_profitability(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        data = await self.fleet_repo.get_tractor_profitability(start_date, end_date)
        
        # Merge with fuel and maintenance costs logically
        fuel_data = {row["tractor"]: row["fuel_cost"] for row in await self.fuel_repo.get_fuel_analytics(start_date, end_date)}
        maint_data = {row["tractor"]: row["maintenance_cost"] for row in await self.maintenance_repo.get_maintenance_analytics(start_date, end_date)}
        
        for row in data:
            tractor = row["tractor"]
            row["fuel_cost"] = fuel_data.get(tractor, Decimal("0.0"))
            row["maintenance_cost"] = maint_data.get(tractor, Decimal("0.0"))
            # Profit = Income - (Fuel + Maint + Trip Expense)
            row["profit"] = row["income"] - (row["fuel_cost"] + row["maintenance_cost"] + row["trip_expense"])

        return data

    async def get_driver_performance(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        return await self.fleet_repo.get_driver_performance(start_date, end_date)

    async def get_party_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        return await self.party_repo.get_party_analytics(start_date, end_date)

    async def get_trip_statistics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        return await self.trip_repo.get_trip_statistics(start_date, end_date)

    async def get_dashboard_summary(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        kpis = await self.get_dashboard_kpis(start_date, end_date)
        revenue_chart = await self.get_revenue_chart(start_date, end_date)
        expense_chart = await self.get_expense_chart(start_date, end_date)
        tractor_profitability = await self.get_tractor_profitability(start_date, end_date)
        driver_performance = await self.get_driver_performance(start_date, end_date)
        party_analytics = await self.get_party_analytics(start_date, end_date)

        return {
            "kpis": kpis,
            "revenue_chart": revenue_chart,
            "expense_chart": expense_chart,
            "tractor_profitability": tractor_profitability,
            "driver_performance": driver_performance,
            "party_analytics": party_analytics
        }
