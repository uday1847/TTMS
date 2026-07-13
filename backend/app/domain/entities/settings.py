from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import BaseEntity


class Settings(BaseEntity):
    """
    Key-Value configuration settings for application parameters (e.g. system tax rates).
    """
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_settings_key",
            "key",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
