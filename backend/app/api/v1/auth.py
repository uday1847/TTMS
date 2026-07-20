from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.dependencies.db import get_session
from app.api.dependencies.auth import get_current_active_user
from app.application.dtos.auth import LoginRequest, LoginResponse, ChangePasswordRequest
from app.application.services.authentication_service import AuthenticationService
from app.application.services.session_service import SessionService
from app.domain.entities.user import User
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
    """
    Primary user login endpoint. Accepts JSON credentials in request body.
    Returns structured login response with access and refresh tokens.
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await auth_service.login(dto, ip_address=ip_address, user_agent=user_agent)

@router.post("/token", response_model=LoginResponse)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    OAuth2 compatible token endpoint. Accepts form-encoded credentials.
    This endpoint exists for Swagger/OpenAPI OAuth2 integration support.
    
    Note: Both /login and /token endpoints return the same LoginResponse structure.
    - Use /login for standard REST API clients (JSON request body)
    - Use /token for OAuth2-compatible integrations (form-encoded body)
    """
    dto = LoginRequest(
        username_or_email=form_data.username,
        password=form_data.password
    )
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return await auth_service.login(dto, ip_address=ip_address, user_agent=user_agent)

@router.put("/change-password")
async def change_password(
    dto: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Change password for the currently authenticated user.
    Requires verification of current password for security.
    Invalidates all user sessions on successful password change.
    Returns APIResponse with success message.
    """
    from app.schemas.response import APIResponse
    
    # Delegate to authentication service which handles:
    # - Password verification
    # - Password history tracking
    # - Session invalidation
    await auth_service.change_password(
        user_id=current_user.id,
        current_password=dto.current_password,
        new_password=dto.new_password,
        confirm_password=dto.confirm_password
    )
    
    return APIResponse(
        success=True,
        message="Password changed successfully. Please log in with your new password.",
        data=None
    )
