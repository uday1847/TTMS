from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Uuid, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.invoice import Invoice
    from app.domain.entities.user import User


class InvoiceStatusHistory(BaseEntity):
    """
    Audit log tracking status transitions on Invoice documents.
    """
    __tablename__ = "invoice_status_histories"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
        nullable=False,
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(
        back_populates="status_history",
        foreign_keys=[invoice_id],
    )
    user: Mapped["User | None"] = relationship(
        foreign_keys=[changed_by],
    )
