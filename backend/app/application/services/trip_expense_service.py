from datetime import datetime, date
from decimal import Decimal
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.trip_expense import TripExpense
from app.domain.entities.trip import Trip
from app.domain.repositories.trip_expense_repository import TripExpenseRepository
from app.domain.repositories.trip_repository import TripRepository
from app.domain.exceptions.trip import TripNotFoundException
from app.domain.exceptions.trip_expense import (
    TripExpenseNotFoundException,
    TripCompletedException,
    TripCancelledException,
    TripExpenseValidationException,
)
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode
from app.domain.enums.payment_status import PaymentStatus
from app.application.dtos.trip_expense import (
    TripExpenseCreate,
    TripExpenseUpdate,
    TripExpenseResponse,
    TripExpenseSummaryResponse,
    TripDashboardResponse,
    ExpenseBreakdownItem,
)
from app.application.services.expense_number_generator import ExpenseNumberGenerator


class TripExpenseService:
    """
    Orchestrates business processes and constraints mapping Trip Expenses.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: TripExpenseRepository,
        trip_repository: TripRepository,
        number_generator: ExpenseNumberGenerator,
    ) -> None:
        self.session = session
        self.repository = repository
        self.trip_repository = trip_repository
        self.number_generator = number_generator

    async def _validate_trip_state(self, trip_id: uuid.UUID) -> Trip:
        """
        Validates whether a trip exists and is editable (not completed or cancelled).
        """
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException(trip_id)

        if trip.status == TripStatus.CANCELLED:
            raise TripCancelledException(trip_id)
        if trip.status == TripStatus.COMPLETED:
            raise TripCompletedException(trip_id)

        return trip

    async def create_expense(
        self,
        dto: TripExpenseCreate,
        user_id: uuid.UUID,
        client_ip: str | None = None,
    ) -> TripExpense:
        """
        Registers a new operational expense entry for an active trip.
        """
        # Validate trip state first
        await self._validate_trip_state(dto.trip_id)

        # Generate sequence ID
        expense_number = await self.number_generator.generate()

        expense = TripExpense(
            id=uuid.uuid4(),
            expense_number=expense_number,
            trip_id=dto.trip_id,
            party_id=dto.party_id,
            paid_to_name=dto.paid_to_name,
            expense_type=dto.expense_type,
            expense_date=dto.expense_date,
            amount=dto.amount,
            payment_mode=dto.payment_mode,
            payment_status=dto.payment_status,
            reference_number=dto.reference_number,
            remarks=dto.remarks,
            attachment_path=dto.attachment_path,
            attachment_name=dto.attachment_name,
            attachment_size=dto.attachment_size,
            attachment_content_type=dto.attachment_content_type,
            created_by=user_id,
            updated_by=user_id,
            created_ip=client_ip,
            updated_ip=client_ip,
            is_active=True,
        )

        await self.repository.create(expense)
        await self.session.commit()
        return await self.repository.get_by_id(expense.id)

    async def update_expense(
        self,
        expense_id: uuid.UUID,
        dto: TripExpenseUpdate,
        user_id: uuid.UUID,
        client_ip: str | None = None,
    ) -> TripExpense:
        """
        Modifies properties of an existing trip expense.
        """
        expense = await self.repository.get_by_id(expense_id)
        if not expense:
            raise TripExpenseNotFoundException(expense_id)

        # Validate trip state before modifications
        await self._validate_trip_state(expense.trip_id)

        # Apply update properties
        update_data = dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(expense, key, value)

        expense.updated_by = user_id
        expense.updated_ip = client_ip
        expense.updated_at = datetime.now()

        await self.repository.update(expense)
        await self.session.commit()
        return await self.repository.get_by_id(expense.id)

    async def delete_expense(
        self,
        expense_id: uuid.UUID,
        user_id: uuid.UUID,
        client_ip: str | None = None,
    ) -> TripExpense:
        """
        Soft deletes a trip expense entry.
        """
        expense = await self.repository.get_by_id(expense_id)
        if not expense:
            raise TripExpenseNotFoundException(expense_id)

        # Validate trip state before deletion
        await self._validate_trip_state(expense.trip_id)

        expense.deleted_at = datetime.now()
        expense.is_active = False
        expense.updated_by = user_id
        expense.updated_ip = client_ip

        await self.repository.update(expense)
        await self.session.commit()
        await self.session.refresh(expense)
        return expense

    async def get_expense_by_id(self, expense_id: uuid.UUID) -> TripExpense:
        """
        Retrieves a single trip expense by ID.
        """
        expense = await self.repository.get_by_id(expense_id)
        if not expense:
            raise TripExpenseNotFoundException(expense_id)
        return expense

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
        Retrieves paginated, filtered, and sorted lists of Trip Expenses.
        """
        return await self.repository.get_trip_expenses(
            trip_id=trip_id,
            expense_type=expense_type,
            payment_mode=payment_mode,
            paid_to_name=paid_to_name,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_trip_expense_summary(self, trip_id: uuid.UUID) -> TripExpenseSummaryResponse:
        """
        Returns rich operational expenses breakdown for a trip.
        """
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException(trip_id)

        # Get grouped summaries
        grouped = await self.repository.get_expenses_by_type(trip_id)
        
        breakdown = []
        total_expenses = Decimal("0.00")
        expense_count = 0

        for item in grouped:
            breakdown.append(ExpenseBreakdownItem(type=item["type"], amount=item["amount"]))
            total_expenses += item["amount"]
            expense_count += item["count"]

        profit = trip.freight_amount - total_expenses

        return TripExpenseSummaryResponse(
            trip_number=trip.trip_number,
            freight=trip.freight_amount,
            advance=trip.advance_amount,
            expenses=total_expenses,
            profit=profit,
            expense_count=expense_count,
            expense_breakdown=breakdown,
        )

    async def get_trip_profit_details(self, trip_id: uuid.UUID) -> dict[str, Any]:
        """
        Retrieves detailed margins and profit/loss calculations for a trip.
        """
        res = await self.repository.get_trip_profit(trip_id)
        if not res:
            raise TripNotFoundException(trip_id)
        return res

    async def get_trip_dashboard(self, trip_id: uuid.UUID) -> TripDashboardResponse:
        """
        Aggregates contextual data for high-level frontend dashboard rendering.
        """
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException(trip_id)

        # Fetch expenses
        expenses, _ = await self.repository.get_trip_expenses(trip_id=trip_id, limit=1000)
        
        # Calculate sums
        total_expense = sum(e.amount for e in expenses)
        total_advances = trip.advance_amount + sum(e.amount for e in expenses if e.expense_type == ExpenseType.DRIVER_ADVANCE)
        net_profit = trip.freight_amount - total_expense

        # Additional financial metrics
        remaining_freight = trip.freight_amount - trip.advance_amount
        remaining_profit = trip.freight_amount - total_expense - trip.advance_amount

        # Get history timeline
        timeline = await self.repository.get_trip_status_history(trip_id)

        return TripDashboardResponse(
            trip_number=trip.trip_number,
            status=trip.status.value,
            driver_name=trip.driver.name if getattr(trip, "driver", None) else None,
            tractor_number=trip.tractor.tractor_number if getattr(trip, "tractor", None) else None,
            party_name=trip.party.name if getattr(trip, "party", None) else None,
            freight=trip.freight_amount,
            advance=trip.advance_amount,
            remaining_freight=remaining_freight,
            expenses=total_expense,
            profit=net_profit,
            remaining_profit=remaining_profit,
            expense_count=len(expenses),
            expenses_list=[TripExpenseResponse.model_validate(e) for e in expenses],
            timeline=timeline,
        )
