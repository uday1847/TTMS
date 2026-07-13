import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.domain.entities.user import User


class RefreshToken(Base):
    """
    Tracks issued JWT refresh tokens, enabling revocation and token rotation security workflows.
    """
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token: Mapped[str] = mapped_column(
        String(512),
        unique=True,
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    replaced_by_token: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        default=None,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
