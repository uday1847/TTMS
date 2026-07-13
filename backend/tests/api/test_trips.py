from decimal import Decimal
import datetime
import pytest
import pytest_asyncio
import uuid
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.main import app
from app.infrastructure.database.session import AsyncSessionLocal, engine
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.entities.trip import Trip
from app.domain.entities.trip_status_history import TripStatusHistory
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.driver_status import DriverStatus
from app.core.security import hash_password


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db():
    # Force clean tables before and after API testing
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(delete(TripStatusHistory))
            await session.execute(delete(Trip))
            await session.execute(delete(Driver))
            await session.execute(delete(Tractor))
            await session.execute(delete(Party))
            await session.execute(delete(User).where(User.username.in_(["admintrip", "opertrip"])))
    yield
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(delete(TripStatusHistory))
            await session.execute(delete(Trip))
            await session.execute(delete(Driver))
            await session.execute(delete(Tractor))
            await session.execute(delete(Party))
            await session.execute(delete(User).where(User.username.in_(["admintrip", "opertrip"])))


@pytest.mark.asyncio
async def test_trip_api_lifecycle() -> None:
    # 1. Setup Admin, Operator accounts, Driver, Tractor, Party
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Ensure permissions catalog
            trip_permissions = [
                ("trips:create", "c"),
                ("trips:read", "r"),
                ("trips:update", "u"),
                ("trips:delete", "d"),
            ]
            perm_map = {}
            for code, desc in trip_permissions:
                stmt_p = select(Permission).where(Permission.code == code)
                p_obj = (await session.execute(stmt_p)).scalar_one_or_none()
                if not p_obj:
                    p_obj = Permission(code=code, description=desc, is_active=True)
                    session.add(p_obj)
                perm_map[code] = p_obj

            # Fetch or create roles
            stmt_admin_role = select(Role).options(selectinload(Role.permissions)).where(Role.name.in_(["admin", "Super Admin"]))
            admin_roles = (await session.execute(stmt_admin_role)).scalars().all()
            if not admin_roles:
                admin_role = Role(name="admin", display_name="Admin", is_active=True)
                session.add(admin_role)
                admin_roles = [admin_role]
            for admin_role in admin_roles:
                for p in perm_map.values():
                    if p not in admin_role.permissions:
                        admin_role.permissions.append(p)

            stmt_op_role = select(Role).options(selectinload(Role.permissions)).where(Role.name == "operator")
            op_role = (await session.execute(stmt_op_role)).scalar_one_or_none()
            if not op_role:
                op_role = Role(name="operator", display_name="Operator", is_active=True)
                session.add(op_role)
            if perm_map["trips:read"] not in op_role.permissions:
                op_role.permissions.append(perm_map["trips:read"])

            # Setup Users
            admin_user = User(
                id=uuid.uuid4(),
                email=f"admin-trip-{uuid.uuid4().hex[:6]}@example.com",
                username="admintrip",
                password_hash=hash_password("adminpass"),
                first_name="Admin",
                last_name="Tester",
                is_active=True
            )
            admin_user.roles.extend(admin_roles)
            session.add(admin_user)

            operator_user = User(
                id=uuid.uuid4(),
                email=f"operator-trip-{uuid.uuid4().hex[:6]}@example.com",
                username="opertrip",
                password_hash=hash_password("operpass"),
                first_name="Oper",
                last_name="Tester",
                is_active=True
            )
            operator_user.roles.append(op_role)
            session.add(operator_user)

            # Assets Setup
            driver = Driver(
                id=uuid.uuid4(),
                employee_code="DRV-007",
                name="James Bond",
                license_number="DL-007",
                license_expiry=datetime.date.today() + datetime.timedelta(days=100),
                license_class="HEAVY",
                contact_phone="+919999888877",
                driver_type="SALARIED",
                current_status=DriverStatus.AVAILABLE,
                is_active=True
            )
            session.add(driver)

            tractor = Tractor(
                id=uuid.uuid4(),
                tractor_number="GJ01-TR-9999",
                owner_name="Company Fleet",
                rc_number="RC-GJ9999",
                insurance_expiry=datetime.date.today() + datetime.timedelta(days=100),
                is_active=True
            )
            session.add(tractor)

            party = Party(
                id=uuid.uuid4(),
                name="Indian Oil Corp",
                party_type="Customer",
                mobile_number="9876543210",
                is_active=True
            )
            session.add(party)

            await session.flush()

            # IDs
            admin_id = admin_user.id
            operator_id = operator_user.id
            driver_id = driver.id
            tractor_id = tractor.id
            party_id = party.id

    # 2. Login to get JWT headers
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        admin_login = await ac.post("/api/v1/auth/login", json={"username_or_email": "admintrip", "password": "adminpass"})
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        oper_login = await ac.post("/api/v1/auth/login", json={"username_or_email": "opertrip", "password": "operpass"})
        assert oper_login.status_code == 200
        oper_token = oper_login.json()["data"]["access_token"]
        oper_headers = {"Authorization": f"Bearer {oper_token}"}

        # A. CREATE TRIP (Operator unauthorized block)
        payload = {
            "party_id": str(party_id),
            "tractor_id": str(tractor_id),
            "driver_id": str(driver_id),
            "source_location": "Mundra Port",
            "destination_location": "Surat Refinery",
            "trip_date": str(datetime.date.today()),
            "expected_delivery_date": str(datetime.date.today() + datetime.timedelta(days=2)),
            "freight_amount": "40000.00",
            "advance_amount": "10000.00",
            "remarks": "API testing first dispatch."
        }
        oper_create = await ac.post("/api/v1/trips", json=payload, headers=oper_headers)
        assert oper_create.status_code == 403

        # B. CREATE TRIP (Admin success)
        admin_create = await ac.post("/api/v1/trips", json=payload, headers=admin_headers)
        assert admin_create.status_code == 201
        trip_data = admin_create.json()["data"]
        trip_id = trip_data["id"]
        assert trip_data["status"] == "PENDING"
        assert trip_data["driver_name"] == "James Bond"
        assert trip_data["tractor_number"] == "GJ01-TR-9999"

        # Verify busy locks are updated in DB
        async with AsyncSessionLocal() as session:
            drv = await session.get(Driver, driver_id)
            trc = await session.get(Tractor, tractor_id)
            assert drv.current_trip_id == uuid.UUID(trip_id)
            assert trc.current_trip_id == uuid.UUID(trip_id)

        # C. CREATE TRIP COLLISION (Driver Busy -> expect 400 Bad Request)
        dup_create = await ac.post("/api/v1/trips", json=payload, headers=admin_headers)
        assert dup_create.status_code == 400
        assert "busy" in dup_create.json()["message"].lower()

        # D. GET DETAILS (Operator authorized read)
        get_details = await ac.get(f"/api/v1/trips/{trip_id}", headers=oper_headers)
        assert get_details.status_code == 200
        details = get_details.json()["data"]
        assert details["trip_number"] is not None
        assert details["trip_age"] == 0

        # E. EDIT TRIP (Pending -> fully editable)
        update_payload = {"freight_amount": "45000.00", "remarks": "Updated freight amount."}
        edit_pending = await ac.put(f"/api/v1/trips/{trip_id}", json=update_payload, headers=admin_headers)
        assert edit_pending.status_code == 200
        assert edit_pending.json()["data"]["freight_amount"] == "45000.00"

        # F. SHIFT STATUS (PENDING -> DISPATCHED)
        status_payload = {"status": "DISPATCHED", "remarks": "Driver left loading bay."}
        shift_status = await ac.patch(f"/api/v1/trips/{trip_id}/status", json=status_payload, headers=admin_headers)
        assert shift_status.status_code == 200
        assert shift_status.json()["data"]["status"] == "DISPATCHED"

        # Check driver is busy ON_TRIP
        async with AsyncSessionLocal() as session:
            drv = await session.get(Driver, driver_id)
            assert drv.current_status == DriverStatus.ON_TRIP

        # G. EDIT DISPATCHED TRIP (Forbidden checks)
        edit_forbidden = await ac.put(f"/api/v1/trips/{trip_id}", json={"freight_amount": "50000.00"}, headers=admin_headers)
        assert edit_forbidden.status_code == 400

        # Allowed edit (remarks & expected_delivery_date)
        edit_allowed = await ac.put(f"/api/v1/trips/{trip_id}", json={"remarks": "Allowed edit remarks."}, headers=admin_headers)
        assert edit_allowed.status_code == 200
        assert edit_allowed.json()["data"]["remarks"] == "Allowed edit remarks."

        # H. STATUS SHIFT (DISPATCHED -> IN_PROGRESS -> COMPLETED)
        status_payload2 = {"status": "IN_PROGRESS", "remarks": "In transit."}
        shift_ip = await ac.patch(f"/api/v1/trips/{trip_id}/status", json=status_payload2, headers=admin_headers)
        assert shift_ip.status_code == 200

        status_payload3 = {"status": "COMPLETED", "remarks": "Delivered successfully."}
        shift_comp = await ac.patch(f"/api/v1/trips/{trip_id}/status", json=status_payload3, headers=admin_headers)
        assert shift_comp.status_code == 200
        assert shift_comp.json()["data"]["actual_delivery_date"] is not None

        # Verify asset locks are released
        async with AsyncSessionLocal() as session:
            drv = await session.get(Driver, driver_id)
            trc = await session.get(Tractor, tractor_id)
            assert drv.current_trip_id is None
            assert drv.current_status == DriverStatus.AVAILABLE
            assert trc.current_trip_id is None

        # I. LIST STATUS TIMELINE HISTORY
        history_get = await ac.get(f"/api/v1/trips/{trip_id}/history", headers=oper_headers)
        assert history_get.status_code == 200
        logs = history_get.json()["data"]
        assert len(logs) == 4 # PENDING -> DISPATCHED -> IN_PROGRESS -> COMPLETED

        # J. SOFT-DELETE (Completed trip cannot be deleted -> expect 400 Bad Request)
        delete_fail = await ac.delete(f"/api/v1/trips/{trip_id}", headers=admin_headers)
        assert delete_fail.status_code == 400

        # K. SOFT-DELETE PENDING (Create another, delete it -> expect 200 Success)
        new_payload = payload.copy()
        # We need a new driver/tractor since previous is released but we want to show pending deletion release
        new_trip = await ac.post("/api/v1/trips", json=new_payload, headers=admin_headers)
        assert new_trip.status_code == 201
        new_trip_id = new_trip.json()["data"]["id"]

        delete_success = await ac.delete(f"/api/v1/trips/{new_trip_id}", headers=admin_headers)
        assert delete_success.status_code == 200

        # Verify released
        async with AsyncSessionLocal() as session:
            drv = await session.get(Driver, driver_id)
            assert drv.current_trip_id is None
