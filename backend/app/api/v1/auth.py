from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.api.dependencies.auth import get_current_active_user, get_user_service
from app.api.dependencies.db import get_session
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.domain.entities.user import User
from app.infrastructure.repositories.refresh_token_repository import SQLAlchemyRefreshTokenRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.schemas.auth.change_password import ChangePassword
from app.schemas.auth.forgot_password import ForgotPassword
from app.schemas.auth.login_request import LoginRequest
from app.schemas.auth.login_response import LoginResponse
from app.schemas.auth.refresh_request import RefreshRequest
from app.schemas.auth.refresh_response import RefreshResponse
from app.schemas.auth.reset_password import ResetPassword
from app.schemas.response import APIResponse
from app.schemas.user.user_create import UserCreate
from app.schemas.user.user_response import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    """
    Dependency injection factory constructing the AuthService.
    """
    user_repo = SQLAlchemyUserRepository(session)
    token_repo = SQLAlchemyRefreshTokenRepository(session)
    return AuthService(session, user_repo, token_repo)


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    dto: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """
    Creates a new user profile with standard credentials.
    """
    user = await user_service.register_user(dto)
    return APIResponse(
        success=True,
        message="User registered successfully.",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    summary="Log in and retrieve tokens",
)
async def login(
    dto: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[LoginResponse]:
    """
    Validates user credentials and issues access and refresh tokens.
    """
    tokens = await auth_service.login(dto)
    return APIResponse(
        success=True,
        message="Login successful.",
        data=tokens,
    )


class TokenResponse(BaseModel):
    """
    Standard OAuth2 compatible token response schema for Swagger UI login.
    """
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="OAuth2-compatible token login for Swagger UI",
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    OAuth2-compatible endpoint that accepts form urlencoded credentials,
    authenticates via AuthService, and returns standard token payload for Swagger UI.
    """
    dto = LoginRequest(
        username_or_email=form_data.username,
        password=form_data.password
    )
    tokens = await auth_service.login(dto)
    return TokenResponse(
        access_token=tokens.access_token,
        token_type="bearer"
    )


@router.post(
    "/logout",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Log out and revoke sessions",
)
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[None]:
    """
    Invalidates and revokes all active token credentials for the user session.
    """
    await auth_service.logout(current_user.id)
    return APIResponse(
        success=True,
        message="User logged out successfully.",
        data=None,
    )


@router.post(
    "/refresh",
    response_model=APIResponse[RefreshResponse],
    status_code=status.HTTP_200_OK,
    summary="Refresh access tokens",
)
async def refresh(
    dto: RefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[RefreshResponse]:
    """
    Performs token rotation. Replaces the current refresh token with a new pair.
    """
    new_tokens = await auth_service.refresh_token(dto)
    return APIResponse(
        success=True,
        message="Tokens refreshed successfully.",
        data=new_tokens,
    )


@router.post(
    "/change-password",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Change account password",
)
async def change_password(
    dto: ChangePassword,
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[None]:
    """
    Updates the user's password after validating current credentials.
    """
    await auth_service.change_password(current_user.id, dto)
    return APIResponse(
        success=True,
        message="Password updated successfully. Active sessions revoked.",
        data=None,
    )


@router.post(
    "/forgot-password",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Request a password reset link",
)
async def forgot_password(
    dto: ForgotPassword,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[None]:
    """
    Triggers password recovery. Issues a short-lived recovery token (sent via logs).
    """
    await auth_service.forgot_password(dto.email)
    return APIResponse(
        success=True,
        message="If the email exists, a password reset link has been dispatched.",
        data=None,
    )


@router.post(
    "/reset-password",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Reset password using token",
)
async def reset_password(
    dto: ResetPassword,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[None]:
    """
    Resets the account password using the token issued during recovery.
    """
    await auth_service.reset_password(dto)
    return APIResponse(
        success=True,
        message="Password has been reset successfully.",
        data=None,
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user details",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> APIResponse[UserResponse]:
    """
    Returns the authenticated user's profile metadata and role groups.
    """
    return APIResponse(
        success=True,
        message="Current user fetched successfully.",
        data=UserResponse.model_validate(current_user),
    )
