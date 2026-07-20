import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError, ExpiredSignatureError

from app.core.security import security_settings
from app.core.settings import settings

class JWTService:
    @staticmethod
    def create_access_token(user_id: uuid.UUID, email: str, token_version: int, permissions: list[str], roles: list[str] = None) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "email": email,
            "version": token_version,
            "roles": roles or [],
            "permissions": permissions,
            "iss": security_settings.TOKEN_ISSUER,
            "aud": security_settings.TOKEN_AUDIENCE,
            "exp": expire,
            "type": "access"
        }
        encoded_jwt = jwt.encode(to_encode, security_settings.JWT_SECRET_KEY, algorithm=security_settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: uuid.UUID, jti: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {
            "sub": str(user_id),
            "jti": jti,
            "iss": security_settings.TOKEN_ISSUER,
            "aud": security_settings.TOKEN_AUDIENCE,
            "exp": expire,
            "type": "refresh"
        }
        encoded_jwt = jwt.encode(to_encode, security_settings.JWT_SECRET_KEY, algorithm=security_settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, expected_type: str = "access") -> dict[str, Any] | None:
        """
        Verify and decode JWT token.
        
        Returns:
            Dictionary with decoded payload if valid
            
        Raises:
            ExpiredSignatureError: Token has expired
            JWTError: Token is invalid, malformed, or has invalid signature
        """
        try:
            payload = jwt.decode(
                token, 
                security_settings.JWT_SECRET_KEY, 
                algorithms=[security_settings.JWT_ALGORITHM],
                audience=security_settings.TOKEN_AUDIENCE,
                issuer=security_settings.TOKEN_ISSUER
            )
            if payload.get("type") != expected_type:
                raise JWTError("Invalid token type")
            return payload
        except ExpiredSignatureError:
            # Re-raise to allow specific handling of expired tokens
            raise
        except JWTError:
            # Re-raise to allow specific handling of other JWT errors
            raise
