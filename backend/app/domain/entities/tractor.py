import datetime
import uuid

from sqlalchemy import Date, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import BaseEntity


class Tractor(BaseEntity):
    """
    Represents heavy vehicle assets, tracking registration, specifications,
    and operational availability.
    """
    __tablename__ = "tractors"

    tractor_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    owner_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    rc_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    insurance_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    insurance_expiry: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    manufacturer: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    registration_date: Mapped[datetime.date | None] = mapped_column(
        Date,
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    current_trip_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_tractors_tractor_number",
            "tractor_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "uq_tractors_rc_number",
            "rc_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
