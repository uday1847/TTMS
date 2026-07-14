from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class FleetReportRepository(ABC):
    @abstractmethod
    async def get_fleet_utilization(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch fleet utilization metrics."""
        pass

    @abstractmethod
    async def get_driver_performance(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch driver performance stats (trips, kmpl, revenue)."""
        pass

    @abstractmethod
    async def get_tractor_profitability(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch profitability metrics per tractor."""
        pass
