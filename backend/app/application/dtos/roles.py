import uuid
from datetime import datetime
from pydantic import Field

from app.domain.enums.role_type import RoleType
from app.application.dtos.base import BaseDTO

class RoleCreate(BaseDTO):
    name: str = Field(..., min_length=2, max_length=50)
    display_name: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    permission_ids: list[uuid.UUID] = []

class RoleUpdate(BaseDTO):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    display_name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    permission_ids: list[uuid.UUID] | None = None

class RoleResponse(BaseDTO):
    id: uuid.UUID
    name: str
    display_name: str
    description: str | None = None
    role_type: RoleType | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
