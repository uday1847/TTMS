import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class RolePermission(Base):
    """
    Junction table for the many-to-many relationship between Roles and Permissions.
    Inherits from root registry Base to define custom composite primary keys.
    """
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    permission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
        nullable=False,
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
