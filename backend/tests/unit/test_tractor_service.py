import datetime
from decimal import Decimal
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.tractor import TractorCreate, TractorUpdate
from app.application.services.tractor_service import TractorService
from app.domain.entities.tractor import Tractor
from app.domain.exceptions.tractor import (
    TractorAlreadyExistsException,
    TractorHasActiveTripsException,
    TractorNotFoundException,
)
from app.domain.repositories.tractor_repository import TractorRepository


@pytest.fixture
def mock_session() -> AsyncSession:
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_repository() -> TractorRepository:
    repo = AsyncMock(spec=TractorRepository)
    return repo


@pytest.fixture
def tractor_service(mock_session: AsyncSession, mock_repository: TractorRepository) -> TractorService:
    return TractorService(session=mock_session, repository=mock_repository)


@pytest.mark.asyncio
async def test_create_tractor_success(
    tractor_service: TractorService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = TractorCreate(
        tractor_number="RJ-14-1234",
        owner_name="Jaipur Minerals",
        rc_number="RC-JAIPUR-888999",
        insurance_number="INS-TR-990011",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=365),
        manufacturer="Mahindra",
        model="Arjun",
        registration_date=datetime.date.today(),
        remarks="Test notes.",
    )
    mock_repository.get_by_tractor_number.return_value = None
    mock_repository.get_by_rc_number.return_value = None

    # Act
    result = await tractor_service.create_tractor(dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.tractor_number == "RJ-14-1234"
    assert result.rc_number == "RC-JAIPUR-888999"
    mock_repository.get_by_tractor_number.assert_called_once_with("RJ-14-1234")
    mock_repository.get_by_rc_number.assert_called_once_with("RC-JAIPUR-888999")
    mock_repository.create.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_tractor_duplicate_number(
    tractor_service: TractorService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = TractorCreate(
        tractor_number="RJ-14-1234",
        owner_name="Jaipur Minerals",
        rc_number="RC-JAIPUR-888999",
        insurance_number="INS-TR-990011",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=365),
        manufacturer="Mahindra",
        model="Arjun",
    )
    mock_repository.get_by_tractor_number.return_value = MagicMock(spec=Tractor)

    # Act & Assert
    with pytest.raises(TractorAlreadyExistsException) as exc_info:
        await tractor_service.create_tractor(dto, current_user_id=uuid.uuid4())

    assert "Tractor number 'RJ-14-1234' is already registered." in str(exc_info.value)
    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_tractor_duplicate_rc(
    tractor_service: TractorService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = TractorCreate(
        tractor_number="RJ-14-1234",
        owner_name="Jaipur Minerals",
        rc_number="RC-JAIPUR-888999",
        insurance_number="INS-TR-990011",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=365),
        manufacturer="Mahindra",
        model="Arjun",
    )
    mock_repository.get_by_tractor_number.return_value = None
    mock_repository.get_by_rc_number.return_value = MagicMock(spec=Tractor)

    # Act & Assert
    with pytest.raises(TractorAlreadyExistsException) as exc_info:
        await tractor_service.create_tractor(dto, current_user_id=uuid.uuid4())

    assert "RC number 'RC-JAIPUR-888999' is already registered." in str(exc_info.value)
    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_tractor_success(
    tractor_service: TractorService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    tractor_id = uuid.uuid4()
    mock_tractor = Tractor(
        id=tractor_id,
        tractor_number="RJ-14-1234",
        owner_name="Old Owner",
        rc_number="RC-111",
        insurance_expiry=datetime.date.today(),
    )
    mock_repository.get_by_id.return_value = mock_tractor
    dto = TractorUpdate(owner_name="New Owner", insurance_number="NEW-INS")

    # Act
    result = await tractor_service.update_tractor(tractor_id, dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.owner_name == "New Owner"
    assert result.insurance_number == "NEW-INS"
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_tractor_not_found(
    tractor_service: TractorService,
    mock_repository: AsyncMock,
) -> None:
    # Arrange
    tractor_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None
    dto = TractorUpdate(owner_name="New Owner")

    # Act & Assert
    with pytest.raises(TractorNotFoundException):
        await tractor_service.update_tractor(tractor_id, dto, current_user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_tractor_success(
    tractor_service: TractorService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    tractor_id = uuid.uuid4()
    mock_tractor = MagicMock(spec=Tractor)
    mock_repository.get_by_id.return_value = mock_tractor
    mock_repository.has_active_trips.return_value = False
    mock_repository.delete.return_value = True

    # Act
    result = await tractor_service.delete_tractor(tractor_id, current_user_id=uuid.uuid4())

    # Assert
    assert result is True
    mock_repository.delete.assert_called_once_with(tractor_id, soft=True)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_tractor_active_trips_raises_exception(
    tractor_service: TractorService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    tractor_id = uuid.uuid4()
    mock_tractor = MagicMock(spec=Tractor)
    mock_repository.get_by_id.return_value = mock_driver = mock_tractor
    mock_repository.has_active_trips.return_value = True

    # Act & Assert
    with pytest.raises(TractorHasActiveTripsException):
        await tractor_service.delete_tractor(tractor_id, current_user_id=uuid.uuid4())

    mock_repository.delete.assert_not_called()
    mock_session.commit.assert_not_called()
