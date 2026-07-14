from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class FuelReportRepository(ABC):
    @abstractmethod
    async def get_fuel_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch analytics around fuel consumption and suspicious transactions."""
        pass
