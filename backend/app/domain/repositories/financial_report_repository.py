from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class FinancialReportRepository(ABC):
    @abstractmethod
    async def get_expense_breakdown(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch breakdown of expenses by type."""
        pass

    @abstractmethod
    async def get_monthly_profit(self, year: int) -> List[Dict[str, Any]]:
        """Fetch monthly profit analysis for a given year."""
        pass

    @abstractmethod
    async def get_receivables(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch outstanding receivables from invoices."""
        pass

    @abstractmethod
    async def get_collections(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch collections data from invoice payments."""
        pass
