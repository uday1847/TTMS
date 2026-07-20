import warnings
from app.application.dtos.users import UserCreate

warnings.warn(
    "Importing UserCreate from app.schemas is deprecated. Use app.application.dtos.users instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["UserCreate"]
