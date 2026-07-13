import datetime
from decimal import Decimal
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.driver import DriverCreate, DriverUpdate
from app.application.services.driver_service import DriverService
from app.domain.entities.driver import Driver
from app.domain.enums.driver_status import DriverStatus
from app.domain.exceptions.driver import (
    DriverAlreadyExistsException,
    DriverHasActiveTripsException,
    DriverNotFoundException,
)
from app.domain.repositories.driver_repository import DriverRepository


@pytest.fixture
def mock_session() -> AsyncSession:
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_repository() -> DriverRepository:
    repo = AsyncMock(spec=DriverRepository)
    return repo


@pytest.fixture
def driver_service(mock_session: AsyncSession, mock_repository: DriverRepository) -> DriverService:
    return DriverService(session=mock_session, repository=mock_repository)


@pytest.mark.asyncio
async def test_create_driver_success(
    driver_service: DriverService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = DriverCreate(
        name="Test Driver",
        address="123 Street",
        employee_code="DRV-001",
        license_number="LIC-12345",
        license_expiry=datetime.date.today() + datetime.timedelta(days=30),
        license_class="Heavy",
        contact_phone="9999988888",
        emergency_contact_phone="9999911111",
        fixed_salary=Decimal("15000.00"),
        commission_percentage=Decimal("4.00"),
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
    )
    mock_repository.get_by_employee_code.return_value = None
    mock_repository.get_by_license_number.return_value = None
    mock_repository.get_by_contact_phone.return_value = None
    
    mock_driver = MagicMock(spec=Driver)
    mock_repository.create.return_value = mock_driver

    # Act
    result = await driver_service.create_driver(dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.name == "Test Driver"
    mock_repository.get_by_employee_code.assert_called_once_with("DRV-001")
    mock_repository.get_by_license_number.assert_called_once_with("LIC-12345")
    mock_repository.get_by_contact_phone.assert_called_once_with("9999988888")
    mock_repository.create.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_driver_duplicate_employee_code(
    driver_service: DriverService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = DriverCreate(
        name="Test Driver",
        address="123 Street",
        employee_code="DRV-001",
        license_number="LIC-12345",
        license_expiry=datetime.date.today() + datetime.timedelta(days=30),
        license_class="Heavy",
        contact_phone="9999988888",
        emergency_contact_phone="9999911111",
        fixed_salary=Decimal("15000.00"),
        commission_percentage=Decimal("4.00"),
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
    )
    mock_repository.get_by_employee_code.return_value = MagicMock(spec=Driver)

    # Act & Assert
    with pytest.raises(DriverAlreadyExistsException) as exc_info:
        await driver_service.create_driver(dto, current_user_id=uuid.uuid4())
    
    assert "Employee code 'DRV-001' is already registered." in str(exc_info.value)
    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_driver_duplicate_license(
    driver_service: DriverService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = DriverCreate(
        name="Test Driver",
        address="123 Street",
        employee_code="DRV-001",
        license_number="LIC-12345",
        license_expiry=datetime.date.today() + datetime.timedelta(days=30),
        license_class="Heavy",
        contact_phone="9999988888",
        emergency_contact_phone="9999911111",
        fixed_salary=Decimal("15000.00"),
        commission_percentage=Decimal("4.00"),
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
    )
    mock_repository.get_by_employee_code.return_value = None
    mock_repository.get_by_license_number.return_value = MagicMock(spec=Driver)

    # Act & Assert
    with pytest.raises(DriverAlreadyExistsException) as exc_info:
        await driver_service.create_driver(dto, current_user_id=uuid.uuid4())
    
    assert "Driving license 'LIC-12345' is already registered." in str(exc_info.value)
    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_driver_duplicate_phone(
    driver_service: DriverService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    dto = DriverCreate(
        name="Test Driver",
        address="123 Street",
        employee_code="DRV-001",
        license_number="LIC-12345",
        license_expiry=datetime.date.today() + datetime.timedelta(days=30),
        license_class="Heavy",
        contact_phone="9999988888",
        emergency_contact_phone="9999911111",
        fixed_salary=Decimal("15000.00"),
        commission_percentage=Decimal("4.00"),
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
    )
    mock_repository.get_by_employee_code.return_value = None
    mock_repository.get_by_license_number.return_value = None
    mock_repository.get_by_contact_phone.return_value = MagicMock(spec=Driver)

    # Act & Assert
    with pytest.raises(DriverAlreadyExistsException) as exc_info:
        await driver_service.create_driver(dto, current_user_id=uuid.uuid4())
    
    assert "Mobile number '9999988888' is already registered." in str(exc_info.value)
    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_driver_success(
    driver_service: DriverService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    driver_id = uuid.uuid4()
    mock_driver = Driver(
        id=driver_id,
        name="Old Name",
        address="Old Address",
        employee_code="DRV-001",
        license_number="LIC-12345",
        contact_phone="9999988888",
        license_expiry=datetime.date.today(),
        license_class="Heavy",
        fixed_salary=Decimal("10000"),
        commission_percentage=Decimal("2"),
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
    )
    mock_repository.get_by_id.return_value = mock_driver
    dto = DriverUpdate(name="New Name", address="New Address")

    # Act
    result = await driver_service.update_driver(driver_id, dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.name == "New Name"
    assert result.address == "New Address"
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_driver_not_found(
    driver_service: DriverService,
    mock_repository: AsyncMock,
) -> None:
    # Arrange
    driver_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None
    dto = DriverUpdate(name="New Name")

    # Act & Assert
    with pytest.raises(DriverNotFoundException):
        await driver_service.update_driver(driver_id, dto, current_user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_update_driver_status_override(
    driver_service: DriverService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    driver_id = uuid.uuid4()
    mock_driver = Driver(
        id=driver_id,
        name="Test",
        employee_code="DRV-001",
        license_number="LIC-12345",
        contact_phone="9999988888",
        license_expiry=datetime.date.today(),
        license_class="Heavy",
        current_status=DriverStatus.AVAILABLE,
        is_active=True,
        driver_type="SALARIED",
    )
    mock_repository.get_by_id.return_value = mock_driver
    dto = DriverUpdate(is_active=False)

    # Act
    result = await driver_service.update_driver(driver_id, dto, current_user_id=uuid.uuid4())

    # Assert
    assert result.is_active is False
    assert result.current_status == DriverStatus.INACTIVE
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_driver_success(
    driver_service: DriverService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    driver_id = uuid.uuid4()
    mock_driver = MagicMock(spec=Driver)
    mock_repository.get_by_id.return_value = mock_driver
    mock_repository.has_active_trips.return_value = False
    mock_repository.delete.return_value = True

    # Act
    result = await driver_service.delete_driver(driver_id, current_user_id=uuid.uuid4())

    # Assert
    assert result is True
    mock_repository.delete.assert_called_once_with(driver_id, soft=True)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_driver_active_trips_raises_exception(
    driver_service: DriverService,
    mock_repository: AsyncMock,
    mock_session: AsyncSession,
) -> None:
    # Arrange
    driver_id = uuid.uuid4()
    mock_driver = MagicMock(spec=Driver)
    mock_repository.get_by_id.return_value = mock_driver
    mock_repository.has_active_trips.return_value = True

    # Act & Assert
    with pytest.raises(DriverHasActiveTripsException):
        await driver_service.delete_driver(driver_id, current_user_id=uuid.uuid4())

    mock_repository.delete.assert_not_called()
    mock_session.commit.assert_not_called()
