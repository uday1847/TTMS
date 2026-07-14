import uuid
from pydantic import BaseModel
from app.domain.enums.permission_module import PermissionModule

class PermissionResponse(BaseModel):
    id: uuid.UUID
    name: str
    module: PermissionModule
    description: str | None = None
