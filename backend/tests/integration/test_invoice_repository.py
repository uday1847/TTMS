import datetime
from decimal import Decimal
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_status_history import InvoiceStatusHistory
from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.enums.invoice_status import InvoiceStatus
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.driver_status import DriverStatus
from app.infrastructure.repositories.invoice_repository import SQLAlchemyInvoiceRepository


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db_invoice(db_session: AsyncSession):
    # Eager clean up test records
    await db_session.execute(delete(InvoiceStatusHistory))
    await db_session.execute(delete(Invoice))
    await db_session.execute(delete(Trip))
    await db_session.execute(delete(Driver))
    await db_session.execute(delete(Tractor))
    await db_session.execute(delete(Party))
    await db_session.commit()
    yield
    await db_session.execute(delete(InvoiceStatusHistory))
    await db_session.execute(delete(Invoice))
    await db_session.execute(delete(Trip))
    await db_session.execute(delete(Driver))
    await db_session.execute(delete(Tractor))
    await db_session.execute(delete(Party))
    await db_session.commit()


@pytest.mark.asyncio
async def test_sqlalchemy_invoice_repository_operations(db_session: AsyncSession) -> None:
    # Arrange: Setup assets, party and trip
    driver = Driver(
        id=uuid.uuid4(),
        employee_code="DRV-INV-99",
        name="James Bond",
        license_number="DL-INV-99",
        license_expiry=datetime.date.today() + datetime.timedelta(days=100),
        license_class="HEAVY",
        contact_phone="+919999111222",
        driver_type="SALARIED",
        current_status=DriverStatus.AVAILABLE,
        is_active=True
    )
    tractor = Tractor(
        id=uuid.uuid4(),
        tractor_number="GJ01-INV-9999",
        owner_name="Company Fleet",
        rc_number="RC-GJ-INV-9999",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=100),
        is_active=True
    )
    party = Party(
        id=uuid.uuid4(),
        name="Reliance Logistics",
        party_type="Customer",
        mobile_number="9998887776",
        gst_number="24AAAAR1111A1Z1",
        pan_number="AAAAP1111A",
        is_active=True
    )
    trip = Trip(
        id=uuid.uuid4(),
        trip_number="TRIP-2026-999999",
        party_id=party.id,
        tractor_id=tractor.id,
        driver_id=driver.id,
        source_location="Mundra Port",
        destination_location="Surat Refinery",
        trip_date=datetime.date.today(),
        expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
        freight_amount=Decimal("50000.00"),
        advance_amount=Decimal("10000.00"),
        status=TripStatus.COMPLETED,
        is_active=True,
    )
    
    db_session.add(driver)
    db_session.add(tractor)
    db_session.add(party)
    db_session.add(trip)
    await db_session.flush()

    repository = SQLAlchemyInvoiceRepository(db_session)

    # 1. Create Invoices
    inv1 = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-2026-000001",
        trip_id=trip.id,
        party_id=party.id,
        invoice_date=datetime.date.today(),
        due_date=datetime.date.today() + datetime.timedelta(days=15),
        gross_amount=Decimal("50000.00"),
        received_amount=Decimal("15000.00"),
        balance_amount=Decimal("35000.00"),
        status=InvoiceStatus.PARTIALLY_PAID,
        is_active=True,
        version_id=1,
    )
    
    await repository.create(inv1)
    await db_session.commit()

    # 2. Get by ID (confirm eager load is successful)
    fetched = await repository.get_by_id(inv1.id)
    assert fetched is not None
    assert fetched.invoice_number == "INV-2026-000001"
    assert fetched.trip.trip_number == "TRIP-2026-999999"
    assert fetched.party.name == "Reliance Logistics"

    # 3. get_by_invoice_number & get_by_trip
    fetched_num = await repository.get_by_invoice_number("INV-2026-000001")
    assert fetched_num is not None
    fetched_trip = await repository.get_by_trip(trip.id)
    assert fetched_trip is not None

    # 4. get_max_sequence_for_year
    max_seq = await repository.get_max_sequence_for_year(2026)
    assert max_seq == 1

    # 5. Dashboard Summary metrics verification
    summary = await repository.get_invoice_dashboard_summary()
    assert summary["total_invoices"] == 1
    assert summary["partially_paid_count"] == 1
    assert summary["total_revenue"] == Decimal("50000.00")
    assert summary["total_collected"] == Decimal("15000.00")
    assert summary["total_outstanding"] == Decimal("35000.00")
    assert summary["monthly_analytics"]["revenue"] == Decimal("50000.00")

    # 6. Listing paginated invoice checks
    invoices, total = await repository.get_invoices(
        search_query="Reliance",
        status=InvoiceStatus.PARTIALLY_PAID,
    )
    assert total == 1
    assert invoices[0].invoice_number == "INV-2026-000001"

    # 7. Search by PAN/GST checks
    invoices_pan, total_pan = await repository.get_invoices(
        search_query="AAAAP1111A",
    )
    assert total_pan == 1
