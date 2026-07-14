from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.dependencies.db import get_session
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.domain.entities.user import User
from app.infrastructure.repositories.audit_repository import SQLAlchemyAuditRepository
from app.application.dtos.audit import AuditResponse

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("", response_model=list[AuditResponse], dependencies=[Depends(PermissionChecker("audit:read"))])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    repo = SQLAlchemyAuditRepository(db)
    items, _ = await repo.list_audit_logs(skip, limit)
    return items
