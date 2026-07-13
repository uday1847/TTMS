from pydantic import BaseModel


class RefreshResponse(BaseModel):
    """
    Response payload for a successful token rotation query.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
