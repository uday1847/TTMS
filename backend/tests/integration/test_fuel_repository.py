import pytest
import pytest_asyncio
import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.domain.entities.fuel_transaction import FuelTransaction
from app.domain.enums.fuel_station_type import FuelStationType
from app.domain.enums.fuel_type import FuelType
from app.domain.enums.fuel_payment_mode import FuelPaymentMode
from app.domain.enums.fuel_transaction_status import FuelTransactionStatus
from app.domain.enums.driver_status import DriverStatus
from app.infrastructure.repositories.fuel_repository import SQLAlchemyFuelRepository

# Additional entity imports needed for foreign key constraints in DB
from app.domain.entities.tractor import Tractor
from app.domain.entities.driver import Driver
from app.domain.entities.fuel_vendor import FuelVendor
from app.domain.entities.user import User


@pytest_asyncio.fixture
async def fuel_repo(db_session: AsyncSession):
    return SQLAlchemyFuelRepository(db_session)


@pytest.mark.asyncio
async def test_fuel_repository_create_and_get(fuel_repo, db_session):
    # Setup dependencies
    admin_id = uuid.uuid4()
    
    user = User(id=admin_id, email=f"fuel_{uuid.uuid4().hex[:8]}@test.com", username=f"fuel_{uuid.uuid4().hex[:8]}", password_hash="hash", first_name="T", last_name="T", is_active=True)
    tractor = Tractor(id=uuid.uuid4(), tractor_number=f"TN01{uuid.uuid4().hex[:4].upper()}", owner_name="Test", rc_number="RC", insurance_number="IN", insurance_expiry=date(2025,1,1), status="ACTIVE", current_odometer=1000, is_active=True)
    driver = Driver(
        id=uuid.uuid4(), 
        name="Driver", 
        contact_phone=f"1234{uuid.uuid4().hex[:6]}", 
        license_number=f"LIC-{uuid.uuid4().hex[:6]}", 
        employee_code=f"EMP-{uuid.uuid4().hex[:6]}",
        license_expiry=date(2025,1,1),
        license_class="HMV",
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE
    )
    vendor = FuelVendor(id=uuid.uuid4(), vendor_code=f"V-{uuid.uuid4().hex[:6]}", name="Vendor", created_by=admin_id, updated_by=admin_id)
    
    db_session.add(user)
    await db_session.flush()
    db_session.add(tractor)
    db_session.add(driver)
    db_session.add(vendor)
    await db_session.flush()

    # Create fuel transaction
    tx_id = uuid.uuid4()
    tx = FuelTransaction(
        id=tx_id,
        fuel_number="FUEL-2023-001",
        tractor_id=tractor.id,
        driver_id=driver.id,
        vendor_id=vendor.id,
        station_type=FuelStationType.PRIVATE,
        fuel_type=FuelType.DIESEL,
        fuel_date=date.today(),
        odometer=1500,
        liters=Decimal("50.0"),
        rate_per_liter=Decimal("90.0"),
        amount=Decimal("4500.0"),
        payment_mode=FuelPaymentMode.CASH,
        status=FuelTransactionStatus.DRAFT,
        created_by=admin_id,
        updated_by=admin_id
    )
    
    await fuel_repo.create(tx)
    
    fetched = await fuel_repo.get_by_id(tx_id)
    assert fetched is not None
    assert fetched.fuel_number == "FUEL-2023-001"
    assert fetched.amount == Decimal("4500.0")

    # Check duplicate
    is_duplicate = await fuel_repo.check_duplicate(tractor.id, vendor.id, date.today(), float("4500.0"), float("50.0"))
    assert is_duplicate is True
