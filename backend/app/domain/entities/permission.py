from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.role import Role


class Permission(BaseEntity):
    """
    Represents a fine-grained access permission (e.g., 'trips:create', 'invoices:approve')
    for authorization checks.
    """
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
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

    # Unique index matching only non-deleted entries for soft delete compatibility
    __table_args__ = (
        Index(
            "uq_permissions_code",
            "code",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
