from decimal import Decimal
import datetime
import pytest
import pytest_asyncio
import uuid

from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.entities.user import User
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.driver_status import DriverStatus
from app.infrastructure.repositories.trip_repository import SQLAlchemyTripRepository


@pytest.fixture
def repository(db_session) -> SQLAlchemyTripRepository:
    return SQLAlchemyTripRepository(db_session)


@pytest_asyncio.fixture
async def setup_data(db_session):
    # Ensure active user
    user = User(
        id=uuid.uuid4(),
        email=f"integration-{uuid.uuid4().hex[:6]}@example.com",
        username=f"tester-{uuid.uuid4().hex[:6]}",
        password_hash="hash",
        first_name="Test",
        last_name="Tester",
        is_active=True
    )
    db_session.add(user)

    # Add 2 drivers, 2 tractors, 2 parties
    driver1 = Driver(
        id=uuid.uuid4(),
        employee_code=f"EMP-{uuid.uuid4().hex[:6]}",
        name="Driver One",
        license_number=f"LIC-{uuid.uuid4().hex[:6]}",
        license_expiry=datetime.date.today() + datetime.timedelta(days=365),
        license_class="MC",
        contact_phone=f"+91{uuid.uuid4().hex[:8]}",
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
        is_active=True,
    )
    driver2 = Driver(
        id=uuid.uuid4(),
        employee_code=f"EMP-{uuid.uuid4().hex[:6]}",
        name="Driver Two",
        license_number=f"LIC-{uuid.uuid4().hex[:6]}",
        license_expiry=datetime.date.today() + datetime.timedelta(days=365),
        license_class="MC",
        contact_phone=f"+91{uuid.uuid4().hex[:8]}",
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
        is_active=True,
    )
    db_session.add(driver1)
    db_session.add(driver2)

    tractor1 = Tractor(
        id=uuid.uuid4(),
        tractor_number=f"GJ01-TR-{uuid.uuid4().hex[:4].upper()}",
        owner_name="Company Owner",
        rc_number=f"RC-{uuid.uuid4().hex[:6].upper()}",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=365),
        is_active=True,
    )
    tractor2 = Tractor(
        id=uuid.uuid4(),
        tractor_number=f"GJ01-TR-{uuid.uuid4().hex[:4].upper()}",
        owner_name="Company Owner",
        rc_number=f"RC-{uuid.uuid4().hex[:6].upper()}",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=365),
        is_active=True,
    )
    db_session.add(tractor1)
    db_session.add(tractor2)

    party1 = Party(
        id=uuid.uuid4(),
        name="Reliance Industries",
        party_type="Customer",
        mobile_number=f"9900{uuid.uuid4().hex[:6]}",
        is_active=True,
    )
    party2 = Party(
        id=uuid.uuid4(),
        name="Adani Enterprises",
        party_type="Customer",
        mobile_number=f"9900{uuid.uuid4().hex[:6]}",
        is_active=True,
    )
    db_session.add(party1)
    db_session.add(party2)

    await db_session.flush()

    return {
        "user": user,
        "driver1": driver1,
        "driver2": driver2,
        "tractor1": tractor1,
        "tractor2": tractor2,
        "party1": party1,
        "party2": party2,
    }


@pytest.mark.asyncio
async def test_repository_get_max_sequence_and_active_lookups(
    db_session,
    repository: SQLAlchemyTripRepository,
    setup_data,
) -> None:
    data = setup_data
    year = datetime.date.today().year

    # 1. Initially sequence for current year is 0
    seq = await repository.get_max_sequence_for_year(year)
    assert seq == 0

    # 2. Add trip
    trip1 = Trip(
        id=uuid.uuid4(),
        trip_number=f"TRIP-{year}-000001",
        party_id=data["party1"].id,
        tractor_id=data["tractor1"].id,
        driver_id=data["driver1"].id,
        source_location="Mundra Port",
        destination_location="Ahmedabad Site",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
        freight_amount=Decimal("35000.00"),
        advance_amount=Decimal("10000.00"),
        status=TripStatus.DISPATCHED,
        created_by=data["user"].id,
        updated_by=data["user"].id
    )
    db_session.add(trip1)
    await db_session.flush()
    # Set current active trip locks on driver and tractor after trip is persisted
    data["driver1"].current_trip_id = trip1.id
    data["tractor1"].current_trip_id = trip1.id
    await db_session.flush()

    seq = await repository.get_max_sequence_for_year(year)
    assert seq == 1

    # 3. Lookups
    active_drv = await repository.get_active_trip_by_driver(data["driver1"].id)
    assert active_drv is not None
    assert active_drv.trip_number == f"TRIP-{year}-000001"

    active_trc = await repository.get_active_trip_by_tractor(data["tractor1"].id)
    assert active_trc is not None

    active_drv_none = await repository.get_active_trip_by_driver(data["driver2"].id)
    assert active_drv_none is None


