import uuid

from pydantic import BaseModel


class PermissionResponse(BaseModel):
    """
    Response model detailing a system permission.
    """
    id: uuid.UUID
    code: str
    description: str | None = None

    model_config = {
        "from_attributes": True,
    }
