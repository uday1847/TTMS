from typing import Protocol
import uuid
from app.domain.entities.audit_log import AuditLog

class AuditRepository(Protocol):
    async def create(self, audit: AuditLog) -> AuditLog: ...
    async def list_audit_logs(self, skip: int = 0, limit: int = 100) -> tuple[list[AuditLog], int]: ...
