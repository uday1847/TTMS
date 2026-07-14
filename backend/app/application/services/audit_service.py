import uuid
from typing import Any

from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.audit_repository import AuditRepository
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.permission_module import PermissionModule

class AuditService:
    def __init__(self, audit_repository: AuditRepository):
        self.audit_repository = audit_repository

    async def log_action(
        self,
        action: AuditAction,
        module: PermissionModule,
        table_name: str,
        record_id: uuid.UUID,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> None:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            module=module,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repository.create(audit)
