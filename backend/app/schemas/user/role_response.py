import uuid

from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    """
    Request model for creating a new role.
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Machine-readable unique name (lowercase, no spaces).",
    )
    display_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Human-readable title display name.",
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="Optional detailed description.",
    )


class RoleResponse(BaseModel):
    """
    Response model detailing a user role.
    """
    id: uuid.UUID
    name: str
    display_name: str
    description: str | None = None

    model_config = {
        "from_attributes": True,
    }
