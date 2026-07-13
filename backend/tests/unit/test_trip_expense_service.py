import datetime
from decimal import Decimal
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.trip_expense_service import TripExpenseService
from app.application.services.expense_number_generator import ExpenseNumberGenerator
from app.domain.entities.trip_expense import TripExpense
from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode
from app.domain.enums.payment_status import PaymentStatus
from app.domain.exceptions.trip import TripNotFoundException
from app.domain.exceptions.trip_expense import (
    TripExpenseNotFoundException,
    TripCompletedException,
    TripCancelledException,
)
from app.application.dtos.trip_expense import TripExpenseCreate, TripExpenseUpdate


@pytest.fixture
def mock_repo() -> MagicMock:
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_trip_expenses = AsyncMock()
    repo.get_expenses_by_type = AsyncMock()
    repo.get_trip_profit = AsyncMock()
    repo.get_trip_status_history = AsyncMock()
    return repo


@pytest.fixture
def mock_trip_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_generator() -> MagicMock:
    generator = MagicMock(spec=ExpenseNumberGenerator)
    generator.generate = AsyncMock(return_value="EXP-2026-000001")
    return generator


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def service(mock_session: MagicMock, mock_repo: MagicMock, mock_trip_repo: MagicMock, mock_generator: MagicMock) -> TripExpenseService:
    return TripExpenseService(mock_session, mock_repo, mock_trip_repo, mock_generator)


