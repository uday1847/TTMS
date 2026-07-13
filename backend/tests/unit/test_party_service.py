from decimal import Decimal
import datetime
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.party import PartyCreate, PartyUpdate
from app.application.services.party_service import PartyService
from app.domain.entities.party import Party
from app.domain.exceptions.party import (
    PartyAlreadyExistsException,
    PartyHasActiveTripsException,
    PartyNotFoundException,
)
from app.domain.repositories.party_repository import PartyRepository


@pytest.fixture
def mock_session() -> AsyncSession:
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_repository() -> PartyRepository:
    repo = AsyncMock(spec=PartyRepository)
    return repo


@pytest.fixture
def party_service(mock_session: AsyncSession, mock_repository: PartyRepository) -> PartyService:
    return PartyService(session=mock_session, repository=mock_repository)


@pytest.mark.asyncio
async def test_create_party_success(
    party_service: PartyService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = PartyCreate(
        name="Jaipur Minerals",
        party_type="CUSTOMER",
        mobile_number="9999900000",
        alternate_mobile="9999911111",
        email="contact@jaipurminerals.com",
        gst_number="08AAAAA1111A1Z2",
        pan_number="AAAAA1111A",
        address="123 Quarry Road, Jaipur",
        city="Jaipur",
        state="Rajasthan",
        pincode="302001",
        contact_person="Raj Kumar",
        opening_balance=Decimal("15000.00"),
        credit_limit=Decimal("50000.00"),
        remarks="Test notes.",
    )
    mock_repository.get_by_mobile.return_value = None
    mock_repository.get_by_gst.return_value = None
    mock_repository.get_by_pan.return_value = None

    # Act
    result = await party_service.create_party(dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.name == "Jaipur Minerals"
    assert result.mobile_number == "9999900000"
    assert result.gst_number == "08AAAAA1111A1Z2"
    mock_repository.get_by_mobile.assert_called_once_with("9999900000")
    mock_repository.get_by_gst.assert_called_once_with("08AAAAA1111A1Z2")
    mock_repository.get_by_pan.assert_called_once_with("AAAAA1111A")
    mock_repository.create.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_party_duplicate_mobile(
    party_service: PartyService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = PartyCreate(
        name="Jaipur Minerals",
        party_type="CUSTOMER",
        mobile_number="9999900000",
        opening_balance=Decimal("0.00"),
        credit_limit=Decimal("0.00"),
    )
    mock_repository.get_by_mobile.return_value = MagicMock(spec=Party)

    # Act & Assert
    with pytest.raises(PartyAlreadyExistsException) as exc_info:
        await party_service.create_party(dto, current_user_id=uuid.uuid4())

    assert "Mobile number '9999900000' is already registered." in str(exc_info.value)
    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_party_duplicate_gst(
    party_service: PartyService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = PartyCreate(
        name="Jaipur Minerals",
        party_type="CUSTOMER",
        mobile_number="9999900000",
        gst_number="08AAAAA1111A1Z2",
        opening_balance=Decimal("0.00"),
        credit_limit=Decimal("0.00"),
    )
    mock_repository.get_by_mobile.return_value = None
    mock_repository.get_by_gst.return_value = MagicMock(spec=Party)

    # Act & Assert
    with pytest.raises(PartyAlreadyExistsException) as exc_info:
        await party_service.create_party(dto, current_user_id=uuid.uuid4())

    assert "GST number '08AAAAA1111A1Z2' is already registered." in str(exc_info.value)
    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_party_duplicate_pan(
    party_service: PartyService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = PartyCreate(
        name="Jaipur Minerals",
        party_type="CUSTOMER",
        mobile_number="9999900000",
        pan_number="AAAAA1111A",
        opening_balance=Decimal("0.00"),
        credit_limit=Decimal("0.00"),
    )
    mock_repository.get_by_mobile.return_value = None
    mock_repository.get_by_gst.return_value = None
    mock_repository.get_by_pan.return_value = MagicMock(spec=Party)

    # Act & Assert
    with pytest.raises(PartyAlreadyExistsException) as exc_info:
        await party_service.create_party(dto, current_user_id=uuid.uuid4())

    assert "PAN number 'AAAAA1111A' is already registered." in str(exc_info.value)
    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_party_success(
    party_service: PartyService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    party_id = uuid.uuid4()
    mock_party = Party(
        id=party_id,
        name="Old Name",
        party_type="CUSTOMER",
        mobile_number="9999900000",
        opening_balance=Decimal("0.00"),
        credit_limit=Decimal("0.00"),
    )
    mock_repository.get_by_id.return_value = mock_party
    dto = PartyUpdate(name="New Name", credit_limit=Decimal("75000.00"))

    # Act
    result = await party_service.update_party(party_id, dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.name == "New Name"
    assert result.credit_limit == Decimal("75000.00")
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_party_not_found(
    party_service: PartyService,
    mock_repository: AsyncMock,
) -> None:
    # Arrange
    party_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None
    dto = PartyUpdate(name="New Name")

    # Act & Assert
    with pytest.raises(PartyNotFoundException):
        await party_service.update_party(party_id, dto, current_user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_party_success(
    party_service: PartyService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    party_id = uuid.uuid4()
    mock_party = MagicMock(spec=Party)
    mock_repository.get_by_id.return_value = mock_party
    mock_repository.has_active_trips.return_value = False
    mock_repository.delete.return_value = True

    # Act
    result = await party_service.delete_party(party_id, current_user_id=uuid.uuid4())

    # Assert
    assert result is True
    mock_repository.delete.assert_called_once_with(party_id, soft=True)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_party_active_trips_raises_exception(
    party_service: PartyService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    party_id = uuid.uuid4()
    mock_party = MagicMock(spec=Party)
    mock_repository.get_by_id.return_value = mock_party
    mock_repository.has_active_trips.return_value = True

    # Act & Assert
    with pytest.raises(PartyHasActiveTripsException):
        await party_service.delete_party(party_id, current_user_id=uuid.uuid4())

    mock_repository.delete.assert_not_called()
    mock_session.commit.assert_not_called()
