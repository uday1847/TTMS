from decimal import Decimal
import datetime
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.trip import TripCreate, TripUpdate
from app.application.services.trip_service import TripService
from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.entities.trip_status_history import TripStatusHistory
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.driver_status import DriverStatus
from app.domain.exceptions.trip import (
    TripNotFoundException,
    TripStatusException,
    DriverBusyException,
    TractorBusyException,
    TripDeleteException,
    InactiveDriverException,
    InactiveTractorException,
    InactivePartyException,
    AdvanceAmountException,
    TripAlreadyCompletedException,
)
from app.domain.repositories.trip_repository import TripRepository


@pytest.fixture
def mock_session() -> AsyncSession:
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_repository() -> TripRepository:
    repo = AsyncMock(spec=TripRepository)
    return repo


@pytest.fixture
def trip_service(mock_session: AsyncSession, mock_repository: TripRepository) -> TripService:
    return TripService(session=mock_session, repository=mock_repository)


@pytest.mark.asyncio
async def test_create_trip_success(
    trip_service: TripService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    party_id = uuid.uuid4()
    tractor_id = uuid.uuid4()
    driver_id = uuid.uuid4()

    mock_party = Party(id=party_id, is_active=True, name="Test Party")
    mock_tractor = Tractor(id=tractor_id, is_active=True, current_trip_id=None)
    mock_driver = Driver(id=driver_id, is_active=True, current_trip_id=None, current_status=DriverStatus.AVAILABLE)

    mock_session.get.side_effect = lambda entity, ident: {
        Party: mock_party,
        Tractor: mock_tractor,
        Driver: mock_driver
    }.get(entity)

    mock_repository.get_max_sequence_for_year.return_value = 5

    dto = TripCreate(
        party_id=party_id,
        tractor_id=tractor_id,
        driver_id=driver_id,
        source_location="Mines A",
        destination_location="Site B",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
        freight_amount=Decimal("15000.00"),
        advance_amount=Decimal("2000.00"),
        remarks="Initiate test trip.",
    )

    # Act
    result = await trip_service.create_trip(dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.trip_number == f"TRIP-{datetime.date.today().year}-000006"
    assert result.status == TripStatus.PENDING
    assert mock_driver.current_trip_id == result.id
    assert mock_tractor.current_trip_id == result.id
    mock_repository.create.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_trip_inactive_driver_raises_exception(
    trip_service: TripService,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    party_id = uuid.uuid4()
    tractor_id = uuid.uuid4()
    driver_id = uuid.uuid4()

    mock_party = Party(id=party_id, is_active=True)
    mock_tractor = Tractor(id=tractor_id, is_active=True, current_trip_id=None)
    mock_driver = Driver(id=driver_id, is_active=False)

    mock_session.get.side_effect = lambda entity, ident: {
        Party: mock_party,
        Tractor: mock_tractor,
        Driver: mock_driver
    }.get(entity)

    dto = TripCreate(
        party_id=party_id,
        tractor_id=tractor_id,
        driver_id=driver_id,
        source_location="Mines A",
        destination_location="Site B",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
        freight_amount=Decimal("15000.00"),
        advance_amount=Decimal("2000.00"),
    )

    # Act & Assert
    with pytest.raises(InactiveDriverException):
        await trip_service.create_trip(dto, current_user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_create_trip_driver_busy_raises_exception(
    trip_service: TripService,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    party_id = uuid.uuid4()
    tractor_id = uuid.uuid4()
    driver_id = uuid.uuid4()

    mock_party = Party(id=party_id, is_active=True)
    mock_tractor = Tractor(id=tractor_id, is_active=True, current_trip_id=None)
    mock_driver = Driver(id=driver_id, is_active=True, current_trip_id=uuid.uuid4())

    mock_session.get.side_effect = lambda entity, ident: {
        Party: mock_party,
        Tractor: mock_tractor,
        Driver: mock_driver
    }.get(entity)

    dto = TripCreate(
        party_id=party_id,
        tractor_id=tractor_id,
        driver_id=driver_id,
        source_location="Mines A",
        destination_location="Site B",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
        freight_amount=Decimal("15000.00"),
        advance_amount=Decimal("2000.00"),
    )

    # Act & Assert
    with pytest.raises(DriverBusyException):
        await trip_service.create_trip(dto, current_user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_create_trip_tractor_busy_raises_exception(
    trip_service: TripService,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    party_id = uuid.uuid4()
    tractor_id = uuid.uuid4()
    driver_id = uuid.uuid4()

    mock_party = Party(id=party_id, is_active=True)
    mock_tractor = Tractor(id=tractor_id, is_active=True, current_trip_id=uuid.uuid4())
    mock_driver = Driver(id=driver_id, is_active=True, current_trip_id=None)

    mock_session.get.side_effect = lambda entity, ident: {
        Party: mock_party,
        Tractor: mock_tractor,
        Driver: mock_driver
    }.get(entity)

    dto = TripCreate(
        party_id=party_id,
        tractor_id=tractor_id,
        driver_id=driver_id,
        source_location="Mines A",
        destination_location="Site B",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
        freight_amount=Decimal("15000.00"),
        advance_amount=Decimal("2000.00"),
    )

    # Act & Assert
    with pytest.raises(TractorBusyException):
        await trip_service.create_trip(dto, current_user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_update_trip_success_when_pending(
    trip_service: TripService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    mock_trip = Trip(
        id=trip_id,
        trip_number="TRIP-2026-000001",
        status=TripStatus.PENDING,
        remarks="Old remarks.",
        expected_delivery_date=datetime.date.today(),
        trip_date=datetime.date.today(),
        freight_amount=Decimal("10000.00"),
        advance_amount=Decimal("1000.00")
    )
    mock_repository.get_by_id.return_value = mock_trip

    dto = TripUpdate(remarks="Updated remarks.", expected_delivery_date=datetime.date.today() + datetime.timedelta(days=1))

    # Act
    result = await trip_service.update_trip(trip_id, dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.remarks == "Updated remarks."
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_trip_dispatched_blocks_forbidden_edits(
    trip_service: TripService,
    mock_repository: AsyncMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    mock_trip = Trip(
        id=trip_id,
        trip_number="TRIP-2026-000001",
        status=TripStatus.DISPATCHED,
        remarks="Old remarks.",
    )
    mock_repository.get_by_id.return_value = mock_trip

    dto = TripUpdate(freight_amount=Decimal("20000.00")) # Forbidden edit after dispatch

    # Act & Assert
    with pytest.raises(TripStatusException):
        await trip_service.update_trip(trip_id, dto, current_user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_status_transition_pending_to_dispatched(
    trip_service: TripService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    mock_trip = Trip(
        id=trip_id,
        status=TripStatus.PENDING,
        driver_id=uuid.uuid4(),
        tractor_id=uuid.uuid4()
    )
    mock_driver = Driver(id=mock_trip.driver_id, current_status=DriverStatus.AVAILABLE)
    mock_tractor = Tractor(id=mock_trip.tractor_id)

    mock_repository.get_by_id.return_value = mock_trip
    mock_session.get.side_effect = lambda entity, ident: {
        Driver: mock_driver,
        Tractor: mock_tractor
    }.get(entity)

    # Act
    result = await trip_service.update_trip_status(
        trip_id,
        new_status=TripStatus.DISPATCHED,
        remarks="Dispatched load.",
        current_user_id=uuid.uuid4()
    )

    # Assert
    assert result.status == TripStatus.DISPATCHED
    assert mock_driver.current_status == DriverStatus.ON_TRIP
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_status_transition_inprogress_to_completed_releases_assets(
    trip_service: TripService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    mock_trip = Trip(
        id=trip_id,
        status=TripStatus.IN_PROGRESS,
        driver_id=uuid.uuid4(),
        tractor_id=uuid.uuid4()
    )
    mock_driver = Driver(id=mock_trip.driver_id, current_trip_id=trip_id, current_status=DriverStatus.ON_TRIP)
    mock_tractor = Tractor(id=mock_trip.tractor_id, current_trip_id=trip_id)

    mock_repository.get_by_id.return_value = mock_trip
    mock_session.get.side_effect = lambda entity, ident: {
        Driver: mock_driver,
        Tractor: mock_tractor
    }.get(entity)

    # Act
    result = await trip_service.update_trip_status(
        trip_id,
        new_status=TripStatus.COMPLETED,
        remarks="Completed successfully.",
        current_user_id=uuid.uuid4()
    )

    # Assert
    assert result.status == TripStatus.COMPLETED
    assert result.actual_delivery_date == datetime.date.today()
    assert mock_driver.current_trip_id is None
    assert mock_driver.current_status == DriverStatus.AVAILABLE
    assert mock_tractor.current_trip_id is None
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_pending_trip_success(
    trip_service: TripService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    mock_trip = Trip(
        id=trip_id,
        status=TripStatus.PENDING,
        driver_id=uuid.uuid4(),
        tractor_id=uuid.uuid4()
    )
    mock_driver = Driver(id=mock_trip.driver_id, current_trip_id=trip_id, current_status=DriverStatus.AVAILABLE)
    mock_tractor = Tractor(id=mock_trip.tractor_id, current_trip_id=trip_id)

    mock_repository.get_by_id.return_value = mock_trip
    mock_session.get.side_effect = lambda entity, ident: {
        Driver: mock_driver,
        Tractor: mock_tractor
    }.get(entity)

    mock_repository.has_expenses.return_value = False
    mock_repository.has_invoice.return_value = False
    mock_repository.has_settlement.return_value = False

    # Act
    result = await trip_service.delete_trip(trip_id, current_user_id=uuid.uuid4())

    # Assert
    assert result is True
    assert mock_driver.current_trip_id is None
    assert mock_tractor.current_trip_id is None
    mock_repository.delete.assert_called_once_with(trip_id, soft=True)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_dispatched_trip_raises_exception(
    trip_service: TripService,
    mock_repository: AsyncMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    mock_trip = Trip(
        id=trip_id,
        status=TripStatus.DISPATCHED,
    )
    mock_repository.get_by_id.return_value = mock_trip

    # Act & Assert
    with pytest.raises(TripDeleteException):
        await trip_service.delete_trip(trip_id, current_user_id=uuid.uuid4())
