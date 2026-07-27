import os
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Load .env file
load_dotenv()


class SecuritySettings:
    """Centralized security configuration."""

    # =========================
    # JWT Settings
    # =========================
    _jwt_secret = os.getenv("JWT_SECRET_KEY")

    if not _jwt_secret:
        raise ValueError(
            "JWT_SECRET_KEY environment variable is required and must be set. "
            "Minimum 32 characters recommended for HS256 security."
        )

    if len(_jwt_secret) < 32:
        raise ValueError(
            f"JWT_SECRET_KEY must be at least 32 characters long (current: {len(_jwt_secret)})"
        )

    JWT_SECRET_KEY: str = _jwt_secret
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Token expiry
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

    TOKEN_ISSUER: str = "ttms-auth-service"
    TOKEN_AUDIENCE: str = "ttms-frontend"

    # =========================
    # Password Policy
    # =========================
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_LOWER: bool = True
    PASSWORD_HISTORY_COUNT: int = 5
    PASSWORD_EXPIRE_DAYS: int = 90

    # =========================
    # Account Lock Policy
    # =========================
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCK_DURATION_MINUTES: int = 15

    # =========================
    # Caching
    # =========================
    PERMISSION_CACHE_TTL_SECONDS: int = 300

    # Shared password hasher instance
    _password_hash = PasswordHash((Argon2Hasher(),))

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls._password_hash.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        try:
            return cls._password_hash.verify(plain_password, hashed_password)
        except Exception:
            return False


# Singleton instance
security_settings = SecuritySettings()


# =========================
# Backward-compatible helper functions
# =========================
def hash_password(password: str) -> str:
    return security_settings.get_password_hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return security_settings.verify_password(password, hashed_password)


def create_access_token(
    subject: str | Any,
    email: str = None,
    username: str = None,
    roles: list[str] = None,
    permissions: list[str] = None,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "email": email or "",
        "username": username or "",
        "roles": roles or [],
        "permissions": permissions or [],
        "type": "access",
        "iss": security_settings.TOKEN_ISSUER,
        "aud": security_settings.TOKEN_AUDIENCE,
    }

    return jwt.encode(
        to_encode,
        security_settings.JWT_SECRET_KEY,
        algorithm=security_settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iss": security_settings.TOKEN_ISSUER,
        "aud": security_settings.TOKEN_AUDIENCE,
    }

    return jwt.encode(
        to_encode,
        security_settings.JWT_SECRET_KEY,
        algorithm=security_settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            security_settings.JWT_SECRET_KEY,
            algorithms=[security_settings.JWT_ALGORITHM],
            audience=security_settings.TOKEN_AUDIENCE,
            issuer=security_settings.TOKEN_ISSUER,
        )
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc