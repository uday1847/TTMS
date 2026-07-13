from decimal import Decimal
import datetime
import pytest
import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.party import Party
from app.domain.entities.trip import Trip
from app.infrastructure.repositories.party_repository import SQLAlchemyPartyRepository


@pytest.mark.asyncio
async def test_sqlalchemy_party_repository_lifecycle(db_session: AsyncSession) -> None:
    """
    Integration test asserting Party creation, unique lookups, paginated search,
    filters, sorting, and soft deletion.
    """
    repo = SQLAlchemyPartyRepository(db_session)

    # Clean up previous entries
    async with db_session.begin():
        await db_session.execute(delete(Trip))
        await db_session.execute(delete(Party))

    # 1. Arrange: Instantiate mock parties
    party1 = Party(
        name="Jaipur Quarry Minerals",
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
        created_by=uuid.UUID(int=1),
        updated_by=uuid.UUID(int=1),
        is_active=True,
    )

    party2 = Party(
        name="Delhi Logistics Supplier",
        party_type="SUPPLIER",
        mobile_number="8888800000",
        alternate_mobile="8888811111",
        email="accounts@delhilogistics.com",
        gst_number="07BBBBB2222B2Z1",
        pan_number="BBBBB2222B",
        address="456 Outer Ring Road, Delhi",
        city="Delhi",
        state="Delhi",
        pincode="110001",
        contact_person="Amit Singh",
        opening_balance=Decimal("5000.00"),
        credit_limit=Decimal("100000.00"),
        created_by=uuid.UUID(int=1),
        updated_by=uuid.UUID(int=1),
        is_active=False,
    )

    async with db_session.begin():
        await repo.create(party1)
        await repo.create(party2)

    # 2. Test unique lookups
    found_by_mobile = await repo.get_by_mobile("9999900000")
    assert found_by_mobile is not None
    assert found_by_mobile.name == "Jaipur Quarry Minerals"

    found_by_gst = await repo.get_by_gst("07BBBBB2222B2Z1")
    assert found_by_gst is not None
    assert found_by_gst.name == "Delhi Logistics Supplier"

    found_by_pan = await repo.get_by_pan("AAAAA1111A")
    assert found_by_pan is not None
    assert found_by_pan.name == "Jaipur Quarry Minerals"

    # 3. Test pagination, search, and filtering
    # Search "Delhi"
    items, total = await repo.get_parties(page=1, size=10, search_query="Delhi")
    assert total == 1
    assert items[0].name == "Delhi Logistics Supplier"

    # Filter status "ACTIVE"
    items, total = await repo.get_parties(page=1, size=10, status_filter="ACTIVE")
    assert total == 1
    assert items[0].name == "Jaipur Quarry Minerals"

    # Filter status "INACTIVE"
    items, total = await repo.get_parties(page=1, size=10, status_filter="INACTIVE")
    assert total == 1
    assert items[0].name == "Delhi Logistics Supplier"

    # Filter by party type "CUSTOMER"
    items, total = await repo.get_parties(page=1, size=10, party_type_filter="CUSTOMER")
    assert total == 1
    assert items[0].name == "Jaipur Quarry Minerals"

    # Filter by City "Jaipur"
    items, total = await repo.get_parties(page=1, size=10, city_filter="Jaipur")
    assert total == 1
    assert items[0].name == "Jaipur Quarry Minerals"

    # 4. Test Sorting (sort by name ascending)
    items, total = await repo.get_parties(page=1, size=10, sort_by="name", order="asc")
    assert total == 2
    assert items[0].name == "Delhi Logistics Supplier"
    assert items[1].name == "Jaipur Quarry Minerals"

    # 5. Test Soft Deletion
    await repo.delete(party1.id, soft=True)
    await db_session.commit()

    # Check that deleted party is excluded by default
    items, total = await repo.get_parties(page=1, size=10)
    assert total == 1
    assert items[0].name == "Delhi Logistics Supplier"

    # Check that deleted party is included when include_deleted=True
    items, total = await repo.get_parties(page=1, size=10, include_deleted=True)
    assert total == 2
