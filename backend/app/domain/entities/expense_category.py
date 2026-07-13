from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import BaseEntity


class ExpenseCategory(BaseEntity):
    """
    Lookup configurations for classifying tractor and trip-level expenses.
    """
    __tablename__ = "expense_categories"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_expense_categories_name",
            "name",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
