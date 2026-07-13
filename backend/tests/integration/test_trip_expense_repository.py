import datetime
from decimal import Decimal
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.domain.entities.trip_expense import TripExpense
from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.entities.user import User
from app.domain.entities.trip_status_history import TripStatusHistory
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.driver_status import DriverStatus
from app.infrastructure.repositories.trip_expense_repository import SQLAlchemyTripExpenseRepository


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db_repo(db_session: AsyncSession):
    # Eager clean up test records
    await db_session.execute(delete(TripExpense))
    await db_session.execute(delete(TripStatusHistory))
    await db_session.execute(delete(Trip))
    await db_session.execute(delete(Driver))
    await db_session.execute(delete(Tractor))
    await db_session.execute(delete(Party))
    await db_session.commit()
    yield
    await db_session.execute(delete(TripExpense))
    await db_session.execute(delete(TripStatusHistory))
    await db_session.execute(delete(Trip))
    await db_session.execute(delete(Driver))
    await db_session.execute(delete(Tractor))
    await db_session.execute(delete(Party))
    await db_session.commit()


@pytest.mark.asyncio
async def test_sqlalchemy_trip_expense_repository_operations(db_session: AsyncSession) -> None:
    # Arrange: Setup assets and trip
    driver = Driver(
        id=uuid.uuid4(),
        employee_code="DRV-EXP-99",
        name="James Bond",
        license_number="DL-EXP-99",
        license_expiry=datetime.date.today() + datetime.timedelta(days=100),
        license_class="HEAVY",
        contact_phone="+919999111222",
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
        is_active=True
    )
    tractor = Tractor(
        id=uuid.uuid4(),
        tractor_number="GJ01-EXP-9999",
        owner_name="Company Fleet",
        rc_number="RC-GJ-EXP-9999",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=100),
        is_active=True
    )
    party = Party(
        id=uuid.uuid4(),
        name="IOCL Pump",
        party_type="Supplier",
        mobile_number="9999888877",
        is_active=True
    )
    trip = Trip(
        id=uuid.uuid4(),
        trip_number="TRIP-2026-999999",
        party_id=party.id,
        tractor_id=tractor.id,
        driver_id=driver.id,
        source_location="Mundra Port",
        destination_location="Surat Refinery",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
        freight_amount=Decimal("50000.00"),
        advance_amount=Decimal("10000.00"),
        status=TripStatus.DISPATCHED,
        is_active=True,
    )
    
    db_session.add(driver)
    db_session.add(tractor)
    db_session.add(party)
    db_session.add(trip)
    await db_session.flush()

    repository = SQLAlchemyTripExpenseRepository(db_session)

    # 1. Create Trip Expenses
    exp1 = TripExpense(
        id=uuid.uuid4(),
        expense_number="EXP-2026-000001",
        trip_id=trip.id,
        party_id=party.id,
        paid_to_name="HP Station",
        expense_type=ExpenseType.DIESEL,
        expense_date=datetime.date.today(),
        amount=Decimal("15000.00"),
        payment_mode=PaymentMode.UPI,
        payment_status=PaymentStatus.PAID,
        is_active=True,
        version_id=1,
    )
    exp2 = TripExpense(
        id=uuid.uuid4(),
        expense_number="EXP-2026-000002",
        trip_id=trip.id,
        expense_type=ExpenseType.TOLL,
        expense_date=datetime.date.today(),
        amount=Decimal("2000.00"),
        payment_mode=PaymentMode.CASH,
        payment_status=PaymentStatus.PAID,
        is_active=True,
        version_id=1,
    )
    
    await repository.create(exp1)
    await repository.create(exp2)
    await db_session.commit()

    # 2. Get by ID
    fetched = await repository.get_by_id(exp1.id)
    assert fetched is not None
    assert fetched.expense_number == "EXP-2026-000001"
    assert fetched.paid_to_name == "HP Station"
    assert fetched.party.name == "IOCL Pump"

    # 3. get_trip_expenses filtering
    expenses, total = await repository.get_trip_expenses(
        trip_id=trip.id,
        expense_type=ExpenseType.DIESEL,
    )
    assert total == 1
    assert expenses[0].expense_number == "EXP-2026-000001"

    # 4. get_expenses_by_type aggregation
    by_type = await repository.get_expenses_by_type(trip.id)
    assert len(by_type) == 2
    assert by_type[0]["type"] == "DIESEL"
    assert by_type[0]["amount"] == Decimal("15000.00")

    # 5. get_top_expense_category
    top = await repository.get_top_expense_category()
    assert top is not None
    assert top["type"] == "DIESEL"

    # 6. get_trip_profit
    profit = await repository.get_trip_profit(trip.id)
    assert profit is not None
    assert profit["freight_amount"] == Decimal("50000.00")
    assert profit["total_expense"] == Decimal("17000.00")
    assert profit["net_profit"] == Decimal("33000.00")

    # 7. get_max_sequence_for_year
    max_seq = await repository.get_max_sequence_for_year(2026)
    assert max_seq == 2

    # 8. get_monthly_expenses
    monthly = await repository.get_monthly_expenses(2026)
    assert len(monthly) == 1
    assert monthly[0]["total_amount"] == Decimal("17000.00")
