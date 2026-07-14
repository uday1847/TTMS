from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.dependencies.db import get_session
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.domain.entities.user import User
from app.application.services.session_service import SessionService
from app.infrastructure.repositories.session_repository import SQLAlchemySessionRepository
from app.application.dtos.audit import SessionResponse

router = APIRouter(prefix="/sessions", tags=["Sessions"])

def get_session_service(db: AsyncSession = Depends(get_session)) -> SessionService:
    return SessionService(SQLAlchemySessionRepository(db))

@router.get("", response_model=list[SessionResponse], dependencies=[Depends(PermissionChecker("auth:read"))])
async def get_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    repo = SQLAlchemySessionRepository(db)
    items = await repo.list_by_user(current_user.id)
    return items

@router.delete("/{session_id}", dependencies=[Depends(PermissionChecker("auth:update"))])
async def revoke_session(
    session_id: uuid.UUID,
    service: SessionService = Depends(get_session_service)
):
    await service.revoke_session(session_id)
    return {"success": True}

@router.delete("", dependencies=[Depends(PermissionChecker("auth:update"))])
async def revoke_all_sessions(
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service)
):
    await service.revoke_all_sessions(current_user.id)
    return {"success": True}
