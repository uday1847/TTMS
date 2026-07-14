from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class TripReportRepository(ABC):
    @abstractmethod
    async def get_trip_statistics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch trip execution statistics."""
        pass
