import datetime
from decimal import Decimal
import pytest
import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.tractor import Tractor
from app.domain.entities.trip import Trip
from app.infrastructure.repositories.tractor_repository import SQLAlchemyTractorRepository


@pytest.mark.asyncio
async def test_sqlalchemy_tractor_repository_lifecycle(db_session: AsyncSession) -> None:
    """
    Integration test asserting Tractor creation, unique lookups, paginated search,
    filters, sorting, and soft deletion.
    """
    repo = SQLAlchemyTractorRepository(db_session)

    # Clean up previous tractors and referencing trips
    async with db_session.begin():
        await db_session.execute(delete(Trip))
        await db_session.execute(delete(Tractor))

    # 1. Arrange: Instantiate mock tractors
    tractor1 = Tractor(
        tractor_number="MH-12-AA-1111",
        owner_name="Asset Management Ltd",
        rc_number="RC-MH-1111",
        insurance_number="INS-1111",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=10),
        manufacturer="John Deere",
        model="5050D",
        created_by=uuid.UUID(int=1),
        updated_by=uuid.UUID(int=1),
        is_active=True,
    )

    tractor2 = Tractor(
        tractor_number="MH-12-BB-2222",
        owner_name="Fleet Owners Co",
        rc_number="RC-MH-2222",
        insurance_number="INS-2222",
        insurance_expiry=datetime.date.today() + datetime.timedelta(days=100),
        manufacturer="Mahindra",
        model="Arjun",
        created_by=uuid.UUID(int=1),
        updated_by=uuid.UUID(int=1),
        is_active=False,
    )

    async with db_session.begin():
        await repo.create(tractor1)
        await repo.create(tractor2)

    # 2. Test unique checks
    found_by_num = await repo.get_by_tractor_number("MH-12-AA-1111")
    assert found_by_num is not None
    assert found_by_num.owner_name == "Asset Management Ltd"

    found_by_rc = await repo.get_by_rc_number("RC-MH-2222")
    assert found_by_rc is not None
    assert found_by_rc.tractor_number == "MH-12-BB-2222"

    # 3. Test pagination, search, and filtering
    # Search "fleet"
    items, total = await repo.get_tractors(page=1, size=10, search_query="fleet")
    assert total == 1
    assert items[0].tractor_number == "MH-12-BB-2222"

    # Filter status "ACTIVE"
    items, total = await repo.get_tractors(page=1, size=10, status_filter="ACTIVE")
    assert total == 1
    assert items[0].tractor_number == "MH-12-AA-1111"

    # Filter status "INACTIVE"
    items, total = await repo.get_tractors(page=1, size=10, status_filter="INACTIVE")
    assert total == 1
    assert items[0].tractor_number == "MH-12-BB-2222"

    # Filter insurance expiring within 15 days
    items, total = await repo.get_tractors(page=1, size=10, insurance_expiring_days=15)
    assert total == 1
    assert items[0].tractor_number == "MH-12-AA-1111"

    # 4. Test Sorting (sort by tractor_number ascending)
    items, total = await repo.get_tractors(page=1, size=10, sort_by="tractor_number", order="asc")
    assert total == 2
    assert items[0].tractor_number == "MH-12-AA-1111"
    assert items[1].tractor_number == "MH-12-BB-2222"

    # 5. Test Soft Deletion
    await repo.delete(tractor1.id, soft=True)
    await db_session.commit()

    # Check that deleted tractor is excluded by default
    items, total = await repo.get_tractors(page=1, size=10)
    assert total == 1
    assert items[0].tractor_number == "MH-12-BB-2222"

    # Check that deleted tractor is included when include_deleted=True
    items, total = await repo.get_tractors(page=1, size=10, include_deleted=True)
    assert total == 2
