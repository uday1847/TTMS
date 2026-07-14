import os
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

class SecuritySettings:
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-ttms-key-must-change-in-prod")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    TOKEN_ISSUER: str = "ttms-auth-service"
    TOKEN_AUDIENCE: str = "ttms-frontend"

    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_LOWER: bool = True
    PASSWORD_HISTORY_COUNT: int = 5
    PASSWORD_EXPIRE_DAYS: int = 90

    # Account Lock Policy
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCK_DURATION_MINUTES: int = 15

    # Caching
    PERMISSION_CACHE_TTL_SECONDS: int = 300

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        password_hash = PasswordHash((Argon2Hasher(),))
        return password_hash.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        try:
            password_hash = PasswordHash((Argon2Hasher(),))
            return password_hash.verify(plain_password, hashed_password)
        except Exception:
            return False

security_settings = SecuritySettings()

# Top-level backward compatibility functions for existing auth dependency
def hash_password(password: str) -> str:
    return security_settings.get_password_hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return security_settings.verify_password(password, hashed_password)

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, security_settings.JWT_SECRET_KEY, algorithm=security_settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, security_settings.JWT_SECRET_KEY, algorithm=security_settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, security_settings.JWT_SECRET_KEY, algorithms=[security_settings.JWT_ALGORITHM])