import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.audit_service import AuditService
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.permission_module import PermissionModule
from app.domain.entities.audit_log import AuditLog

@pytest.fixture
def mock_audit_repository():
    return AsyncMock()

@pytest.fixture
def audit_service(mock_audit_repository):
    return AuditService(mock_audit_repository)

@pytest.mark.asyncio
async def test_log_action_login(audit_service, mock_audit_repository):
    user_id = uuid.uuid4()
    record_id = uuid.uuid4()
    
    await audit_service.log_action(
        action=AuditAction.LOGIN,
        module=PermissionModule.AUTH,
        table_name="users",
        record_id=record_id,
        user_id=user_id,
        ip_address="127.0.0.1",
        user_agent="pytest"
    )
    
    mock_audit_repository.create.assert_called_once()
    args, _ = mock_audit_repository.create.call_args
    created_audit: AuditLog = args[0]
    
    assert created_audit.action == AuditAction.LOGIN
    assert created_audit.module == PermissionModule.AUTH
    assert created_audit.table_name == "users"
    assert created_audit.record_id == record_id
    assert created_audit.user_id == user_id
    assert created_audit.ip_address == "127.0.0.1"
    assert created_audit.user_agent == "pytest"

@pytest.mark.asyncio
async def test_log_action_crud(audit_service, mock_audit_repository):
    user_id = uuid.uuid4()
    record_id = uuid.uuid4()
    
    old_values = {"status": "ACTIVE"}
    new_values = {"status": "INACTIVE"}
    
    await audit_service.log_action(
        action=AuditAction.UPDATE,
        module=PermissionModule.USERS,
        table_name="users",
        record_id=record_id,
        old_values=old_values,
        new_values=new_values,
        user_id=user_id
    )
    
    mock_audit_repository.create.assert_called_once()
    args, _ = mock_audit_repository.create.call_args
    created_audit: AuditLog = args[0]
    
    assert created_audit.action == AuditAction.UPDATE
    assert created_audit.module == PermissionModule.USERS
    assert created_audit.old_values == old_values
    assert created_audit.new_values == new_values

@pytest.mark.asyncio
async def test_log_action_permission_change(audit_service, mock_audit_repository):
    user_id = uuid.uuid4()
    record_id = uuid.uuid4()
    
    await audit_service.log_action(
        action=AuditAction.PERMISSION_CHANGE,
        module=PermissionModule.ROLES,
        table_name="roles",
        record_id=record_id,
        new_values={"permissions": ["auth:read"]},
        user_id=user_id
    )
    
    mock_audit_repository.create.assert_called_once()
    args, _ = mock_audit_repository.create.call_args
    created_audit: AuditLog = args[0]
    
    assert created_audit.action == AuditAction.PERMISSION_CHANGE
    assert created_audit.module == PermissionModule.ROLES
