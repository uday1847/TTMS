import uuid
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from typing import Optional, Any
from datetime import datetime
from app.domain.enums.user_status import UserStatus

from app.application.dtos.base import BaseDTO

class RoleSummaryDTO(BaseDTO):
    id: uuid.UUID
    name: str
    display_name: str

class PermissionSummaryDTO(BaseDTO):
    id: uuid.UUID
    name: str
    description: str | None = None

class UserRoleUpdate(BaseDTO):
    role_ids: list[uuid.UUID]

class UserPermissionOverrideUpdate(BaseDTO):
    grant_permissions: list[str] = Field(default_factory=list)
    revoke_permissions: list[str] = Field(default_factory=list)

class UserCreate(BaseDTO):
    email: EmailStr = Field(..., description="Unique email address for the user.")
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_\-]+$")
    password: str = Field(..., min_length=6, description="Initial login password (which will be hashed).")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=10, max_length=30, pattern=r"^\+?[0-9\-\s]+$")
    role_ids: list[uuid.UUID] = []

class UserUpdate(BaseDTO):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, description="Updated user email address.")
    username: str | None = Field(default=None, min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_\-]+$")
    phone: str | None = Field(default=None, min_length=10, max_length=30, pattern=r"^\+?[0-9\-\s]+$")
    is_active: bool | None = Field(default=None, description="Updated logical user status.")
    role_ids: list[uuid.UUID] | None = None

class UserResponse(BaseDTO):
    id: uuid.UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone: str | None = None
    status: UserStatus
    is_active: bool = True
    created_at: datetime
    updated_at: datetime | None = None
    roles: list[RoleSummaryDTO] = []
    effective_permissions: list[str] = []
    direct_permissions: list[str] = []
    
    @field_validator('direct_permissions', mode='before')
    @classmethod
    def parse_direct_permissions(cls, value: Any) -> list[str]:
        if not value:
            return []
        if isinstance(value, list):
            if all(isinstance(v, str) for v in value):
                return value
            return [
                f"+{up.permission.name}" if getattr(up, 'is_granted', True) else f"-{up.permission.name}"
                for up in value if getattr(up, 'permission', None)
            ]
        return []
        
    @model_validator(mode='before')
    @classmethod
    def set_computed_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            status_val = data.get('status')
            if status_val is not None:
                data['is_active'] = (status_val == UserStatus.ACTIVE or status_val == UserStatus.ACTIVE.value)
        else:
            status_val = getattr(data, 'status', None)
            if status_val is not None:
                data.is_active = (status_val == UserStatus.ACTIVE or status_val == UserStatus.ACTIVE.value)
        return data

class UserDashboardResponse(BaseDTO):
    users: list[UserResponse]
    total_count: int

class BulkUserCreate(BaseDTO):
    users: list[UserCreate]

class BulkUserAction(BaseDTO):
    user_ids: list[uuid.UUID]
