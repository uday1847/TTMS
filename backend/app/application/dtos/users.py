import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.domain.enums.user_status import UserStatus

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    phone: str | None = None
    role_ids: list[uuid.UUID] = []

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    profile_picture_url: str | None = None
    role_ids: list[uuid.UUID] | None = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone: str | None = None
    status: UserStatus
    last_login_at: datetime | None = None
    profile_picture_url: str | None = None
    created_at: datetime
    updated_at: datetime

class UserDashboardResponse(BaseModel):
    users: list[UserResponse]
    total_count: int

class BulkUserCreate(BaseModel):
    users: list[UserCreate]

class BulkUserAction(BaseModel):
    user_ids: list[uuid.UUID]
