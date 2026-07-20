import warnings
from app.application.dtos.users import UserUpdate

warnings.warn(
    "Importing UserUpdate from app.schemas is deprecated. Use app.application.dtos.users instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["UserUpdate"]
