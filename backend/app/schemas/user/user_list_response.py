from pydantic import BaseModel

from app.schemas.user.user_response import UserResponse


class UserListResponse(BaseModel):
    """
    Paginated list wrapper for user responses.
    """
    items: list[UserResponse]
    total: int
    page: int
    size: int
