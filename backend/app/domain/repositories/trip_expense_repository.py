from abc import abstractmethod
from datetime import date
from decimal import Decimal
import uuid
from typing import Any

from app.domain.repositories.base_repository import BaseRepository
from app.domain.entities.trip_expense import TripExpense
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode


class TripExpenseRepository(BaseRepository[TripExpense]):
    """
    Interface defining data-access operations specifically for Trip Expenses.
    """

    @abstractmethod
    async def get_trip_expenses(
        self,
        trip_id: uuid.UUID | None = None,
        expense_type: ExpenseType | None = None,
        payment_mode: PaymentMode | None = None,
        paid_to_name: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "expense_date",
        sort_order: str = "desc",
    ) -> tuple[list[TripExpense], int]:
        """
        Retrieves a filtered, sorted, and paginated list of Trip Expenses along with total count.
        """
        pass

    @abstractmethod
    async def get_monthly_expenses(self, year: int) -> list[dict[str, Any]]:
        """
        Retrieves total expenses grouped by month for a given year.
        """
        pass

    @abstractmethod
    async def get_expenses_by_type(self, trip_id: uuid.UUID | None = None) -> list[dict[str, Any]]:
        """
        Retrieves aggregate expense sums grouped by ExpenseType.
        """
        pass

    @abstractmethod
    async def get_expenses_by_trip(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Retrieves aggregate expense summaries grouped by trip ID.
        """
        pass

    @abstractmethod
    async def get_top_expense_category(self) -> dict[str, Any] | None:
        """
        Retrieves the expense category with the highest total amount.
        """
        pass

    @abstractmethod
    async def get_trip_profit(self, trip_id: uuid.UUID) -> dict[str, Any] | None:
        """
        Retrieves financial aggregates (freight, advances, total expenses, net profit) for a trip.
        """
        pass

    @abstractmethod
    async def get_driver_expense(self, driver_id: uuid.UUID) -> Decimal:
        """
        Retrieves sum of all expenses incurred by a driver.
        """
        pass

    @abstractmethod
    async def get_tractor_expense(self, tractor_id: uuid.UUID) -> Decimal:
        """
        Retrieves sum of all expenses incurred by a tractor.
        """
        pass

    @abstractmethod
    async def get_dashboard_summary(self) -> dict[str, Any]:
        """
        Retrieves global analytical summary metrics for dashboard reporting.
        """
        pass

    @abstractmethod
    async def get_max_sequence_for_year(self, year: int) -> int:
        """
        Retrieves the maximum sequence number used for the specified year.
        """
        pass

    @abstractmethod
    async def get_trip_status_history(self, trip_id: uuid.UUID) -> list[Any]:
        """
        Retrieves status change history for a given trip.
        """
        pass
