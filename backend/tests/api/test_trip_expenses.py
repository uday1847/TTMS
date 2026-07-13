import datetime
from decimal import Decimal
import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.main import app
from app.infrastructure.database.session import AsyncSessionLocal
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.domain.entities.trip_expense import TripExpense
from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.entities.trip_status_history import TripStatusHistory
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.payment_mode import PaymentMode
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.driver_status import DriverStatus
from app.core.security import hash_password


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db_api():
    # Clean tables before and after testing
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(delete(TripExpense))
            await session.execute(delete(TripStatusHistory))
            await session.execute(delete(Trip))
            await session.execute(delete(Driver))
            await session.execute(delete(Tractor))
            await session.execute(delete(Party))
            await session.execute(delete(User).where(User.username.in_(["admin-exp", "oper-exp"])))
    yield
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(delete(TripExpense))
            await session.execute(delete(TripStatusHistory))
            await session.execute(delete(Trip))
            await session.execute(delete(Driver))
            await session.execute(delete(Tractor))
            await session.execute(delete(Party))
            await session.execute(delete(User).where(User.username.in_(["admin-exp", "oper-exp"])))


@pytest.mark.asyncio
async def test_trip_expense_api_lifecycle() -> None:
    # 1. Setup Admin, Operator accounts, Driver, Tractor, Party, Trip
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Setup permissions/roles
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
                email="admin-exp@example.com",
                username="admin-exp",
                password_hash=hash_password("adminpass"),
                first_name="Admin",
                last_name="Tester",
                is_active=True
            )
            admin_user.roles.extend(admin_roles)
            session.add(admin_user)

            operator_user = User(
                id=uuid.uuid4(),
                email="oper-exp@example.com",
                username="oper-exp",
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
                employee_code="DRV-EXP-API",
                name="James Bond",
                license_number="DL-EXP-API",
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
                tractor_number="GJ01-EXP-API",
                owner_name="Company Fleet",
                rc_number="RC-GJ-EXP-API",
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

            trip = Trip(
                id=uuid.uuid4(),
                trip_number="TRIP-2026-EXP-API",
                party_id=party.id,
                tractor_id=tractor.id,
                driver_id=driver.id,
                source_location="Mundra Port",
                destination_location="Surat Refinery",
                trip_date=datetime.date.today(),
                expected_delivery_date=datetime.date.today() + datetime.timedelta(days=2),
                freight_amount=Decimal("50000.00"),
                advance_amount=Decimal("10000.00"),
                status=TripStatus.DISPATCHED,
                is_active=True,
            )
            session.add(trip)

            await session.flush()
            trip_id = trip.id
            party_id = party.id

    # 2. Login to get JWT headers
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        admin_login = await ac.post("/api/v1/auth/login", json={"username_or_email": "admin-exp", "password": "adminpass"})
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        oper_login = await ac.post("/api/v1/auth/login", json={"username_or_email": "oper-exp", "password": "operpass"})
        assert oper_login.status_code == 200
        oper_token = oper_login.json()["data"]["access_token"]
        oper_headers = {"Authorization": f"Bearer {oper_token}"}

        # A. CREATE TRIP EXPENSE (Operator unauthorized block)
        payload = {
            "trip_id": str(trip_id),
            "party_id": str(party_id),
            "paid_to_name": "IOCL Pumpmundra",
            "expense_type": "DIESEL",
            "expense_date": str(datetime.date.today()),
            "amount": "15000.00",
            "payment_mode": "UPI",
            "payment_status": "PAID",
            "reference_number": "REF-987",
            "remarks": "Diesel for initial segment",
            "attachment_path": "/uploads/expenses/hp_bill.jpg",
            "attachment_name": "hp_bill.jpg",
            "attachment_size": 102400,
            "attachment_content_type": "image/jpeg"
        }
        oper_create = await ac.post("/api/v1/trip-expenses", json=payload, headers=oper_headers)
        assert oper_create.status_code == 403

        # B. CREATE TRIP EXPENSE (Admin success)
        admin_create = await ac.post("/api/v1/trip-expenses", json=payload, headers=admin_headers)
        assert admin_create.status_code == 201
        expense_data = admin_create.json()["data"]
        expense_id = expense_data["id"]
        assert expense_data["expense_number"].startswith("EXP-202")
        assert expense_data["paid_to_name"] == "IOCL Pumpmundra"

        # C. GET TRIP EXPENSE DETAIL
        detail_get = await ac.get(f"/api/v1/trip-expenses/{expense_id}", headers=admin_headers)
        assert detail_get.status_code == 200
        assert detail_get.json()["data"]["amount"] == "15000.00"

        # D. LIST TRIP EXPENSES (With query filters)
        list_get = await ac.get(f"/api/v1/trip-expenses?trip_id={trip_id}&expense_type=DIESEL", headers=admin_headers)
        assert list_get.status_code == 200
        assert list_get.json()["data"]["total"] == 1

        # E. UPDATE TRIP EXPENSE
        update_payload = {"amount": "16500.00", "remarks": "Diesel amount revised upwards."}
        update_put = await ac.put(f"/api/v1/trip-expenses/{expense_id}", json=update_payload, headers=admin_headers)
        assert update_put.status_code == 200
        assert update_put.json()["data"]["amount"] == "16500.00"
        assert update_put.json()["data"]["remarks"] == "Diesel amount revised upwards."

        # F. GET TRIP EXPENSE SUMMARY
        summary_get = await ac.get(f"/api/v1/trips/{trip_id}/expense-summary", headers=admin_headers)
        assert summary_get.status_code == 200
        assert summary_get.json()["data"]["expenses"] == "16500.00"
        assert summary_get.json()["data"]["profit"] == "33500.00"
        assert len(summary_get.json()["data"]["expense_breakdown"]) == 1

        # G. GET TRIP PROFIT DETAILS
        profit_get = await ac.get(f"/api/v1/trips/{trip_id}/profit", headers=admin_headers)
        assert profit_get.status_code == 200
        assert profit_get.json()["data"]["net_profit"] == "33500.00"
        assert profit_get.json()["data"]["profit_percentage"] == "67.00"

        # H. GET TRIP DASHBOARD CONTEXT AGGREGATOR
        dashboard_get = await ac.get(f"/api/v1/trips/{trip_id}/dashboard", headers=admin_headers)
        assert dashboard_get.status_code == 200
        db_data = dashboard_get.json()["data"]
        assert db_data["trip_number"] == "TRIP-2026-EXP-API"
        assert db_data["freight"] == "50000.00"
        assert db_data["expenses"] == "16500.00"
        assert db_data["remaining_profit"] == "23500.00" # freight - expenses - advance (50000 - 16500 - 10000 = 23500)
        assert len(db_data["expenses_list"]) == 1

        # I. DELETE TRIP EXPENSE
        delete_del = await ac.delete(f"/api/v1/trip-expenses/{expense_id}", headers=admin_headers)
        assert delete_del.status_code == 200
        assert delete_del.json()["data"]["is_active"] is False

        # J. CONFIRM DELETED IN SUMMARY
        summary_get2 = await ac.get(f"/api/v1/trips/{trip_id}/expense-summary", headers=admin_headers)
        assert summary_get2.status_code == 200
        assert summary_get2.json()["data"]["expenses"] == "0.00"
