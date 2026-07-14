from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.financial_report_repository import FinancialReportRepository
from app.domain.entities.trip_expense import TripExpense
from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_payment import InvoicePayment


class SQLAlchemyFinancialReportRepository(FinancialReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_expense_breakdown(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        stmt = select(
            TripExpense.expense_type,
            func.sum(TripExpense.amount).label("amount")
        ).where(TripExpense.deleted_at.is_(None))
        
        if start_date:
            stmt = stmt.where(TripExpense.expense_date >= start_date)
        if end_date:
            stmt = stmt.where(TripExpense.expense_date <= end_date)
            
        stmt = stmt.group_by(TripExpense.expense_type).order_by(func.sum(TripExpense.amount).desc())
        
        result = await self.session.execute(stmt)
        rows = result.fetchall()
        
        total_expense = sum(row.amount for row in rows) if rows else 1 # avoid div by zero
        
        res = []
        for row in rows:
            res.append({
                "expense_type": row.expense_type.value,
                "amount": row.amount,
                "percentage": float((row.amount / total_expense) * 100) if total_expense else 0
            })
        return res

    async def get_monthly_profit(self, year: int) -> List[Dict[str, Any]]:
        # Simplified similar to revenue chart but filtered by year
        return [] # We can leverage the dashboard logic or leave as a stub for specialized views

    async def get_receivables(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        stmt = select(
            Invoice.id,
            Invoice.invoice_number,
            Invoice.invoice_date,
            Invoice.total_amount,
            Invoice.balance_amount
        ).where(Invoice.balance_amount > 0, Invoice.deleted_at.is_(None))
        
        if start_date: stmt = stmt.where(Invoice.invoice_date >= start_date)
        if end_date: stmt = stmt.where(Invoice.invoice_date <= end_date)
        
        result = await self.session.execute(stmt)
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_collections(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        stmt = select(
            InvoicePayment.id,
            InvoicePayment.payment_date,
            InvoicePayment.amount,
            InvoicePayment.payment_mode
        ).where(InvoicePayment.deleted_at.is_(None))
        
        if start_date: stmt = stmt.where(InvoicePayment.payment_date >= start_date)
        if end_date: stmt = stmt.where(InvoicePayment.payment_date <= end_date)
        
        result = await self.session.execute(stmt)
        return [dict(row._mapping) for row in result.fetchall()]
