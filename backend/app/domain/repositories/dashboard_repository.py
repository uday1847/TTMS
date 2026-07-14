from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class DashboardRepository(ABC):
    @abstractmethod
    async def get_kpis(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """Fetch overall dashboard KPIs."""
        pass

    @abstractmethod
    async def get_revenue_chart(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch revenue vs expense chart data."""
        pass
