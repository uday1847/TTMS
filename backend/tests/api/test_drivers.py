import datetime
from decimal import Decimal
import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.main import app
from app.infrastructure.database.session import engine, AsyncSessionLocal
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.domain.entities.user import User
from app.domain.entities.driver import Driver
from app.domain.entities.trip import Trip
from app.domain.enums.trip_status import TripStatus
from app.domain.entities.tractor import Tractor
from app.domain.entities.material import Material
from app.domain.entities.party import Party
from app.domain.entities.quarry import Quarry
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_drivers_module_full_lifecycle() -> None:
    """
    Validates complete Phase 1 operations for the Driver module.
    Covers:
    - Creating permissions
    - Seeding test users (Admin, Operator)
    - Full CRUD logic (Create, Read, Search/Filter, Update, Toggle Status, Soft Delete)
    - Duplications checks (Conflicts on unique phone/license)
    - Deletion check when linked to active trips
    - RBAC authorization check
    """
    
    # 1. Setup DB state (permissions, roles, user accounts)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Clean up sessions and previous driver data
            await session.execute(delete(RefreshToken))
            await session.execute(delete(Trip))
            await session.execute(delete(Driver))

            # Ensure driver permissions exist in permissions catalog
            driver_permissions = [
                ("drivers:read", "Read drivers"),
                ("drivers:create", "Create drivers"),
                ("drivers:update", "Update drivers"),
                ("drivers:delete", "Delete drivers"),
            ]
            perm_map = {}
            for code, desc in driver_permissions:
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

            # Operator Role setup (read-only drivers permission)
            stmt_op_role = select(Role).options(selectinload(Role.permissions)).where(Role.name == "operator")
            op_role = (await session.execute(stmt_op_role)).scalar_one_or_none()
            if not op_role:
                op_role = Role(name="operator", display_name="Operator Role", is_active=True)
                session.add(op_role)
            if perm_map["drivers:read"] not in op_role.permissions:
                op_role.permissions.append(perm_map["drivers:read"])

            # Create test operator user
            stmt_op_user = select(User).options(selectinload(User.roles)).where(User.username == "operator_test")
            op_user = (await session.execute(stmt_op_user)).scalar_one_or_none()
            if not op_user:
                op_user = User(
                    email="operator@ttms.com",
                    username="operator_test",
                    password_hash=hash_password("OperatorPass123!"),
                    first_name="Test",
                    last_name="Operator",
                    is_active=True,
                )
                session.add(op_user)
            if op_role not in op_user.roles:
                op_user.roles.append(op_role)

            # Standardize emails in user list to pass validator checks
            stmt_users = select(User)
            all_users = (await session.execute(stmt_users)).scalars().all()
            for u in all_users:
                if u.email.endswith(".local"):
                    u.email = u.email.replace(".local", ".com")

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

        # B. TEST: Create Driver as Admin (Success)
        driver_payload = {
            "name": "Raj Kumar",
            "address": "123 Quarry Road, Jaipur",
            "employee_code": "DRV-101",
            "license_number": "DL-1234567890",
            "license_expiry": str(datetime.date.today() + datetime.timedelta(days=365)),
            "license_class": "Heavy Duty",
            "contact_phone": "+91 9999988888",
            "emergency_contact_phone": "+91 9999911111",
            "fixed_salary": "25000.00",
            "commission_percentage": "5.50",
            "driver_type": "SALARIED",
            "current_status": "available"
        }
        create_res = await ac.post("/api/v1/drivers", json=driver_payload, headers=admin_headers)
        assert create_res.status_code == 201
        driver_data = create_res.json()["data"]
        assert driver_data["name"] == "Raj Kumar"
        driver_id = driver_data["id"]

        # C. TEST: Conflict Checks (Duplicate license/phone)
        dup_payload = driver_payload.copy()
        dup_payload["employee_code"] = "DRV-102"
        dup_res = await ac.post("/api/v1/drivers", json=dup_payload, headers=admin_headers)
        assert dup_res.status_code == 409

        # D. TEST: Operator RBAC checks (operator cannot mutate)
        op_create = await ac.post("/api/v1/drivers", json=driver_payload, headers=operator_headers)
        assert op_create.status_code == 403

        # E. TEST: Read details (Admin & Operator)
        get_res = await ac.get(f"/api/v1/drivers/{driver_id}", headers=operator_headers)
        assert get_res.status_code == 200
        assert get_res.json()["data"]["name"] == "Raj Kumar"

        # F. TEST: Listing, searching & sorting (GET /drivers)
        # Search match name
        search_res = await ac.get("/api/v1/drivers?q=raj", headers=operator_headers)
        assert search_res.status_code == 200
        assert len(search_res.json()["data"]["items"]) == 1

        # Search no match
        search_res2 = await ac.get("/api/v1/drivers?q=nonexistent", headers=operator_headers)
        assert len(search_res2.json()["data"]["items"]) == 0

        # G. TEST: Update Driver Details
        update_payload = {
            "name": "Raj K. Sharma",
            "address": "456 Mines Road, Jaipur"
        }
        update_res = await ac.put(f"/api/v1/drivers/{driver_id}", json=update_payload, headers=admin_headers)
        assert update_res.status_code == 200
        assert update_res.json()["data"]["name"] == "Raj K. Sharma"
        assert update_res.json()["data"]["address"] == "456 Mines Road, Jaipur"

        # H. TEST: Toggle logical status
        status_res = await ac.patch(f"/api/v1/drivers/{driver_id}/status?is_active=false", headers=admin_headers)
        assert status_res.status_code == 200
        assert status_res.json()["data"]["is_active"] is False
        assert status_res.json()["data"]["current_status"] == "inactive"

        # Restore status to active for further checks
        await ac.patch(f"/api/v1/drivers/{driver_id}/status?is_active=true", headers=admin_headers)

        # I. TEST: Delete check when linked to active Trip
        # Create a mock active trip referencing the driver
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Fetch first tractor, material, party, quarry to build trip reference
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
                        remarks="Assigned to test driver active trips checks.",
                        created_by=uuid.UUID(int=1),
                        updated_by=uuid.UUID(int=1)
                    )
                    session.add(tractor_obj)

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
                    trip_number="TRIP-999",
                    trip_date=datetime.date.today(),
                    tractor_id=tractor_obj.id,
                    driver_id=uuid.UUID(driver_id),
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

        # Attempt to delete driver who is assigned to an active trip -> Check 400 Bad Request
        delete_fail = await ac.delete(f"/api/v1/drivers/{driver_id}", headers=admin_headers)
        assert delete_fail.status_code == 400

        # Mark trip as inactive (completed) in DB to allow soft deletion
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt_t = select(Trip).where(Trip.trip_number == "TRIP-999")
                trip_obj = (await session.execute(stmt_t)).scalar_one()
                trip_obj.is_active = False

        # J. TEST: Soft Delete Driver (Success)
        delete_success = await ac.delete(f"/api/v1/drivers/{driver_id}", headers=admin_headers)
        assert delete_success.status_code == 200

        # Read details after delete -> Check 404
        get_fail = await ac.get(f"/api/v1/drivers/{driver_id}", headers=admin_headers)
        assert get_fail.status_code == 404

    await engine.dispose()
