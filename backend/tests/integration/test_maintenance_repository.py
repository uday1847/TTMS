import pytest
from datetime import date
from decimal import Decimal
import uuid

from app.domain.entities.maintenance import Maintenance
from app.domain.entities.tractor import Tractor
from app.domain.enums.maintenance_status import MaintenanceStatus
from app.domain.enums.maintenance_priority import MaintenancePriority
from app.domain.enums.maintenance_type import MaintenanceType
from app.domain.enums.tractor_status import TractorStatus
from app.infrastructure.repositories.maintenance_repository import SQLAlchemyMaintenanceRepository


@pytest.fixture
def maintenance_repo(db_session):
    return SQLAlchemyMaintenanceRepository(db_session)


@pytest.mark.asyncio
async def test_create_and_get_maintenance(maintenance_repo, db_session):
    # Setup tractor
    unique_id = uuid.uuid4().hex[:8]
    tractor = Tractor(
        tractor_number=f"TR-TEST-{unique_id}",
        owner_name="Test Owner",
        rc_number=f"RC{unique_id}",
        insurance_expiry=date(2026, 12, 31),
        status=TractorStatus.ACTIVE,
        current_odometer=1000
    )
    db_session.add(tractor)
    await db_session.flush()

    # Create Maintenance
    maintenance = Maintenance(
        maintenance_number="MNT-2026-000001",
        tractor_id=tractor.id,
        maintenance_type=MaintenanceType.ENGINE_SERVICE,
        priority=MaintenancePriority.HIGH,
        status=MaintenanceStatus.SCHEDULED,
        scheduled_date=date(2026, 8, 1),
        current_odometer=1500,
        parts_cost=Decimal("500.00"),
        labor_cost=Decimal("200.00"),
        other_cost=Decimal("0.00"),
        total_cost=Decimal("700.00"),
    )
    
    saved = await maintenance_repo.save(maintenance)
    assert saved.id is not None
    
    # Get by ID
    retrieved = await maintenance_repo.get_by_id(saved.id)
    assert retrieved is not None
    assert retrieved.maintenance_number == "MNT-2026-000001"
    
    # Get by number
    retrieved_num = await maintenance_repo.get_by_number("MNT-2026-000001")
    assert retrieved_num is not None
    assert retrieved_num.id == saved.id
    
    # Get active for tractor
    active = await maintenance_repo.get_active_for_tractor(tractor.id)
    assert active is not None
    assert active.id == saved.id


@pytest.mark.asyncio
async def test_search_maintenances(maintenance_repo, db_session):
    unique_id = uuid.uuid4().hex[:8]
    tractor = Tractor(
        tractor_number=f"TR-TEST-{unique_id}",
        owner_name="Test Owner",
        rc_number=f"RC{unique_id}",
        insurance_expiry=date(2026, 12, 31),
        status=TractorStatus.ACTIVE,
        current_odometer=1000
    )
    db_session.add(tractor)
    await db_session.flush()

    maintenance = Maintenance(
        maintenance_number="MNT-2026-000002",
        tractor_id=tractor.id,
        maintenance_type=MaintenanceType.TYRE_CHANGE,
        priority=MaintenancePriority.URGENT,
        status=MaintenanceStatus.COMPLETED,
        vendor_name="Super Tyres",
        scheduled_date=date(2026, 8, 1),
        current_odometer=1500,
    )
    await maintenance_repo.save(maintenance)
    
    # Search by vendor name
    items, total = await maintenance_repo.search({"search": "Super"}, page=1, size=10)
    assert total >= 1
    assert any(m.vendor_name == "Super Tyres" for m in items)

    # Search by status
    items, total = await maintenance_repo.search({"status": MaintenanceStatus.COMPLETED}, page=1, size=10)
    assert total >= 1
    assert any(m.status == MaintenanceStatus.COMPLETED for m in items)
