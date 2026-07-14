from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class PartyReportRepository(ABC):
    @abstractmethod
    async def get_party_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Fetch customer (party) revenue and receivables analytics."""
        pass
