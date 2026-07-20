from typing import Annotated
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, ExpiredSignatureError

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
    return UserService(user_repo, role_repo)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """
    Dependency extracting the access token and returning the current authenticated User.
    Provides specific error messages for different JWT failure modes:
    - Expired tokens
    - Invalid signatures
    - Malformed tokens
    - Missing/invalid claims
    """
    
    # Base exception for generic auth failures
    generic_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        from app.application.services.jwt_service import JWTService
        try:
            payload = JWTService.verify_token(token, expected_type="access")
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError as e:
            # Handle invalid signature, malformed token, or other JWT errors
            error_detail = str(e)
            if "signature" in error_detail.lower():
                detail = "Invalid token signature. Token may have been tampered with."
            elif "malformed" in error_detail.lower() or "invalid" in error_detail.lower():
                detail = "Malformed or invalid token format."
            else:
                detail = "Invalid authentication token."
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail,
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not payload:
            raise generic_credentials_exception
            
        user_id_str = validate_auth_token_payload(payload)
        user_id = uuid.UUID(user_id_str)
        
    except HTTPException:
        # Re-raise HTTP exceptions (specific JWT errors already raised above)
        raise
    except InvalidCredentialsException:
        raise generic_credentials_exception
    except Exception as e:
        # Generic catch-all for unexpected errors
        raise generic_credentials_exception

    # Fetch user from database
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been deleted.",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
