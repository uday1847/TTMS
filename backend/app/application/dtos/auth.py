import uuid
from pydantic import BaseModel, EmailStr
from datetime import datetime

class LoginRequest(BaseModel):
    username_or_email: str
    password: str
    device_fingerprint: str | None = None

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: uuid.UUID

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    device_fingerprint: str | None = None

class CurrentUserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    profile_picture_url: str | None = None
    permissions: list[str] = []

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
