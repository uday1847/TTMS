import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError

from app.core.security import security_settings

class JWTService:
    @staticmethod
    def create_access_token(user_id: uuid.UUID, email: str, token_version: int, permissions: list[str]) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "email": email,
            "version": token_version,
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
        expire = datetime.now(timezone.utc) + timedelta(days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS)
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
        try:
            payload = jwt.decode(
                token, 
                security_settings.JWT_SECRET_KEY, 
                algorithms=[security_settings.JWT_ALGORITHM],
                audience=security_settings.TOKEN_AUDIENCE,
                issuer=security_settings.TOKEN_ISSUER
            )
            if payload.get("type") != expected_type:
                return None
            return payload
        except JWTError:
            return None
