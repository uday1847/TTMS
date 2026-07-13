import datetime
import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.domain.entities.user import User


class AuditLog(Base):
    """
    Read-only system audit log recording CRUD mutations and user actions.
    Uses PostgreSQL JSONB columns to capture data changes.
    """
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    # Actor doing the change (nullable to support system-triggered mutations)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(10),
        nullable=False,  # e.g., 'INSERT', 'UPDATE', 'DELETE', 'RESTORE'
    )

    table_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
        index=True,
    )

    # Audit values changes (diff payload)
    old_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    new_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Network metadata
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User | None"] = relationship()

    # Indexes
    __table_args__ = (
        Index("idx_audit_logs_created_at", created_at.desc()),
        Index("idx_audit_logs_target_record", table_name, record_id),
    )
