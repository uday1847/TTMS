import pytest
import pytest_asyncio
import uuid
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.fuel_vendor import FuelVendor
from app.infrastructure.repositories.fuel_vendor_repository import SQLAlchemyFuelVendorRepository


@pytest_asyncio.fixture
async def vendor_repo(db_session: AsyncSession):
    return SQLAlchemyFuelVendorRepository(db_session)


@pytest.mark.asyncio
async def test_create_and_get_vendor(vendor_repo, db_session):
    vendor_id = uuid.uuid4()
    vendor = FuelVendor(
        id=vendor_id,
        vendor_code="IOCL-001",
        name="Indian Oil Test",
        is_active=True,
        created_by=uuid.uuid4(),
        updated_by=uuid.uuid4()
    )
    
    created = await vendor_repo.create(vendor)
    assert created.id == vendor_id
    
    fetched = await vendor_repo.get_by_id(vendor_id)
    assert fetched is not None
    assert fetched.name == "Indian Oil Test"


@pytest.mark.asyncio
async def test_check_duplicate_vendor(vendor_repo, db_session):
    vendor_id = uuid.uuid4()
    vendor = FuelVendor(
        id=vendor_id,
        vendor_code="HP-001",
        name="HP Petrol Pump",
        gst_number="27AAAAA0000A1Z5",
        is_active=True,
        created_by=uuid.uuid4(),
        updated_by=uuid.uuid4()
    )
    await vendor_repo.create(vendor)
    
    # Should be duplicate by code
    assert await vendor_repo.check_duplicate("HP-001", "27AAAAA0000A1Z5") is True
    
    # Should not be duplicate if excluded
    assert await vendor_repo.check_duplicate("HP-001", "27AAAAA0000A1Z5", exclude_id=vendor_id) is False
    
    # Not duplicate
    assert await vendor_repo.check_duplicate("NEW-001", "27AAAAA0000A1Z6") is False
