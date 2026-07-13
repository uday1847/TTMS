from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.trip import Trip
    from app.domain.entities.user import User


class TripStatusHistory(BaseEntity):
    """
    Represents audit trail logs for trip status transitions.
    """
    __tablename__ = "trip_status_histories"

    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    trip: Mapped["Trip"] = relationship(back_populates="status_history", foreign_keys=[trip_id])
