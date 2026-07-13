from pydantic import BaseModel


class LoginResponse(BaseModel):
    """
    Response payload for successful user authentication.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
