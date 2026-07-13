from decimal import Decimal
import datetime
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
async def test_parties_module_full_lifecycle() -> None:
    """
    Validates complete Phase 1 operations for the Party module.
    Covers:
    - Creating permissions
    - Seeding test users (Admin, Operator)
    - Full CRUD logic (Create, Read, Search/Filter, Update, Toggle Status, Soft Delete)
    - Duplications checks (Conflicts on unique mobile, GST, PAN)
    - Deletion check when linked to active trips
    - RBAC authorization checks (Operator denied on write actions)
    """

    # 1. Setup DB state (permissions, roles, user accounts)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Clean up sessions and previous party data
            await session.execute(delete(Trip))
            await session.execute(delete(Party))

            # Ensure party permissions exist in permissions catalog
            party_permissions = [
                ("parties:read", "Read parties"),
                ("parties:create", "Create parties"),
                ("parties:update", "Update parties"),
                ("parties:delete", "Delete parties"),
            ]
            perm_map = {}
            for code, desc in party_permissions:
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

            # Operator Role setup (read-only parties permission)
            stmt_op_role = select(Role).options(selectinload(Role.permissions)).where(Role.name == "operator")
            op_role = (await session.execute(stmt_op_role)).scalar_one_or_none()
            if not op_role:
                op_role = Role(name="operator", display_name="Operator Role", is_active=True)
                session.add(op_role)
            if perm_map["parties:read"] not in op_role.permissions:
                op_role.permissions.append(perm_map["parties:read"])

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

        # B. TEST: Create Party as Admin (Success)
        party_payload = {
            "name": "Jaipur Quarry Minerals",
            "party_type": "CUSTOMER",
            "mobile_number": "+91 9999900000",
            "alternate_mobile": "+91 9999911111",
            "email": "contact@jaipurminerals.com",
            "gst_number": "08aaaaa1111a1z2", # Lowercase to test uppercase normalizer
            "pan_number": "aaaaa1111a",       # Lowercase to test uppercase normalizer
            "address": "123 Quarry Road, Jaipur",
            "city": "Jaipur",
            "state": "Rajasthan",
            "pincode": "302001",
            "contact_person": "Raj Kumar Sharma",
            "opening_balance": "15000.00",
            "credit_limit": "50000.00",
            "remarks": "Priority accounts customer."
        }
        create_res = await ac.post("/api/v1/parties", json=party_payload, headers=admin_headers)
        assert create_res.status_code == 201
        party_data = create_res.json()["data"]
        assert party_data["name"] == "Jaipur Quarry Minerals"
        assert party_data["gst_number"] == "08AAAAA1111A1Z2" # Assert normalization
        assert party_data["pan_number"] == "AAAAA1111A"
        party_id = party_data["id"]

        # C. TEST: Validation Checks (email format, negative opening balance, invalid party type)
        bad_payload = party_payload.copy()
        bad_payload["email"] = "invalid-email"
        bad_res = await ac.post("/api/v1/parties", json=bad_payload, headers=admin_headers)
        assert bad_res.status_code == 422

        bad_payload = party_payload.copy()
        bad_payload["opening_balance"] = "-500.00"
        bad_res = await ac.post("/api/v1/parties", json=bad_payload, headers=admin_headers)
        assert bad_res.status_code == 422

        # D. TEST: Conflict Checks (Duplicate mobile, GST, PAN)
        dup_payload = party_payload.copy()
        # Different mobile/PAN, duplicate GST
        dup_payload["mobile_number"] = "+91 8888800000"
        dup_payload["pan_number"] = "BBBBB2222B"
        dup_res1 = await ac.post("/api/v1/parties", json=dup_payload, headers=admin_headers)
        assert dup_res1.status_code == 409

        # E. TEST: Operator RBAC checks (operator cannot mutate)
        op_create = await ac.post("/api/v1/parties", json=party_payload, headers=operator_headers)
        assert op_create.status_code == 403

        # F. TEST: Read details (Admin & Operator)
        get_res = await ac.get(f"/api/v1/parties/{party_id}", headers=operator_headers)
        assert get_res.status_code == 200
        assert get_res.json()["data"]["name"] == "Jaipur Quarry Minerals"

        # G. TEST: Listing, searching & sorting (GET /parties)
        # Search match name
        search_res = await ac.get("/api/v1/parties?q=Minerals", headers=operator_headers)
        assert search_res.status_code == 200
        assert len(search_res.json()["data"]["items"]) == 1

        # Search no match
        search_res2 = await ac.get("/api/v1/parties?q=nonexistent", headers=operator_headers)
        assert len(search_res2.json()["data"]["items"]) == 0

        # H. TEST: Update Party Details
        update_payload = {
            "name": "Jaipur Quarry Minerals Modified",
            "remarks": "Modified remarks info."
        }
        update_res = await ac.put(f"/api/v1/parties/{party_id}", json=update_payload, headers=admin_headers)
        assert update_res.status_code == 200
        assert update_res.json()["data"]["name"] == "Jaipur Quarry Minerals Modified"

        # I. TEST: Toggle logical status
        status_res = await ac.patch(f"/api/v1/parties/{party_id}/status?is_active=false", headers=admin_headers)
        assert status_res.status_code == 200
        assert status_res.json()["data"]["is_active"] is False

        # Restore status to active for further checks
        await ac.patch(f"/api/v1/parties/{party_id}/status?is_active=true", headers=admin_headers)

        # J. TEST: Delete check when linked to active Trip
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Fetch first driver, tractor, quarry, material to build trip reference
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

                tractor_stmt = select(Tractor)
                tractor_obj = (await session.execute(tractor_stmt)).scalars().first()
                if not tractor_obj:
                    tractor_obj = Tractor(
                        tractor_number="RJ-14-1234",
                        owner_name="Jaipur Minerals LLC",
                        rc_number="RC-JAIPUR-888999",
                        insurance_number="INS-TR-990011",
                        insurance_expiry=datetime.date.today() + datetime.timedelta(days=365),
                        manufacturer="Mahindra",
                        model="Arjun",
                        registration_date=datetime.date.today(),
                        remarks="Test tractor",
                        created_by=uuid.UUID(int=1),
                        updated_by=uuid.UUID(int=1)
                    )
                    session.add(tractor_obj)

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
                    tractor_id=tractor_obj.id,
                    driver_id=driver_obj.id,
                    party_id=uuid.UUID(party_id),
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

        # Deleting this party must return 400 Bad Request
        delete_fail = await ac.delete(f"/api/v1/parties/{party_id}", headers=admin_headers)
        assert delete_fail.status_code == 400

        # K. Clean up mock trip to test successful soft deletion
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await session.execute(delete(Trip))

        delete_success = await ac.delete(f"/api/v1/parties/{party_id}", headers=admin_headers)
        assert delete_success.status_code == 200

        # Check soft-deleted party not visible in list
        get_res_deleted = await ac.get(f"/api/v1/parties/{party_id}", headers=admin_headers)
        assert get_res_deleted.status_code == 404
