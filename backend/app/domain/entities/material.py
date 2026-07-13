from decimal import Decimal

from sqlalchemy import Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import BaseEntity


class Material(BaseEntity):
    """
    Represents material categories hauled by tractors (e.g. M-Sand, Blue Metal).
    """
    __tablename__ = "materials"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    unit_of_measure: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="TONS",  # e.g., 'TONS', 'BRASS', 'TRIP'
    )

    density_factor: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 3),
        nullable=True,
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_materials_name",
            "name",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
