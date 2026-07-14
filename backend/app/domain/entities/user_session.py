import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.infrastructure.database.base import BaseEntity
from app.domain.enums.session_status import SessionStatus

if TYPE_CHECKING:
    from app.domain.entities.user import User

class UserSession(BaseEntity):
    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    device_fingerprint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    
    refresh_token_jti: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    status: Mapped[SessionStatus] = mapped_column(
        ENUM(SessionStatus, name="session_status", create_type=False),
        nullable=False,
        default=SessionStatus.ACTIVE,
    )

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions", foreign_keys=[user_id])
