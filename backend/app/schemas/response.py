from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard envelope format for all API responses.
    """
    success: bool = True
    message: str | None = None
    data: T | None = None


class PaginatedData(BaseModel, Generic[T]):
    """
    Wraps standard paginated array responses.
    """
    items: list[T]
    total: int
    page: int
    size: int
