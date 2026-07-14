import pytest
import pytest_asyncio
import uuid
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.domain.entities.fuel_vendor import FuelVendor
from app.domain.entities.user import User
from app.infrastructure.repositories.fuel_vendor_repository import SQLAlchemyFuelVendorRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


@pytest_asyncio.fixture
async def vendor_repo(db_session: AsyncSession):
    return SQLAlchemyFuelVendorRepository(db_session)


@pytest.mark.asyncio
async def test_create_and_get_vendor(vendor_repo, db_session):
    user_repo = SQLAlchemyUserRepository(db_session)
    user = User(email=f"vendor_{uuid.uuid4().hex[:8]}@test.com", username=f"vendor_{uuid.uuid4().hex[:8]}", password_hash="hash", first_name="T", last_name="T", is_active=True)
    created_user = await user_repo.create(user)
    await db_session.flush()

    vendor_id = uuid.uuid4()
    vendor = FuelVendor(
        id=vendor_id,
        vendor_code=f"IOCL-{uuid.uuid4().hex[:6]}",
        name="Indian Oil Test",
        is_active=True,
        created_by=created_user.id,
        updated_by=created_user.id
    )
    
    created = await vendor_repo.create(vendor)
    await db_session.flush()
    
    assert created.id == vendor_id
    
    fetched = await vendor_repo.get_by_id(vendor_id)
    assert fetched is not None
    assert fetched.name == "Indian Oil Test"


@pytest.mark.asyncio
async def test_check_duplicate_vendor(vendor_repo, db_session):
    user_repo = SQLAlchemyUserRepository(db_session)
    user = User(email=f"vendor2_{uuid.uuid4().hex[:8]}@test.com", username=f"vendor2_{uuid.uuid4().hex[:8]}", password_hash="hash", first_name="T", last_name="T", is_active=True)
    created_user = await user_repo.create(user)
    await db_session.flush()

    vendor_id = uuid.uuid4()
    code = f"HP-{uuid.uuid4().hex[:6]}"
    gst = f"27AAAAA0000{uuid.uuid4().hex[:4].upper()}Z5"
    vendor = FuelVendor(
        id=vendor_id,
        vendor_code=code,
        name="HP Petrol Pump",
        gst_number=gst,
        is_active=True,
        created_by=created_user.id,
        updated_by=created_user.id
    )
    await vendor_repo.create(vendor)
    await db_session.flush()
    
    # Should be duplicate by code
    assert await vendor_repo.check_duplicate(code, gst) is True
    
    # Should not be duplicate if excluded
    assert await vendor_repo.check_duplicate(code, gst, exclude_id=vendor_id) is False
    
    # Not duplicate
    assert await vendor_repo.check_duplicate("NEW-001", "27AAAAA0000A1Z6") is False
