from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.role import Role

from sqlalchemy.dialects.postgresql import ENUM
from app.domain.enums.permission_module import PermissionModule


class Permission(BaseEntity):
    """
    Represents a fine-grained access permission (e.g., 'trips:create', 'invoices:approve')
    for authorization checks.
    """
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    module: Mapped[PermissionModule] = mapped_column(
        ENUM(PermissionModule, name="permission_module", create_type=False),
        nullable=False,
        default=PermissionModule.USERS,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        secondary="role_permissions",
        back_populates="permissions",
    )

    __table_args__ = (
        Index(
            "uq_permissions_name",
            "name",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
