import uuid
from datetime import date
from typing import Any, Tuple

from sqlalchemy import select, or_, func, desc
from sqlalchemy.orm import selectinload

from app.domain.entities.maintenance import Maintenance
from app.domain.entities.maintenance_history import MaintenanceHistory
from app.domain.entities.tractor import Tractor
from app.domain.enums.maintenance_status import MaintenanceStatus
from app.domain.repositories.maintenance_repository import MaintenanceRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyMaintenanceRepository(SQLAlchemyBaseRepository[Maintenance], MaintenanceRepository):
    
    def __init__(self, session):
        super().__init__(session, Maintenance)
        
    async def get_by_id(self, maintenance_id: uuid.UUID) -> Maintenance | None:
        stmt = (
            select(Maintenance)
            .options(selectinload(Maintenance.tractor))
            .where(Maintenance.id == maintenance_id, Maintenance.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_number(self, maintenance_number: str) -> Maintenance | None:
        stmt = (
            select(Maintenance)
            .options(selectinload(Maintenance.tractor))
            .where(Maintenance.maintenance_number == maintenance_number, Maintenance.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active_for_tractor(self, tractor_id: uuid.UUID) -> Maintenance | None:
        stmt = (
            select(Maintenance)
            .where(
                Maintenance.tractor_id == tractor_id,
                Maintenance.status.in_([MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS]),
                Maintenance.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def search(self, filters: dict[str, Any], page: int, size: int) -> Tuple[list[Maintenance], int]:
        stmt = select(Maintenance).options(selectinload(Maintenance.tractor)).where(Maintenance.deleted_at.is_(None))
        count_stmt = select(func.count()).where(Maintenance.deleted_at.is_(None))
        
        # Apply filters
        if search_query := filters.get("search"):
            search_filter = or_(
                Maintenance.maintenance_number.ilike(f"%{search_query}%"),
                Maintenance.vendor_name.ilike(f"%{search_query}%"),
                Maintenance.invoice_number.ilike(f"%{search_query}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)
            
        if tractor_id := filters.get("tractor_id"):
            stmt = stmt.where(Maintenance.tractor_id == tractor_id)
            count_stmt = count_stmt.where(Maintenance.tractor_id == tractor_id)
            
        if status := filters.get("status"):
            stmt = stmt.where(Maintenance.status == status)
            count_stmt = count_stmt.where(Maintenance.status == status)
            
        if priority := filters.get("priority"):
            stmt = stmt.where(Maintenance.priority == priority)
            count_stmt = count_stmt.where(Maintenance.priority == priority)
            
        if maintenance_type := filters.get("maintenance_type"):
            stmt = stmt.where(Maintenance.maintenance_type == maintenance_type)
            count_stmt = count_stmt.where(Maintenance.maintenance_type == maintenance_type)
            
        # Pagination
        stmt = stmt.order_by(desc(Maintenance.created_at)).offset((page - 1) * size).limit(size)
        
        items = (await self.session.execute(stmt)).scalars().all()
        total = (await self.session.execute(count_stmt)).scalar() or 0
        
        return list(items), total

    async def get_dashboard_stats(self) -> dict[str, Any]:
        today = date.today()
        first_day_month = today.replace(day=1)
        first_day_year = today.replace(month=4, day=1) if today.month >= 4 else today.replace(year=today.year-1, month=4, day=1)
        
        # Status counts
        status_stmt = select(Maintenance.status, func.count()).where(Maintenance.deleted_at.is_(None)).group_by(Maintenance.status)
        status_counts = dict((await self.session.execute(status_stmt)).all())
        
        # Costs
        cost_stmt = select(func.sum(Maintenance.total_cost)).where(Maintenance.deleted_at.is_(None), Maintenance.status == MaintenanceStatus.COMPLETED)
        total_cost = (await self.session.execute(cost_stmt)).scalar() or 0
        
        month_cost_stmt = select(func.sum(Maintenance.total_cost)).where(
            Maintenance.deleted_at.is_(None),
            Maintenance.status == MaintenanceStatus.COMPLETED,
            Maintenance.completion_date >= first_day_month
        )
        current_month_cost = (await self.session.execute(month_cost_stmt)).scalar() or 0
        
        year_cost_stmt = select(func.sum(Maintenance.total_cost)).where(
            Maintenance.deleted_at.is_(None),
            Maintenance.status == MaintenanceStatus.COMPLETED,
            Maintenance.completion_date >= first_day_year
        )
        current_year_cost = (await self.session.execute(year_cost_stmt)).scalar() or 0
        
        avg_cost_stmt = select(func.avg(Maintenance.total_cost)).where(
            Maintenance.deleted_at.is_(None),
            Maintenance.status == MaintenanceStatus.COMPLETED
        )
        average_cost = (await self.session.execute(avg_cost_stmt)).scalar() or 0
        
        highest_cost_stmt = select(func.max(Maintenance.total_cost)).where(
            Maintenance.deleted_at.is_(None),
            Maintenance.status == MaintenanceStatus.COMPLETED
        )
        highest_cost_repair = (await self.session.execute(highest_cost_stmt)).scalar()
        
        subq = select(func.sum(Maintenance.total_cost).label("total_cost")).where(
            Maintenance.deleted_at.is_(None),
            Maintenance.status == MaintenanceStatus.COMPLETED
        ).group_by(Maintenance.tractor_id).subquery()
        
        avg_tractor_cost_stmt = select(func.avg(subq.c.total_cost))
        average_cost_by_tractor = (await self.session.execute(avg_tractor_cost_stmt)).scalar()
        
        # Upcoming & Overdue
        upcoming_count_stmt = select(func.count()).where(
            Maintenance.deleted_at.is_(None),
            Maintenance.status == MaintenanceStatus.SCHEDULED,
            Maintenance.scheduled_date >= today
        )
        upcoming_count = (await self.session.execute(upcoming_count_stmt)).scalar() or 0
        
        overdue_count_stmt = select(func.count()).where(
            Maintenance.deleted_at.is_(None),
            Maintenance.status == MaintenanceStatus.SCHEDULED,
            Maintenance.scheduled_date < today
        )
        overdue_count = (await self.session.execute(overdue_count_stmt)).scalar() or 0
        
        # Type & Priority Breakdown
        type_cost_stmt = select(Maintenance.maintenance_type, func.sum(Maintenance.total_cost)).where(
            Maintenance.deleted_at.is_(None), Maintenance.status == MaintenanceStatus.COMPLETED
        ).group_by(Maintenance.maintenance_type)
        cost_by_maintenance_type = dict((await self.session.execute(type_cost_stmt)).all())
        
        priority_stmt = select(Maintenance.priority, func.count()).where(Maintenance.deleted_at.is_(None)).group_by(Maintenance.priority)
        priority_distribution = dict((await self.session.execute(priority_stmt)).all())
        
        # Monthly trend (last 6 months)
        # We simplify the monthly trend here to just use the month string (YYYY-MM) via Postgres to_char
        trend_stmt = select(
            func.to_char(Maintenance.completion_date, 'YYYY-MM').label('month'),
            func.sum(Maintenance.total_cost)
        ).where(
            Maintenance.deleted_at.is_(None),
            Maintenance.status == MaintenanceStatus.COMPLETED,
            Maintenance.completion_date.is_not(None)
        ).group_by(func.to_char(Maintenance.completion_date, 'YYYY-MM')).order_by(desc('month')).limit(6)
        
        trend_results = (await self.session.execute(trend_stmt)).all()
        monthly_trend = [{"month": r[0], "cost": float(r[1])} for r in reversed(trend_results)]
        
        return {
            "scheduled_count": status_counts.get(MaintenanceStatus.SCHEDULED, 0),
            "in_progress_count": status_counts.get(MaintenanceStatus.IN_PROGRESS, 0),
            "completed_count": status_counts.get(MaintenanceStatus.COMPLETED, 0),
            "cancelled_count": status_counts.get(MaintenanceStatus.CANCELLED, 0),
            "total_cost": total_cost,
            "current_month_cost": current_month_cost,
            "current_year_cost": current_year_cost,
            "average_cost": average_cost,
            "upcoming_service_count": upcoming_count,
            "overdue_service_count": overdue_count,
            "highest_cost_repair": highest_cost_repair,
            "average_cost_by_tractor": average_cost_by_tractor,
            "cost_by_maintenance_type": {k.value: float(v) for k, v in cost_by_maintenance_type.items()},
            "priority_distribution": {k.value: v for k, v in priority_distribution.items()},
            "monthly_trend": monthly_trend,
        }

    async def get_upcoming_services(self, limit: int = 10) -> list[Maintenance]:
        today = date.today()
        stmt = (
            select(Maintenance)
            .options(selectinload(Maintenance.tractor))
            .where(
                Maintenance.status == MaintenanceStatus.SCHEDULED,
                Maintenance.scheduled_date >= today,
                Maintenance.deleted_at.is_(None)
            )
            .order_by(Maintenance.scheduled_date.asc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_overdue_services(self, limit: int = 10) -> list[Maintenance]:
        today = date.today()
        stmt = (
            select(Maintenance)
            .options(selectinload(Maintenance.tractor))
            .where(
                Maintenance.status == MaintenanceStatus.SCHEDULED,
                Maintenance.scheduled_date < today,
                Maintenance.deleted_at.is_(None)
            )
            .order_by(Maintenance.scheduled_date.asc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_history(self, maintenance_id: uuid.UUID) -> list[MaintenanceHistory]:
        stmt = (
            select(MaintenanceHistory)
            .options(selectinload(MaintenanceHistory.user))
            .where(MaintenanceHistory.maintenance_id == maintenance_id)
            .order_by(desc(MaintenanceHistory.created_at))
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def save(self, maintenance: Maintenance) -> Maintenance:
        self.session.add(maintenance)
        await self.session.flush()
        return maintenance
