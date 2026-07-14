from decimal import Decimal
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class DashboardKPIResponse(BaseModel):
    total_trips: int = 0
    completed_trips: int = 0
    cancelled_trips: int = 0
    running_trips: int = 0
    
    total_income: Decimal = Decimal("0.0")
    total_expenses: Decimal = Decimal("0.0")
    gross_profit: Decimal = Decimal("0.0")
    net_profit: Decimal = Decimal("0.0")
    profit_margin: Decimal = Decimal("0.0")
    
    outstanding_receivables: Decimal = Decimal("0.0")
    received_payments: Decimal = Decimal("0.0")
    
    fleet_utilization: float = 0.0
    active_drivers: int = 0
    active_tractors: int = 0

    model_config = ConfigDict(from_attributes=True)


class RevenueChartResponse(BaseModel):
    month: str
    revenue: Decimal = Decimal("0.0")
    expenses: Decimal = Decimal("0.0")
    profit: Decimal = Decimal("0.0")

    model_config = ConfigDict(from_attributes=True)


class ExpenseChartResponse(BaseModel):
    expense_type: str
    amount: Decimal = Decimal("0.0")
    percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class FuelAnalyticsResponse(BaseModel):
    tractor: str
    total_liters: Decimal = Decimal("0.0")
    average_kmpl: Decimal = Decimal("0.0")
    cost_per_km: Decimal = Decimal("0.0")
    fuel_cost: Decimal = Decimal("0.0")
    suspicious_transactions: int = 0

    model_config = ConfigDict(from_attributes=True)


class MaintenanceAnalyticsResponse(BaseModel):
    tractor: str
    maintenance_count: int = 0
    maintenance_cost: Decimal = Decimal("0.0")
    downtime_days: int = 0
    next_service: Optional[date] = None
    overdue: bool = False

    model_config = ConfigDict(from_attributes=True)


class TractorProfitabilityResponse(BaseModel):
    tractor: str
    trip_count: int = 0
    income: Decimal = Decimal("0.0")
    fuel_cost: Decimal = Decimal("0.0")
    maintenance_cost: Decimal = Decimal("0.0")
    trip_expense: Decimal = Decimal("0.0")
    profit: Decimal = Decimal("0.0")

    model_config = ConfigDict(from_attributes=True)


class DriverPerformanceResponse(BaseModel):
    driver: str
    trip_count: int = 0
    average_kmpl: Decimal = Decimal("0.0")
    revenue: Decimal = Decimal("0.0")
    profit: Decimal = Decimal("0.0")
    on_time_delivery: float = 0.0
    fuel_efficiency: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class PartyAnalyticsResponse(BaseModel):
    party: str
    trip_count: int = 0
    revenue: Decimal = Decimal("0.0")
    pending_invoice: Decimal = Decimal("0.0")
    received_payment: Decimal = Decimal("0.0")
    outstanding: Decimal = Decimal("0.0")

    model_config = ConfigDict(from_attributes=True)


class DashboardSummaryResponse(BaseModel):
    kpis: DashboardKPIResponse
    revenue_chart: List[RevenueChartResponse] = []
    expense_chart: List[ExpenseChartResponse] = []
    tractor_profitability: List[TractorProfitabilityResponse] = []
    driver_performance: List[DriverPerformanceResponse] = []
    party_analytics: List[PartyAnalyticsResponse] = []

    model_config = ConfigDict(from_attributes=True)