@pytest.mark.asyncio
async def test_create_expense_success(
    service: TripExpenseService,
    mock_repo: MagicMock,
    mock_trip_repo: MagicMock,
    mock_generator: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    user_id = uuid.uuid4()
    trip = Trip(id=trip_id, status=TripStatus.PENDING, freight_amount=Decimal("30000.00"), advance_amount=Decimal("5000.00"))
    mock_trip_repo.get_by_id.return_value = trip

    dto = TripExpenseCreate(
        trip_id=trip_id,
        party_id=uuid.uuid4(),
        paid_to_name="HP Pump",
        expense_type=ExpenseType.DIESEL,
        expense_date=datetime.date.today(),
        amount=Decimal("8000.00"),
        payment_mode=PaymentMode.UPI,
        payment_status=PaymentStatus.PAID,
        reference_number="TXN123",
        remarks="Test diesel",
    )

    mock_repo.create.side_effect = lambda x: x
    mock_repo.get_by_id.side_effect = lambda x: mock_repo.create.call_args[0][0]

    # Act
    expense = await service.create_expense(dto, user_id, "127.0.0.1")

    # Assert
    assert expense.expense_number == "EXP-2026-000001"
    assert expense.trip_id == trip_id
    assert expense.amount == Decimal("8000.00")
    assert expense.created_by == user_id
    assert expense.created_ip == "127.0.0.1"
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_expense_trip_not_found(
    service: TripExpenseService,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    mock_trip_repo.get_by_id.return_value = None

    dto = TripExpenseCreate(
        trip_id=trip_id,
        expense_type=ExpenseType.TOLL,
        expense_date=datetime.date.today(),
        amount=Decimal("120.00"),
        payment_mode=PaymentMode.CASH,
        payment_status=PaymentStatus.PAID,
    )

    # Act & Assert
    with pytest.raises(TripNotFoundException):
        await service.create_expense(dto, uuid.uuid4())


@pytest.mark.asyncio
async def test_create_expense_trip_cancelled(
    service: TripExpenseService,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    trip = Trip(id=trip_id, status=TripStatus.CANCELLED)
    mock_trip_repo.get_by_id.return_value = trip

    dto = TripExpenseCreate(
        trip_id=trip_id,
        expense_type=ExpenseType.TOLL,
        expense_date=datetime.date.today(),
        amount=Decimal("120.00"),
        payment_mode=PaymentMode.CASH,
        payment_status=PaymentStatus.PAID,
    )

    # Act & Assert
    with pytest.raises(TripCancelledException):
        await service.create_expense(dto, uuid.uuid4())


@pytest.mark.asyncio
async def test_create_expense_trip_completed(
    service: TripExpenseService,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    trip = Trip(id=trip_id, status=TripStatus.COMPLETED)
    mock_trip_repo.get_by_id.return_value = trip

    dto = TripExpenseCreate(
        trip_id=trip_id,
        expense_type=ExpenseType.TOLL,
        expense_date=datetime.date.today(),
        amount=Decimal("120.00"),
        payment_mode=PaymentMode.CASH,
        payment_status=PaymentStatus.PAID,
    )

    # Act & Assert
    with pytest.raises(TripCompletedException):
        await service.create_expense(dto, uuid.uuid4())


@pytest.mark.asyncio
async def test_update_expense_success(
    service: TripExpenseService,
    mock_repo: MagicMock,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    expense_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    expense = TripExpense(id=expense_id, trip_id=trip_id, amount=Decimal("100.00"), is_active=True)
    trip = Trip(id=trip_id, status=TripStatus.PENDING)
    
    mock_repo.get_by_id.return_value = expense
    mock_trip_repo.get_by_id.return_value = trip
    mock_repo.update.side_effect = lambda x: x

    dto = TripExpenseUpdate(amount=Decimal("150.00"), remarks="Updated Toll amount")

    # Act
    updated = await service.update_expense(expense_id, dto, uuid.uuid4(), "10.0.0.1")

    # Assert
    assert updated.amount == Decimal("150.00")
    assert updated.remarks == "Updated Toll amount"
    assert updated.updated_ip == "10.0.0.1"


@pytest.mark.asyncio
async def test_update_expense_not_found(
    service: TripExpenseService,
    mock_repo: MagicMock,
) -> None:
    # Arrange
    expense_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = None

    dto = TripExpenseUpdate(amount=Decimal("150.00"))

    # Act & Assert
    with pytest.raises(TripExpenseNotFoundException):
        await service.update_expense(expense_id, dto, uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_expense_success(
    service: TripExpenseService,
    mock_repo: MagicMock,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    expense_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    expense = TripExpense(id=expense_id, trip_id=trip_id, amount=Decimal("100.00"), is_active=True)
    trip = Trip(id=trip_id, status=TripStatus.PENDING)
    
    mock_repo.get_by_id.return_value = expense
    mock_trip_repo.get_by_id.return_value = trip
    mock_repo.update.side_effect = lambda x: x

    # Act
    deleted = await service.delete_expense(expense_id, uuid.uuid4())

    # Assert
    assert deleted.is_active is False
    assert deleted.deleted_at is not None


@pytest.mark.asyncio
async def test_get_trip_expense_summary(
    service: TripExpenseService,
    mock_repo: MagicMock,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    trip = Trip(id=trip_id, trip_number="TRIP-2026-000001", freight_amount=Decimal("50000.00"), advance_amount=Decimal("10000.00"))
    mock_trip_repo.get_by_id.return_value = trip

    mock_repo.get_expenses_by_type.return_value = [
        {"type": ExpenseType.DIESEL, "amount": Decimal("15000.00"), "count": 1},
        {"type": ExpenseType.TOLL, "amount": Decimal("2000.00"), "count": 2},
    ]

    # Act
    summary = await service.get_trip_expense_summary(trip_id)

    # Assert
    assert summary.trip_number == "TRIP-2026-000001"
    assert summary.freight == Decimal("50000.00")
    assert summary.advance == Decimal("10000.00")
    assert summary.expenses == Decimal("17000.00")
    assert summary.profit == Decimal("33000.00")
    assert summary.expense_count == 3
    assert len(summary.expense_breakdown) == 2


@pytest.mark.asyncio
async def test_get_trip_dashboard(
    service: TripExpenseService,
    mock_repo: MagicMock,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    driver = Driver(name="Driver A")
    tractor = Tractor(tractor_number="TRC-123")
    party = Party(name="Party A")
    
    trip = Trip(
        id=trip_id,
        trip_number="TRIP-2026-000001",
        status=TripStatus.DISPATCHED,
        freight_amount=Decimal("50000.00"),
        advance_amount=Decimal("10000.00"),
        driver=driver,
        tractor=tractor,
        party=party,
    )
    mock_trip_repo.get_by_id.return_value = trip

    expenses = [
        TripExpense(id=uuid.uuid4(), trip_id=trip_id, expense_number="EXP-001", amount=Decimal("15000.00"), expense_type=ExpenseType.DIESEL, is_active=True, deleted_at=None, expense_date=datetime.date.today(), payment_mode=PaymentMode.UPI, payment_status=PaymentStatus.PAID, version_id=1),
        TripExpense(id=uuid.uuid4(), trip_id=trip_id, expense_number="EXP-002", amount=Decimal("3000.00"), expense_type=ExpenseType.DRIVER_ADVANCE, is_active=True, deleted_at=None, expense_date=datetime.date.today(), payment_mode=PaymentMode.CASH, payment_status=PaymentStatus.PAID, version_id=1),
    ]
    mock_repo.get_trip_expenses.return_value = (expenses, 2)
    mock_repo.get_trip_status_history.return_value = []

    # Act
    dashboard = await service.get_trip_dashboard(trip_id)

    # Assert
    assert dashboard.trip_number == "TRIP-2026-000001"
    assert dashboard.status == "DISPATCHED"
    assert dashboard.driver_name == "Driver A"
    assert dashboard.tractor_number == "TRC-123"
    assert dashboard.party_name == "Party A"
    assert dashboard.freight == Decimal("50000.00")
    assert dashboard.advance == Decimal("10000.00")
    assert dashboard.remaining_freight == Decimal("40000.00")
    assert dashboard.expenses == Decimal("18000.00")
    assert dashboard.profit == Decimal("32000.00")
    assert dashboard.remaining_profit == Decimal("22000.00")
    assert dashboard.expense_count == 2
    assert len(dashboard.expenses_list) == 2
