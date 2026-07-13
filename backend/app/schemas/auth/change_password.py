from pydantic import BaseModel, Field


class ChangePassword(BaseModel):
    """
    Request model for updating user passwords.
    """
    old_password: str = Field(
        ...,
        min_length=6,
        description="The user's current account password.",
    )
    new_password: str = Field(
        ...,
        min_length=6,
        description="The new password to set on the account.",
    )
