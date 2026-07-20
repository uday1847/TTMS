from typing import TYPE_CHECKING
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.domain.entities.permission import Permission


class UserPermission(Base):
    """
    Junction table for user-specific permission overrides.
    is_granted=True means an explicit grant.
    is_granted=False means an explicit revocation (deny).
    """
    __tablename__ = "user_permissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    permission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    is_granted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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
    
    # Relationship to load the actual permission
    permission: Mapped["Permission"] = relationship("Permission")
