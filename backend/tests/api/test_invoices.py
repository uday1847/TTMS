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
from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_status_history import InvoiceStatusHistory
from app.domain.entities.trip import Trip
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.enums.invoice_status import InvoiceStatus
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.driver_status import DriverStatus
from app.core.security import hash_password


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db_invoice_api():
    # Clean tables before and after testing
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(delete(InvoiceStatusHistory))
            await session.execute(delete(Invoice))
            await session.execute(delete(Trip))
            await session.execute(delete(Driver))
            await session.execute(delete(Tractor))
            await session.execute(delete(Party))
            await session.execute(delete(User).where(User.username.in_(["admin-inv", "oper-inv"])))
    yield
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(delete(InvoiceStatusHistory))
            await session.execute(delete(Invoice))
            await session.execute(delete(Trip))
            await session.execute(delete(Driver))
            await session.execute(delete(Tractor))
            await session.execute(delete(Party))
            await session.execute(delete(User).where(User.username.in_(["admin-inv", "oper-inv"])))


@pytest.mark.asyncio
async def test_invoice_api_lifecycle() -> None:
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
                email="admin-inv@example.com",
                username="admin-inv",
                password_hash=hash_password("adminpass"),
                first_name="Admin",
                last_name="Tester",
                is_active=True
            )
            admin_user.roles.extend(admin_roles)
            session.add(admin_user)

            operator_user = User(
                id=uuid.uuid4(),
                email="oper-inv@example.com",
                username="oper-inv",
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
                employee_code="DRV-INV-API",
                name="James Bond",
                license_number="DL-INV-API",
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
                tractor_number="GJ01-INV-API",
                owner_name="Company Fleet",
                rc_number="RC-GJ-INV-API",
                insurance_expiry=datetime.date.today() + datetime.timedelta(days=100),
                is_active=True
            )
            session.add(tractor)

            party = Party(
                id=uuid.uuid4(),
                name="Reliance Petroleum",
                party_type="Customer",
                mobile_number="9876543210",
                is_active=True
            )
            session.add(party)

            trip = Trip(
                id=uuid.uuid4(),
                trip_number="TRIP-2026-INV-API",
                party_id=party.id,
                tractor_id=tractor.id,
                driver_id=driver.id,
                source_location="Mundra Port",
                destination_location="Surat Refinery",
                trip_date=datetime.date.today() - datetime.timedelta(days=3),
                expected_delivery_date=datetime.date.today() - datetime.timedelta(days=1),
                actual_delivery_date=datetime.date.today() - datetime.timedelta(days=1),
                freight_amount=Decimal("50000.00"),
                advance_amount=Decimal("10000.00"),
                status=TripStatus.COMPLETED,
                is_active=True,
            )
            session.add(trip)

            await session.flush()
            trip_id = trip.id
            party_id = party.id

    # 2. Login to get JWT headers
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        admin_login = await ac.post("/api/v1/auth/login", json={"username_or_email": "admin-inv", "password": "adminpass"})
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        oper_login = await ac.post("/api/v1/auth/login", json={"username_or_email": "oper-inv", "password": "operpass"})
        assert oper_login.status_code == 200
        oper_token = oper_login.json()["data"]["access_token"]
        oper_headers = {"Authorization": f"Bearer {oper_token}"}

        # A. CREATE INVOICE (Operator unauthorized block)
        payload = {
            "trip_id": str(trip_id),
            "invoice_date": str(datetime.date.today()),
            "due_date": str(datetime.date.today() + datetime.timedelta(days=15)),
            "remarks": "API testing first invoice draft."
        }
        oper_create = await ac.post("/api/v1/invoices", json=payload, headers=oper_headers)
        assert oper_create.status_code == 403

        # B. CREATE INVOICE (Admin success)
        admin_create = await ac.post("/api/v1/invoices", json=payload, headers=admin_headers)
        assert admin_create.status_code == 201
        invoice_data = admin_create.json()["data"]
        invoice_id = invoice_data["id"]
        assert invoice_data["invoice_number"].startswith("INV-202")
        assert invoice_data["gross_amount"] == "50000.00"
        assert invoice_data["status"] == "DRAFT"

        # C. GET INVOICE DETAIL
        detail_get = await ac.get(f"/api/v1/invoices/{invoice_id}", headers=admin_headers)
        assert detail_get.status_code == 200
        assert detail_get.json()["data"]["gross_amount"] == "50000.00"
        assert detail_get.json()["data"]["party_name"] == "Reliance Petroleum"

        # D. LIST INVOICES (With query filters)
        list_get = await ac.get(f"/api/v1/invoices?trip_id={trip_id}&status=DRAFT", headers=admin_headers)
        assert list_get.status_code == 200
        assert list_get.json()["data"]["total"] == 1

        # E. UPDATE INVOICE REMARKS
        update_payload = {"remarks": "Revised draft remarks."}
        update_put = await ac.put(f"/api/v1/invoices/{invoice_id}", json=update_payload, headers=admin_headers)
        assert update_put.status_code == 200
        assert update_put.json()["data"]["remarks"] == "Revised draft remarks."

        # F. TRANSITION STATUS TO ISSUED
        status_payload = {"status": "ISSUED", "remarks": "Mailed to client."}
        status_patch = await ac.patch(f"/api/v1/invoices/{invoice_id}/status", json=status_payload, headers=admin_headers)
        assert status_patch.status_code == 200
        assert status_patch.json()["data"]["status"] == "ISSUED"

        # G. RECORD PAYMENT Receipt (PARTIALLY_PAID check)
        pay_post = await ac.post(f"/api/v1/invoices/{invoice_id}/payments?amount=20000.00&remarks=First+cheque+receipt", headers=admin_headers)
        assert pay_post.status_code == 200
        pay_data = pay_post.json()["data"]
        assert pay_data["received_amount"] == "20000.00"
        assert pay_data["balance_amount"] == "30000.00"
        assert pay_data["status"] == "PARTIALLY_PAID"

        # H. GET DASHBOARD RECEIVABLES
        dash_get = await ac.get("/api/v1/invoices/dashboard", headers=admin_headers)
        assert dash_get.status_code == 200
        dash_data = dash_get.json()["data"]
        assert dash_data["total_revenue"] == "50000.00"
        assert dash_data["total_collected"] == "20000.00"
        assert dash_data["total_outstanding"] == "30000.00"

        # I. GET STATUS HISTORY logs
        hist_get = await ac.get(f"/api/v1/invoices/{invoice_id}/history", headers=admin_headers)
        assert hist_get.status_code == 200
        hist_list = hist_get.json()["data"]
        # History tracks: DRAFT creation log, transition to ISSUED, transition to PARTIALLY_PAID payment
        assert len(hist_list) == 3
        assert hist_list[0]["new_status"] == "DRAFT"
        assert hist_list[1]["new_status"] == "ISSUED"
        assert hist_list[2]["new_status"] == "PARTIALLY_PAID"

        # J. BLOCK DELETION since it is partially paid
        del_delete = await ac.delete(f"/api/v1/invoices/{invoice_id}", headers=admin_headers)
        assert del_delete.status_code == 400
        assert "Only invoices in DRAFT status can be deleted" in del_delete.json()["message"]