@pytest.mark.asyncio
async def test_repository_get_trips_searching_filtering_sorting(
    db_session,
    repository: SQLAlchemyTripRepository,
    setup_data,
) -> None:
    data = setup_data
    year = datetime.date.today().year

    trip1 = Trip(
        id=uuid.uuid4(),
        trip_number=f"TRIP-{year}-000001",
        party_id=data["party1"].id,
        tractor_id=data["tractor1"].id,
        driver_id=data["driver1"].id,
        source_location="Mundra Port",
        destination_location="Ahmedabad Site",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=1),
        freight_amount=Decimal("30000.00"),
        advance_amount=Decimal("5000.00"),
        status=TripStatus.DISPATCHED,
        created_by=data["user"].id,
        updated_by=data["user"].id
    )
    trip2 = Trip(
        id=uuid.uuid4(),
        trip_number=f"TRIP-{year}-000002",
        party_id=data["party2"].id,
        tractor_id=data["tractor2"].id,
        driver_id=data["driver2"].id,
        source_location="Pipavav Port",
        destination_location="Surat Site",
        trip_date=datetime.date.today() + datetime.timedelta(days=1),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=3),
        freight_amount=Decimal("45000.00"),
        advance_amount=Decimal("15000.00"),
        status=TripStatus.PENDING,
        created_by=data["user"].id,
        updated_by=data["user"].id
    )
    db_session.add(trip1)
    db_session.add(trip2)
    await db_session.flush()

    # 1. Search by location
    items, total = await repository.get_trips(page=1, size=10, search_query="Mundra")
    assert total == 1
    assert items[0].trip_number == f"TRIP-{year}-000001"

    # 2. Filter by status
    items, total = await repository.get_trips(page=1, size=10, status_filter="PENDING")
    assert total == 1
    assert items[0].trip_number == f"TRIP-{year}-000002"

    # 3. Sort by freight
    items, total = await repository.get_trips(page=1, size=10, sort_by="freight_amount", order="asc")
    assert total == 2
    assert items[0].freight_amount == Decimal("30000.00")
    assert items[1].freight_amount == Decimal("45000.00")


@pytest.mark.asyncio
async def test_repository_counts_and_dashboard_metrics(
    db_session,
    repository: SQLAlchemyTripRepository,
    setup_data,
) -> None:
    data = setup_data
    year = datetime.date.today().year

    trip1 = Trip(
        id=uuid.uuid4(),
        trip_number=f"TRIP-{year}-000001",
        party_id=data["party1"].id,
        tractor_id=data["tractor1"].id,
        driver_id=data["driver1"].id,
        source_location="Mundra",
        destination_location="Ahmedabad",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=1),
        freight_amount=Decimal("10000.00"),
        advance_amount=Decimal("0.00"),
        status=TripStatus.DISPATCHED,
        created_by=data["user"].id,
        updated_by=data["user"].id
    )
    trip2 = Trip(
        id=uuid.uuid4(),
        trip_number=f"TRIP-{year}-000002",
        party_id=data["party2"].id,
        tractor_id=data["tractor2"].id,
        driver_id=data["driver2"].id,
        source_location="Pipavav",
        destination_location="Surat",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=1),
        freight_amount=Decimal("20000.00"),
        advance_amount=Decimal("0.00"),
        status=TripStatus.COMPLETED,
        actual_delivery_date=datetime.date.today(),
        created_by=data["user"].id,
        updated_by=data["user"].id
    )
    db_session.add(trip1)
    db_session.add(trip2)
    await db_session.flush()

    # 1. State counts
    cnt_active = await repository.count_active_trips()
    assert cnt_active == 1  # only DISPATCHED is active, COMPLETED is not active

    cnt_completed = await repository.count_completed_today()
    assert cnt_completed == 1

    cnt_pending = await repository.count_pending()
    assert cnt_pending == 0

    # 2. Revenue calculation
    rev = await repository.get_revenue_by_date_range(
        datetime.date.today() - datetime.timedelta(days=1),
        datetime.date.today() + datetime.timedelta(days=1)
    )
    assert rev == 30000.00
