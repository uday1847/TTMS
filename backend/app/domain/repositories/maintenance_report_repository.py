from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class MaintenanceReportRepository(ABC):
    @abstractmethod
    async def get_maintenance_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch maintenance analytics (costs, counts, downtime)."""
        pass
