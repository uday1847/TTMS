from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr

from app.schemas.user.role_response import RoleResponse


class UserResponse(BaseModel):
    """
    Response model detailing a user's details and active role associations.
    """
    id: uuid.UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: list[RoleResponse] = []

    model_config = {
        "from_attributes": True,
    }
