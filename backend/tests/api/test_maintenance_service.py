import uuid
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

from app.application.dtos.maintenance import MaintenanceCreate, MaintenanceStatusUpdate
from app.application.services.maintenance_service import MaintenanceService
from app.domain.entities.maintenance import Maintenance
from app.domain.entities.tractor import Tractor
from app.domain.enums.maintenance_status import MaintenanceStatus
from app.domain.enums.maintenance_priority import MaintenancePriority
from app.domain.enums.maintenance_type import MaintenanceType
from app.domain.enums.tractor_status import TractorStatus
from app.domain.exceptions.maintenance import (
    MaintenanceValidationException,
    MaintenanceAlreadyScheduledException,
    MaintenanceStatusException,
)
from app.domain.exceptions.tractor import TractorNotFoundException


@pytest.fixture
def mock_maintenance_repo():
    repo = AsyncMock()
    repo.save = AsyncMock(side_effect=lambda m: m)
    return repo


@pytest.fixture
def mock_tractor_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_maintenance_repo, mock_tractor_repo):
    return MaintenanceService(mock_maintenance_repo, mock_tractor_repo)


@pytest.mark.asyncio
async def test_create_maintenance_success(service, mock_tractor_repo, mock_maintenance_repo):
    tractor_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_tractor_repo.get_by_id.return_value = Tractor(id=tractor_id, current_odometer=1000, status=TractorStatus.ACTIVE, is_active=True)
    mock_maintenance_repo.get_active_for_tractor.return_value = None

    data = MaintenanceCreate(
        tractor_id=tractor_id,
        maintenance_type=MaintenanceType.ENGINE_SERVICE,
        priority=MaintenancePriority.HIGH,
        scheduled_date=date(2026, 8, 1),
        current_odometer=1500,
        parts_cost=Decimal("500.00"),
        labor_cost=Decimal("200.00"),
        other_cost=Decimal("0.00"),
    )

    maintenance = await service.create_maintenance(data, user_id)

    assert maintenance.tractor_id == tractor_id
    assert maintenance.total_cost == Decimal("700.00")
    assert maintenance.status == MaintenanceStatus.SCHEDULED
    assert len(maintenance.histories) == 1
    assert maintenance.histories[0].new_total_cost == Decimal("700.00")


@pytest.mark.asyncio
async def test_create_maintenance_odometer_validation(service, mock_tractor_repo, mock_maintenance_repo):
    tractor_id = uuid.uuid4()
    mock_tractor_repo.get_by_id.return_value = Tractor(id=tractor_id, current_odometer=2000, status=TractorStatus.ACTIVE, is_active=True)

    data = MaintenanceCreate(
        tractor_id=tractor_id,
        maintenance_type=MaintenanceType.GENERAL_SERVICE,
        priority=MaintenancePriority.LOW,
        scheduled_date=date(2026, 8, 1),
        current_odometer=1000,  # Lower than tractor's 2000
    )

    with pytest.raises(MaintenanceValidationException):
        await service.create_maintenance(data, uuid.uuid4())


@pytest.mark.asyncio
async def test_create_maintenance_duplicate_active(service, mock_tractor_repo, mock_maintenance_repo):
    tractor_id = uuid.uuid4()
    mock_tractor_repo.get_by_id.return_value = Tractor(id=tractor_id, current_odometer=1000, status=TractorStatus.ACTIVE, is_active=True)
    mock_maintenance_repo.get_active_for_tractor.return_value = Maintenance()  # Indicates an active one exists

    data = MaintenanceCreate(
        tractor_id=tractor_id,
        maintenance_type=MaintenanceType.GENERAL_SERVICE,
        priority=MaintenancePriority.LOW,
        scheduled_date=date(2026, 8, 1),
        current_odometer=1500,
    )

    with pytest.raises(MaintenanceAlreadyScheduledException):
        await service.create_maintenance(data, uuid.uuid4())


@pytest.mark.asyncio
async def test_update_status_tractor_sync(service, mock_tractor_repo, mock_maintenance_repo):
    tractor_id = uuid.uuid4()
    maintenance_id = uuid.uuid4()
    user_id = uuid.uuid4()

    tractor = Tractor(id=tractor_id, status=TractorStatus.ACTIVE, current_odometer=1000)
    maintenance = Maintenance(
        id=maintenance_id,
        tractor_id=tractor_id,
        status=MaintenanceStatus.SCHEDULED,
        current_odometer=1500,
    )

    mock_maintenance_repo.get_by_id.return_value = maintenance
    mock_tractor_repo.get_by_id.return_value = tractor

    # Test SCHEDULED -> IN_PROGRESS
    update_data = MaintenanceStatusUpdate(status=MaintenanceStatus.IN_PROGRESS)
    updated_maintenance = await service.update_status(maintenance_id, update_data, user_id)
    
    assert updated_maintenance.status == MaintenanceStatus.IN_PROGRESS
    assert tractor.status == TractorStatus.IN_MAINTENANCE

    # Test IN_PROGRESS -> COMPLETED
    update_data = MaintenanceStatusUpdate(status=MaintenanceStatus.COMPLETED)
    updated_maintenance = await service.update_status(maintenance_id, update_data, user_id)
    
    assert updated_maintenance.status == MaintenanceStatus.COMPLETED
    assert tractor.status == TractorStatus.ACTIVE
    assert tractor.current_odometer == 1500  # Synced from maintenance
