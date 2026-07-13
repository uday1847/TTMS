from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    Request model for user authentication. Accepts email or username.
    """
    username_or_email: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The username or email address registered for the user account.",
    )
    password: str = Field(
        ...,
        min_length=6,
        description="The account password.",
    )
