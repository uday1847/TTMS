from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """
    Request model for creating a new system user profile.
    """
    email: EmailStr = Field(..., description="Unique email address for the user.")
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="Unique username containing alphanumeric, hyphens, and underscores.",
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Initial login password (which will be hashed).",
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="First name profile value.",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Last name profile value.",
    )
    phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=15,
        pattern=r"^\+?[0-9\-\s]+$",
        description="Optional contact telephone value.",
    )
