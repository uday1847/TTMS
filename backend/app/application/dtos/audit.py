import uuid
from typing import Any
from datetime import datetime
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.permission_module import PermissionModule
from app.domain.enums.login_result import LoginResult
from app.domain.enums.session_status import SessionStatus
from app.application.dtos.base import BaseDTO

class AuditResponse(BaseDTO):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: AuditAction
    module: PermissionModule
    table_name: str
    record_id: uuid.UUID
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime

class LoginHistoryResponse(BaseDTO):
    id: uuid.UUID
    user_id: uuid.UUID
    ip_address: str | None
    browser: str | None
    os: str | None
    platform: str | None
    result: LoginResult
    failure_reason: str | None
    created_at: datetime

class SessionResponse(BaseDTO):
    id: uuid.UUID
    user_id: uuid.UUID
    device_fingerprint: str | None
    ip_address: str | None
    user_agent: str | None
    status: SessionStatus
    expires_at: datetime
    created_at: datetime
