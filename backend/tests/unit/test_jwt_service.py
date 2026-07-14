import uuid
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.application.services.jwt_service import JWTService
from app.core.security import security_settings

def test_create_access_token():
    user_id = uuid.uuid4()
    email = "test@example.com"
    token_version = 1
    permissions = ["auth:read", "users:write"]

    token = JWTService.create_access_token(user_id, email, token_version, permissions)
    assert isinstance(token, str)

    payload = jwt.decode(
        token,
        security_settings.JWT_SECRET_KEY,
        algorithms=[security_settings.JWT_ALGORITHM],
        audience=security_settings.TOKEN_AUDIENCE,
        issuer=security_settings.TOKEN_ISSUER
    )

    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["version"] == token_version
    assert payload["permissions"] == permissions
    assert payload["type"] == "access"
    assert "exp" in payload

def test_create_refresh_token():
    user_id = uuid.uuid4()
    jti = str(uuid.uuid4())

    token = JWTService.create_refresh_token(user_id, jti)
    assert isinstance(token, str)

    payload = jwt.decode(
        token,
        security_settings.JWT_SECRET_KEY,
        algorithms=[security_settings.JWT_ALGORITHM],
        audience=security_settings.TOKEN_AUDIENCE,
        issuer=security_settings.TOKEN_ISSUER
    )

    assert payload["sub"] == str(user_id)
    assert payload["jti"] == jti
    assert payload["type"] == "refresh"
    assert "exp" in payload

def test_verify_token_valid_access():
    user_id = uuid.uuid4()
    token = JWTService.create_access_token(user_id, "test@example.com", 1, [])
    
    payload = JWTService.verify_token(token, expected_type="access")
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"

def test_verify_token_valid_refresh():
    user_id = uuid.uuid4()
    token = JWTService.create_refresh_token(user_id, "test-jti")
    
    payload = JWTService.verify_token(token, expected_type="refresh")
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"

def test_verify_token_wrong_type():
    user_id = uuid.uuid4()
    token = JWTService.create_access_token(user_id, "test@example.com", 1, [])
    
    payload = JWTService.verify_token(token, expected_type="refresh")
    assert payload is None

def test_verify_token_invalid_signature():
    user_id = uuid.uuid4()
    token = JWTService.create_access_token(user_id, "test@example.com", 1, [])
    
    # Tamper with token
    tampered_token = token[:-5] + "aaaaa"
    
    payload = JWTService.verify_token(tampered_token)
    assert payload is None

def test_verify_token_expired():
    # Create an expired token manually
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode = {
        "sub": str(uuid.uuid4()),
        "iss": security_settings.TOKEN_ISSUER,
        "aud": security_settings.TOKEN_AUDIENCE,
        "exp": expire,
        "type": "access"
    }
    expired_token = jwt.encode(to_encode, security_settings.JWT_SECRET_KEY, algorithm=security_settings.JWT_ALGORITHM)
    
    payload = JWTService.verify_token(expired_token)
    assert payload is None

def test_verify_token_invalid_issuer():
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode = {
        "sub": str(uuid.uuid4()),
        "iss": "wrong-issuer",
        "aud": security_settings.TOKEN_AUDIENCE,
        "exp": expire,
        "type": "access"
    }
    token = jwt.encode(to_encode, security_settings.JWT_SECRET_KEY, algorithm=security_settings.JWT_ALGORITHM)
    
    payload = JWTService.verify_token(token)
    assert payload is None

def test_verify_token_invalid_audience():
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode = {
        "sub": str(uuid.uuid4()),
        "iss": security_settings.TOKEN_ISSUER,
        "aud": "wrong-audience",
        "exp": expire,
        "type": "access"
    }
    token = jwt.encode(to_encode, security_settings.JWT_SECRET_KEY, algorithm=security_settings.JWT_ALGORITHM)
    
    payload = JWTService.verify_token(token)
    assert payload is None
