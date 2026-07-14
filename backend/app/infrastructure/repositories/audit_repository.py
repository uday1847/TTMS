from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.audit_repository import AuditRepository

class SQLAlchemyAuditRepository(AuditRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, audit: AuditLog) -> AuditLog:
        self.session.add(audit)
        await self.session.flush()
        return audit

    async def list_audit_logs(self, skip: int = 0, limit: int = 100) -> tuple[list[AuditLog], int]:
        stmt_count = select(func.count(AuditLog.id))
        total = (await self.session.execute(stmt_count)).scalar_one()

        stmt_items = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list((await self.session.execute(stmt_items)).scalars().all())
        
        return items, total
