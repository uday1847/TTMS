from pydantic import BaseModel, Field


class RefreshRequest(BaseModel):
    """
    Request model for token rotation.
    """
    refresh_token: str = Field(
        ...,
        description="The refresh token issued during login.",
    )
