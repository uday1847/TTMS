from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError
from pwdlib import PasswordHash

from app.core.settings import settings

# Initialize PasswordHash using recommended settings (Argon2id default via argon2-cffi)
_password_hasher = PasswordHash.recommended()

# Configuration settings (loaded via settings object)
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using Argon2id/bcrypt via pwdlib.
    """
    return _password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed value.
    """
    try:
        return _password_hasher.verify(password, hashed_password)
    except Exception:
        return False


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT access token encoding the subject claim and an expiration timeframe.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT refresh token with a longer duration.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises JWTError if invalid or expired.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])