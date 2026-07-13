from pydantic import BaseModel, EmailStr, Field


class UserUpdate(BaseModel):
    """
    Request model for modifying a user profile (supports partial updates).
    """
    email: EmailStr | None = Field(default=None, description="Updated user email address.")
    username: str | None = Field(default=None, min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_\-]+$")
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=10, max_length=30, pattern=r"^\+?[0-9\-\s]+$")
    is_active: bool | None = Field(default=None, description="Updated logical user status.")
