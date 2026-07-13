from pydantic import BaseModel, Field


class ResetPassword(BaseModel):
    """
    Request model for completing a password reset using a validation token.
    """
    token: str = Field(
        ...,
        description="The verification token received via email.",
    )
    new_password: str = Field(
        ...,
        min_length=6,
        description="The new password to set on the account.",
    )
