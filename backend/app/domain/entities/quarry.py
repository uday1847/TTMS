from sqlalchemy import Index, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import BaseEntity


class Quarry(BaseEntity):
    """
    Represents quarries, mine sites, or load terminals from which materials are transported.
    """
    __tablename__ = "quarries"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    location: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    contact_phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    permit_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_third_party: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_quarries_name",
            "name",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
