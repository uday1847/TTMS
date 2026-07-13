from typing import Annotated
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_session
from app.core.security import decode_token
from app.domain.entities.user import User
from app.domain.exceptions.auth import InvalidCredentialsException
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.application.services.user_service import UserService
from app.application.validators.auth_validator import validate_auth_token_payload

# Token endpoint URL matching auth router registration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    """
    Dependency injection factory constructing the UserService.
    """
    user_repo = SQLAlchemyUserRepository(session)
    role_repo = SQLAlchemyRoleRepository(session)
    return UserService(session, user_repo, role_repo)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """
    Dependency extracting the access token and returning the current authenticated User.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise InvalidCredentialsException()
        user_id_str = validate_auth_token_payload(payload)
        user_id = uuid.UUID(user_id_str)
    except Exception:
        raise credentials_exception

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency checking if the current authenticated User is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user profile.",
        )
    return current_user
