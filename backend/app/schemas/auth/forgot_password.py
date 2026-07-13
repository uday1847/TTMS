from pydantic import BaseModel, EmailStr, Field


class ForgotPassword(BaseModel):
    """
    Request model for triggering password recovery.
    """
    email: EmailStr = Field(
        ...,
        description="The email address associated with the account.",
    )
