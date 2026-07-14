from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_user, PermissionChecker
from app.domain.entities.user import User
from app.infrastructure.repositories.login_history_repository import SQLAlchemyLoginHistoryRepository
from app.application.dtos.audit import LoginHistoryResponse

router = APIRouter(prefix="/login-history", tags=["Login History"])

@router.get("", response_model=list[LoginHistoryResponse], dependencies=[Depends(PermissionChecker("auth:read"))])
async def get_login_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    repo = SQLAlchemyLoginHistoryRepository(db)
    items, _ = await repo.list_by_user(current_user.id, skip, limit)
    return items
