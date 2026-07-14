from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.dashboard_repository import DashboardRepository
from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_payment import InvoicePayment
from app.domain.entities.trip_expense import TripExpense


class SQLAlchemyDashboardRepository(DashboardRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_kpis(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        # Base filter for date ranges where applicable
        
        # Trip metrics
        stmt_trips = select(
            func.count(Trip.id).label("total_trips"),
            func.sum(case((Trip.status == 'COMPLETED', 1), else_=0)).label("completed_trips"),
            func.sum(case((Trip.status == 'CANCELLED', 1), else_=0)).label("cancelled_trips"),
            func.sum(case((Trip.status.notin_(['COMPLETED', 'CANCELLED']), 1), else_=0)).label("running_trips")
        ).where(Trip.deleted_at.is_(None))
        
        if start_date:
            stmt_trips = stmt_trips.where(Trip.trip_date >= start_date)
        if end_date:
            stmt_trips = stmt_trips.where(Trip.trip_date <= end_date)
            
        # Execute queries individually or concurrently
        # For simplicity, sequential await is fine for now, we can optimize with asyncio.gather
        
        trip_res = (await self.session.execute(stmt_trips)).fetchone()
        
        # Financial metrics (Income from trips or invoices)
        stmt_income = select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(Invoice.deleted_at.is_(None))
        if start_date: stmt_income = stmt_income.where(Invoice.invoice_date >= start_date)
        if end_date: stmt_income = stmt_income.where(Invoice.invoice_date <= end_date)
        total_income = (await self.session.execute(stmt_income)).scalar_one()

        stmt_expense = select(func.coalesce(func.sum(TripExpense.amount), 0)).where(TripExpense.deleted_at.is_(None))
        if start_date: stmt_expense = stmt_expense.where(TripExpense.expense_date >= start_date)
        if end_date: stmt_expense = stmt_expense.where(TripExpense.expense_date <= end_date)
        total_expense = (await self.session.execute(stmt_expense)).scalar_one()

        stmt_outstanding = select(func.coalesce(func.sum(Invoice.balance_amount), 0)).where(Invoice.deleted_at.is_(None))
        outstanding = (await self.session.execute(stmt_outstanding)).scalar_one()
        
        stmt_received = select(func.coalesce(func.sum(InvoicePayment.amount), 0)).where(InvoicePayment.deleted_at.is_(None))
        if start_date: stmt_received = stmt_received.where(InvoicePayment.payment_date >= start_date)
        if end_date: stmt_received = stmt_received.where(InvoicePayment.payment_date <= end_date)
        received = (await self.session.execute(stmt_received)).scalar_one()
        
        # Fleet active
        stmt_drivers = select(func.count(Driver.id)).where(Driver.is_active == True, Driver.deleted_at.is_(None))
        active_drivers = (await self.session.execute(stmt_drivers)).scalar_one()
        
        stmt_tractors = select(func.count(Tractor.id)).where(Tractor.is_active == True, Tractor.deleted_at.is_(None))
        active_tractors = (await self.session.execute(stmt_tractors)).scalar_one()
        
        # Gross profit = income - expense. Net profit will be handled by service
        gross_profit = total_income - total_expense
        profit_margin = 0
        if total_income > 0:
            profit_margin = (gross_profit / total_income) * 100

        return {
            "total_trips": int(trip_res.total_trips) if trip_res.total_trips else 0,
            "completed_trips": int(trip_res.completed_trips) if trip_res.completed_trips else 0,
            "cancelled_trips": int(trip_res.cancelled_trips) if trip_res.cancelled_trips else 0,
            "running_trips": int(trip_res.running_trips) if trip_res.running_trips else 0,
            "total_income": total_income,
            "total_expenses": total_expense,
            "gross_profit": gross_profit,
            "net_profit": gross_profit, # Placeholder, Service will refine
            "profit_margin": profit_margin,
            "outstanding_receivables": outstanding,
            "received_payments": received,
            "fleet_utilization": 0.0, # Placeholder
            "active_drivers": active_drivers,
            "active_tractors": active_tractors
        }

    async def get_revenue_chart(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        # This will group revenue and expenses by month
        # Since PostgreSQL is used, we can use date_trunc('month', date)
        
        stmt_rev = select(
            func.to_char(Invoice.invoice_date, 'YYYY-MM').label('month'),
            func.sum(Invoice.total_amount).label('revenue')
        ).where(Invoice.deleted_at.is_(None))
        
        if start_date: stmt_rev = stmt_rev.where(Invoice.invoice_date >= start_date)
        if end_date: stmt_rev = stmt_rev.where(Invoice.invoice_date <= end_date)
            
        stmt_rev = stmt_rev.group_by('month').order_by('month')
        
        stmt_exp = select(
            func.to_char(TripExpense.expense_date, 'YYYY-MM').label('month'),
            func.sum(TripExpense.amount).label('expenses')
        ).where(TripExpense.deleted_at.is_(None))
        
        if start_date: stmt_exp = stmt_exp.where(TripExpense.expense_date >= start_date)
        if end_date: stmt_exp = stmt_exp.where(TripExpense.expense_date <= end_date)
            
        stmt_exp = stmt_exp.group_by('month').order_by('month')
        
        rev_rows = (await self.session.execute(stmt_rev)).fetchall()
        exp_rows = (await self.session.execute(stmt_exp)).fetchall()
        
        # Merge them (Can also be done via FULL OUTER JOIN CTE in SQL, but merging in python for small sets is fast)
        data_map = {}
        for r in rev_rows:
            data_map[r.month] = {"month": r.month, "revenue": r.revenue, "expenses": 0, "profit": r.revenue}
            
        for e in exp_rows:
            if e.month not in data_map:
                data_map[e.month] = {"month": e.month, "revenue": 0, "expenses": e.expenses, "profit": -e.expenses}
            else:
                data_map[e.month]["expenses"] = e.expenses
                data_map[e.month]["profit"] = data_map[e.month]["revenue"] - e.expenses
                
        return sorted(list(data_map.values()), key=lambda x: x["month"])
