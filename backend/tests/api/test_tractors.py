import datetime
from decimal import Decimal
import pytest
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
from app.domain.entities.quarry import Quarry
from app.domain.entities.material import Material
from app.domain.entities.trip import Trip
from app.domain.enums.trip_status import TripStatus
from app.core.security import hash_password
from app.domain.enums.driver_status import DriverStatus


@pytest.mark.asyncio
async def test_tractors_module_full_lifecycle() -> None:
    """
    Validates complete Phase 1 operations for the Tractor module.
    Covers:
    - Creating permissions
    - Seeding test users (Admin, Operator)
    - Full CRUD logic (Create, Read, Search/Filter, Update, Toggle Status, Soft Delete)
    - Duplications checks (Conflicts on unique tractor number/RC number)
    - Deletion check when linked to active trips
    - RBAC authorization checks (Operator denied on write actions)
    """

    # 1. Setup DB state (permissions, roles, user accounts)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Clean up sessions and previous tractor data
            await session.execute(delete(Trip))
            await session.execute(delete(Tractor))

            # Ensure tractor permissions exist in permissions catalog
            tractor_permissions = [
                ("tractors:read", "Read tractors"),
                ("tractors:create", "Create tractors"),
                ("tractors:update", "Update tractors"),
                ("tractors:delete", "Delete tractors"),
            ]
            perm_map = {}
            for code, desc in tractor_permissions:
                stmt_p = select(Permission).where(Permission.code == code)
                p_obj = (await session.execute(stmt_p)).scalar_one_or_none()
                if not p_obj:
                    p_obj = Permission(code=code, description=desc, is_active=True)
                    session.add(p_obj)
                perm_map[code] = p_obj

            # Admin Role setup (all permissions)
            stmt_admin_role = select(Role).options(selectinload(Role.permissions)).where(Role.name.in_(["admin", "Super Admin"]))
            admin_roles = (await session.execute(stmt_admin_role)).scalars().all()
            for admin_role in admin_roles:
                for p in perm_map.values():
                    if p not in admin_role.permissions:
                        admin_role.permissions.append(p)

            # Operator Role setup (read-only tractors permission)
            stmt_op_role = select(Role).options(selectinload(Role.permissions)).where(Role.name == "operator")
            op_role = (await session.execute(stmt_op_role)).scalar_one_or_none()
            if not op_role:
                op_role = Role(name="operator", display_name="Operator Role", is_active=True)
                session.add(op_role)
            if perm_map["tractors:read"] not in op_role.permissions:
                op_role.permissions.append(perm_map["tractors:read"])

    await engine.dispose()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # A. Login to get tokens
        admin_login = await ac.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Admin@123"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        operator_login = await ac.post(
            "/api/v1/auth/token",
            data={"username": "operator_test", "password": "OperatorPass123!"},
        )
        assert operator_login.status_code == 200
        operator_token = operator_login.json()["access_token"]
        operator_headers = {"Authorization": f"Bearer {operator_token}"}

        # B. TEST: Create Tractor as Admin (Success)
        tractor_payload = {
            "tractor_number": "RJ-14-TR-9999",
            "owner_name": "Jaipur Fleet Group",
            "rc_number": "RC-JAIPUR-888777",
            "insurance_number": "INS-TR-777",
            "insurance_expiry": str(datetime.date.today() + datetime.timedelta(days=365)),
            "manufacturer": "John Deere",
            "model": "5050D",
            "registration_date": str(datetime.date.today() - datetime.timedelta(days=100)),
            "remarks": "Fleet operational."
        }
        create_res = await ac.post("/api/v1/tractors", json=tractor_payload, headers=admin_headers)
        assert create_res.status_code == 201
        tractor_data = create_res.json()["data"]
        assert tractor_data["tractor_number"] == "RJ-14-TR-9999"
        tractor_id = tractor_data["id"]

        # C. TEST: Conflict Checks (Duplicate RC number / Tractor number)
        dup_payload = tractor_payload.copy()
        # Different plate, duplicate RC
        dup_payload["tractor_number"] = "RJ-14-TR-8888"
        dup_res1 = await ac.post("/api/v1/tractors", json=dup_payload, headers=admin_headers)
        assert dup_res1.status_code == 409

        # Duplicate plate, different RC
        dup_payload2 = tractor_payload.copy()
        dup_payload2["rc_number"] = "RC-JAIPUR-12345"
        dup_res2 = await ac.post("/api/v1/tractors", json=dup_payload2, headers=admin_headers)
        assert dup_res2.status_code == 409

        # D. TEST: Operator RBAC checks (operator cannot mutate)
        op_create = await ac.post("/api/v1/tractors", json=tractor_payload, headers=operator_headers)
        assert op_create.status_code == 403

        # E. TEST: Read details (Admin & Operator)
        get_res = await ac.get(f"/api/v1/tractors/{tractor_id}", headers=operator_headers)
        assert get_res.status_code == 200
        assert get_res.json()["data"]["tractor_number"] == "RJ-14-TR-9999"

        # F. TEST: Listing, searching & sorting (GET /tractors)
        # Search match plate
        search_res = await ac.get("/api/v1/tractors?q=9999", headers=operator_headers)
        assert search_res.status_code == 200
        assert len(search_res.json()["data"]["items"]) == 1

        # Search no match
        search_res2 = await ac.get("/api/v1/tractors?q=nonexistent", headers=operator_headers)
        assert len(search_res2.json()["data"]["items"]) == 0

        # G. TEST: Update Tractor Details
        update_payload = {
            "owner_name": "Jaipur Fleet Group Modified",
            "remarks": "Fleet operational modified."
        }
        update_res = await ac.put(f"/api/v1/tractors/{tractor_id}", json=update_payload, headers=admin_headers)
        assert update_res.status_code == 200
        assert update_res.json()["data"]["owner_name"] == "Jaipur Fleet Group Modified"
        assert update_res.json()["data"]["remarks"] == "Fleet operational modified."

        # H. TEST: Toggle logical status
        status_res = await ac.patch(f"/api/v1/tractors/{tractor_id}/status?is_active=false", headers=admin_headers)
        assert status_res.status_code == 200
        assert status_res.json()["data"]["is_active"] is False

        # Restore status to active for further checks
        await ac.patch(f"/api/v1/tractors/{tractor_id}/status?is_active=true", headers=admin_headers)

        # I. TEST: Delete check when linked to active Trip
        # Create a mock active trip referencing the tractor
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Fetch first driver, material, party, quarry to build trip reference
                driver_stmt = select(Driver)
                driver_obj = (await session.execute(driver_stmt)).scalars().first()
                if not driver_obj:
                    driver_obj = Driver(
                        name="Mock Driver Test",
                        address="Mines Area",
                        employee_code="DRV-999",
                        license_number="DL-99999",
                        license_expiry=datetime.date.today() + datetime.timedelta(days=100),
                        license_class="Heavy",
                        contact_phone="+91 9999955555",
                        emergency_contact_phone="+91 9999966666",
                        fixed_salary=Decimal("15000"),
                        commission_percentage=Decimal("5"),
                        driver_type="SALARIED",
                        current_status=DriverStatus.AVAILABLE,
                        created_by=uuid.UUID(int=1),
                        updated_by=uuid.UUID(int=1),
                        is_active=True,
                    )
                    session.add(driver_obj)

                party_stmt = select(Party)
                party_obj = (await session.execute(party_stmt)).scalars().first()
                if not party_obj:
                    party_obj = Party(
                        name="Jaipur Minerals",
                        party_type="CUSTOMER",
                        mobile_number="9999900000",
                        address="123 Road, Jaipur",
                        contact_person="Director",
                        opening_balance=Decimal("0.00"),
                        credit_limit=Decimal("50000.00"),
                        created_by=uuid.UUID(int=1),
                        updated_by=uuid.UUID(int=1)
                    )
                    session.add(party_obj)

                quarry_stmt = select(Quarry)
                quarry_obj = (await session.execute(quarry_stmt)).scalars().first()
                if not quarry_obj:
                    quarry_obj = Quarry(
                        name="Rajasthan Quarry-5",
                        location="Jaipur mines",
                        is_third_party=True,
                        created_by=uuid.UUID(int=1),
                        updated_by=uuid.UUID(int=1)
                    )
                    session.add(quarry_obj)

                material_stmt = select(Material)
                material_obj = (await session.execute(material_stmt)).scalars().first()
                if not material_obj:
                    material_obj = Material(
                        name="Crushed Gravel",
                        unit_of_measure="TONS",
                        density_factor=Decimal("1.600"),
                        created_by=uuid.UUID(int=1),
                        updated_by=uuid.UUID(int=1)
                    )
                    session.add(material_obj)

                await session.flush()

                trip = Trip(
                    trip_number="TRIP-998",
                    trip_date=datetime.date.today(),
                    tractor_id=uuid.UUID(tractor_id),
                    driver_id=driver_obj.id,
                    party_id=party_obj.id,
                    source_location="Jaipur",
                    destination_location="Delhi",
                    expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
                    freight_amount=Decimal("25000.00"),
                    advance_amount=Decimal("5000.00"),
                    status=TripStatus.PENDING,
                    is_active=True,
                    created_by=uuid.UUID(int=1),
                    updated_by=uuid.UUID(int=1)
                )
                session.add(trip)

        # Deleting this tractor must return 400 Bad Request
        delete_fail = await ac.delete(f"/api/v1/tractors/{tractor_id}", headers=admin_headers)
        assert delete_fail.status_code == 400

        # J. Clean up mock trip to test successful soft deletion
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await session.execute(delete(Trip))

        delete_success = await ac.delete(f"/api/v1/tractors/{tractor_id}", headers=admin_headers)
        assert delete_success.status_code == 200

        # Check soft-deleted tractor not visible in list
        get_res_deleted = await ac.get(f"/api/v1/tractors/{tractor_id}", headers=admin_headers)
        assert get_res_deleted.status_code == 404
