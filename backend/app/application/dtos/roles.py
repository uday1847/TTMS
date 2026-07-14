import uuid
from pydantic import BaseModel
from datetime import datetime
from app.domain.enums.role_type import RoleType

class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    permission_ids: list[uuid.UUID] = []

class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permission_ids: list[uuid.UUID] | None = None

class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    role_type: RoleType
    created_at: datetime
    updated_at: datetime
