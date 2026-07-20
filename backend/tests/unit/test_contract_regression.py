import pytest
from pydantic import ConfigDict, Field
from datetime import datetime, timezone
import json
from app.application.dtos.base import BaseDTO
from enum import Enum

class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class DummyDTO(BaseDTO):
    first_name: str
    last_name: str
    is_active: bool = True
    status: StatusEnum = StatusEnum.ACTIVE
    created_at: datetime | None = None

def test_base_dto_camel_case_serialization():
    dt = datetime(2026, 7, 19, 10, 20, 11, tzinfo=timezone.utc)
    dto = DummyDTO(
        first_name="John",
        last_name="Doe",
        is_active=False,
        status=StatusEnum.INACTIVE,
        created_at=dt
    )
    
    # Dump to JSON
    json_str = dto.model_dump_json(by_alias=True)
    data = json.loads(json_str)
    
    # Verify camelCase keys are generated
    assert "firstName" in data
    assert "lastName" in data
    assert "isActive" in data
    assert "createdAt" in data
    
    # Verify no snake_case keys are present
    assert "first_name" not in data
    
    # Verify values
    assert data["firstName"] == "John"
    assert data["isActive"] is False
    assert data["status"] == "INACTIVE"

def test_base_dto_camel_case_deserialization():
    payload = {
        "firstName": "Jane",
        "lastName": "Smith",
        "isActive": True,
        "status": "ACTIVE",
        "createdAt": "2026-07-19T10:20:11Z"
    }
    
    dto = DummyDTO.model_validate(payload)
    
    # Verify properties are mapped back to snake_case attributes
    assert dto.first_name == "Jane"
    assert dto.last_name == "Smith"
    assert dto.is_active is True
    assert dto.status == StatusEnum.ACTIVE
    assert dto.created_at is not None

def test_base_dto_snake_case_deserialization_fallback():
    # Because populate_by_name=True is set, we can still accept snake_case in python land
    payload = {
        "first_name": "Bob",
        "last_name": "Ross"
    }
    
    dto = DummyDTO.model_validate(payload)
    
    assert dto.first_name == "Bob"
    assert dto.last_name == "Ross"

from app.application.dtos.users import UserUpdate

def test_update_user_accepts_frontend_payload():
    payload = {
        "firstName": "Updated",
        "isActive": True
    }
    
    dto = UserUpdate(**payload)
    
    assert dto.first_name == "Updated"
    assert dto.is_active is True

from app.application.dtos.users import UserResponse
from app.domain.enums.user_status import UserStatus
import uuid
from datetime import datetime, timezone

def test_user_response_serializes_to_camel_case():
    dto = UserResponse(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        first_name="Uday",
        last_name="Zala",
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc)
    )

    data = dto.model_dump(by_alias=True)

    assert data["firstName"] == "Uday"
    assert data["lastName"] == "Zala"
    assert "first_name" not in data


from app.application.dtos.driver import DriverResponse
from app.domain.enums.driver_status import DriverStatus

def test_driver_response_openapi_schema_uses_camel_case():
    from app.main import app

    schema = app.openapi()
    driver_schema = schema["components"]["schemas"]["DriverResponse"]

    props = driver_schema["properties"]

    assert "licenseNumber" in props
    assert "employeeCode" in props
    assert "license_number" not in props
    assert "employee_code" not in props

from decimal import Decimal

def test_driver_response_serializes_timezone_aware_datetimes():
    dto = DriverResponse(
        id=uuid.uuid4(),
        name="Uday Zala",
        employee_code="DRV-001",
        license_number="GJ01-1234",
        license_expiry=datetime(2030, 1, 1).date(),
        license_class="LMV",
        contact_phone="+91 9999999999",
        fixed_salary=Decimal("1000.00"),
        commission_percentage=Decimal("0.0"),
        driver_type="SALARIED",
        is_active=True,
        current_status=DriverStatus.AVAILABLE,
        created_at=datetime.now(timezone.utc),
        version_id=1,
    )

    data = dto.model_dump(mode="json", by_alias=True)

    assert "createdAt" in data
    # Ensure it ends with +00:00 or Z to denote UTC awareness
    assert data["createdAt"].endswith("+00:00") or data["createdAt"].endswith("Z")

