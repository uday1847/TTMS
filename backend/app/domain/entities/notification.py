import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.notification_type import NotificationType

if TYPE_CHECKING:
    from app.domain.entities.user import User


class Notification(BaseEntity):
    """
    Represents system notifications, warnings, and messages generated for users.
    Supports tracking read status via a nullable timestamp and custom category types.
    """
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),  # Cascades deletion of notifications if user is deleted
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notification_type_enum", native_enum=True),
        nullable=False,
    )

    # Status tracking (None = Unread, Datetime = Read)
    read_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    # Helper property to expose a boolean is_read status
    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    # Indexes (Partial index to quickly load unread notifications)
    __table_args__ = (
        Index(
            "idx_notifications_unread",
            user_id,
            read_at,
            postgresql_where="read_at IS NULL",
        ),
    )
