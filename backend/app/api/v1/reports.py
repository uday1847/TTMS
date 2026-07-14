import uuid
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Path, status, Response

from app.api.dependencies.db import get_session
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.application.dtos.reports import (
    DashboardKPIResponse,
    DashboardSummaryResponse,
    RevenueChartResponse,
    ExpenseChartResponse,
    FuelAnalyticsResponse,
    MaintenanceAnalyticsResponse,
    TractorProfitabilityResponse,
    DriverPerformanceResponse,
    PartyAnalyticsResponse
)
from app.application.services.report_service import ReportService
from app.application.services.report_export_service import ReportExportService
from app.infrastructure.repositories.dashboard_repository import SQLAlchemyDashboardRepository
from app.infrastructure.repositories.financial_report_repository import SQLAlchemyFinancialReportRepository
from app.infrastructure.repositories.fleet_report_repository import SQLAlchemyFleetReportRepository
from app.infrastructure.repositories.fuel_report_repository import SQLAlchemyFuelReportRepository
from app.infrastructure.repositories.maintenance_report_repository import SQLAlchemyMaintenanceReportRepository
from app.infrastructure.repositories.trip_report_repository import SQLAlchemyTripReportRepository
from app.infrastructure.repositories.party_report_repository import SQLAlchemyPartyReportRepository
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

def get_report_service(session: AsyncSession = Depends(get_session)) -> ReportService:
    return ReportService(
        dashboard_repo=SQLAlchemyDashboardRepository(session),
        financial_repo=SQLAlchemyFinancialReportRepository(session),
        fleet_repo=SQLAlchemyFleetReportRepository(session),
        fuel_repo=SQLAlchemyFuelReportRepository(session),
        maintenance_repo=SQLAlchemyMaintenanceReportRepository(session),
        trip_repo=SQLAlchemyTripReportRepository(session),
        party_repo=SQLAlchemyPartyReportRepository(session)
    )

# --- Dashboard & JSON Endpoints ---

@router.get(
    "/dashboard/kpi",
    response_model=DashboardKPIResponse,
    dependencies=[Depends(PermissionChecker("reports:dashboard"))]
)
async def get_dashboard_kpis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_dashboard_kpis(start_date, end_date)

@router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse,
    dependencies=[Depends(PermissionChecker("reports:dashboard"))]
)
async def get_dashboard_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_dashboard_summary(start_date, end_date)

@router.get(
    "/revenue",
    response_model=List[RevenueChartResponse],
    dependencies=[Depends(PermissionChecker("reports:analytics"))]
)
async def get_revenue_chart(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_revenue_chart(start_date, end_date)

@router.get(
    "/expenses",
    response_model=List[ExpenseChartResponse],
    dependencies=[Depends(PermissionChecker("reports:analytics"))]
)
async def get_expense_chart(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_expense_chart(start_date, end_date)

@router.get(
    "/fuel",
    response_model=List[FuelAnalyticsResponse],
    dependencies=[Depends(PermissionChecker("reports:analytics"))]
)
async def get_fuel_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_fuel_analytics(start_date, end_date)

@router.get(
    "/maintenance",
    response_model=List[MaintenanceAnalyticsResponse],
    dependencies=[Depends(PermissionChecker("reports:analytics"))]
)
async def get_maintenance_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_maintenance_analytics(start_date, end_date)

@router.get(
    "/profitability",
    response_model=List[TractorProfitabilityResponse],
    dependencies=[Depends(PermissionChecker("reports:analytics"))]
)
async def get_tractor_profitability(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_tractor_profitability(start_date, end_date)

@router.get(
    "/drivers",
    response_model=List[DriverPerformanceResponse],
    dependencies=[Depends(PermissionChecker("reports:analytics"))]
)
async def get_driver_performance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_driver_performance(start_date, end_date)

@router.get(
    "/parties",
    response_model=List[PartyAnalyticsResponse],
    dependencies=[Depends(PermissionChecker("reports:analytics"))]
)
async def get_party_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_party_analytics(start_date, end_date)


# --- Export Endpoints ---

def get_media_type(format: str) -> str:
    if format == "csv": return "text/csv"
    if format == "xlsx": return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if format == "pdf": return "application/pdf"
    return "text/plain"

def get_extension(format: str) -> str:
    return format

@router.get(
    "/export/dashboard",
    dependencies=[Depends(PermissionChecker("reports:read"))]
)
async def export_dashboard(
    format: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    data = await service.get_dashboard_kpis(start_date, end_date)
    content = ReportExportService.export_dashboard(data, format)
    
    headers = {
        'Content-Disposition': f'attachment; filename="dashboard_export_{date.today()}.{get_extension(format)}"'
    }
    return Response(content=content, media_type=get_media_type(format), headers=headers)

@router.get(
    "/export/trips",
    dependencies=[Depends(PermissionChecker("reports:read"))]
)
async def export_trips(
    format: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    data = await service.get_trip_statistics(start_date, end_date)
    content = ReportExportService.export_trips(data, format)
    
    headers = {
        'Content-Disposition': f'attachment; filename="trips_export_{date.today()}.{get_extension(format)}"'
    }
    return Response(content=content, media_type=get_media_type(format), headers=headers)

@router.get(
    "/export/fuel",
    dependencies=[Depends(PermissionChecker("reports:read"))]
)
async def export_fuel(
    format: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    data = await service.get_fuel_analytics(start_date, end_date)
    content = ReportExportService.export_fuel(data, format)
    
    headers = {
        'Content-Disposition': f'attachment; filename="fuel_analytics_export_{date.today()}.{get_extension(format)}"'
    }
    return Response(content=content, media_type=get_media_type(format), headers=headers)

@router.get(
    "/export/profitability",
    dependencies=[Depends(PermissionChecker("reports:read"))]
)
async def export_profitability(
    format: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ReportService = Depends(get_report_service)
):
    data = await service.get_tractor_profitability(start_date, end_date)
    # Serialize decimals
    for row in data:
        for k, v in row.items():
            if isinstance(v, Decimal):
                row[k] = float(v)
                
    content = ReportExportService.export_profitability(data, format)
    
    headers = {
        'Content-Disposition': f'attachment; filename="tractor_profitability_export_{date.today()}.{get_extension(format)}"'
    }
    return Response(content=content, media_type=get_media_type(format), headers=headers)
