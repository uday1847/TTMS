import warnings
from app.application.dtos.users import UserResponse

warnings.warn(
    "Importing UserResponse from app.schemas is deprecated. Use app.application.dtos.users instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["UserResponse"]
