import warnings
from app.application.dtos.roles import RoleCreate, RoleResponse

warnings.warn(
    "Importing from app.schemas is deprecated. Use app.application.dtos.roles instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["RoleCreate", "RoleResponse"]
