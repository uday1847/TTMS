from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.dependencies.db import get_session
from app.application.dtos.auth import LoginRequest, LoginResponse, ChangePasswordRequest
from app.application.services.authentication_service import AuthenticationService
from app.application.services.session_service import SessionService
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.login_history_repository import SQLAlchemyLoginHistoryRepository
from app.infrastructure.repositories.password_history_repository import SQLAlchemyPasswordHistoryRepository
from app.infrastructure.repositories.session_repository import SQLAlchemySessionRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_session_service(db: AsyncSession = Depends(get_session)) -> SessionService:
    return SessionService(SQLAlchemySessionRepository(db))

def get_auth_service(db: AsyncSession = Depends(get_session), session_service: SessionService = Depends(get_session_service)) -> AuthenticationService:
    return AuthenticationService(
        SQLAlchemyUserRepository(db),
        SQLAlchemyLoginHistoryRepository(db),
        SQLAlchemyPasswordHistoryRepository(db),
        session_service
    )

@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    dto: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await auth_service.login(dto, ip_address=ip_address, user_agent=user_agent)

@router.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    dto = LoginRequest(
        username_or_email=form_data.username,
        password=form_data.password
    )
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    response = await auth_service.login(dto, ip_address=ip_address, user_agent=user_agent)
    
    return {
        "access_token": response.access_token,
        "token_type": response.token_type,
        "refresh_token": response.refresh_token,
        "user_id": str(response.user_id)
    }

@router.put("/change-password")
async def change_password(
    dto: ChangePasswordRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    # TODO: Get user_id from Current User dependency
    # For now, hardcode or accept from header if not fully implemented current_user
    # Actually, we need a get_current_user dependency to do this properly.
    # We will implement get_current_user in dependencies.
    pass
