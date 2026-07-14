from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.dependencies.db import get_session
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.domain.entities.user import User
from app.infrastructure.repositories.login_history_repository import SQLAlchemyLoginHistoryRepository
from app.application.dtos.audit import LoginHistoryResponse

router = APIRouter(prefix="/login-history", tags=["Login History"])

@router.get("", response_model=list[LoginHistoryResponse], dependencies=[Depends(PermissionChecker("auth:read"))])
async def get_login_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    repo = SQLAlchemyLoginHistoryRepository(db)
    items, _ = await repo.list_by_user(current_user.id, skip, limit)
    return items
