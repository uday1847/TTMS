import pytest
import pytest_asyncio
import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.fuel_transaction import FuelTransaction
from app.domain.enums.fuel_station_type import FuelStationType
from app.domain.enums.fuel_type import FuelType
from app.domain.enums.fuel_payment_mode import FuelPaymentMode
from app.domain.enums.fuel_transaction_status import FuelTransactionStatus
from app.infrastructure.repositories.fuel_repository import SQLAlchemyFuelRepository

# Additional entity imports needed for foreign key constraints in DB
from app.domain.entities.tractor import Tractor
from app.domain.entities.driver import Driver
from app.domain.entities.fuel_vendor import FuelVendor


@pytest_asyncio.fixture
async def fuel_repo(db_session: AsyncSession):
    return SQLAlchemyFuelRepository(db_session)


@pytest.mark.asyncio
async def test_fuel_repository_create_and_get(fuel_repo, db_session):
    # Setup dependencies
    admin_id = uuid.uuid4()
    
    tractor = Tractor(id=uuid.uuid4(), tractor_number="TN01AA1111", owner_name="Test", rc_number="RC", insurance_number="IN", insurance_expiry=date(2025,1,1), status="ACTIVE", current_odometer=1000, is_active=True)
    driver = Driver(id=uuid.uuid4(), name="Driver", mobile_number="1234567890", license_number="LIC", status="ACTIVE")
    vendor = FuelVendor(id=uuid.uuid4(), vendor_code="V-001", name="Vendor", created_by=admin_id, updated_by=admin_id)
    
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
        station_type=FuelStationType.REGULAR,
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
