from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.permission import Permission
    from app.domain.entities.user import User


class Role(BaseEntity):
    """
    Defines system authorization groups (e.g., 'admin', 'dispatcher', 'driver', 'accountant').
    """
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles",
    )

    users: Mapped[list["User"]] = relationship(
        secondary="user_roles",
        primaryjoin="Role.id == UserRole.role_id",
        secondaryjoin="User.id == UserRole.user_id",
        back_populates="roles",
    )

    # Unique index matching only active non-deleted roles
    __table_args__ = (
        Index(
            "uq_roles_name",
            "name",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
