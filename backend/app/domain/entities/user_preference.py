import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.user import User

class UserPreference(BaseEntity):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    theme: Mapped[str] = mapped_column(String(50), nullable=False, default="light")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    date_format: Mapped[str] = mapped_column(String(20), nullable=False, default="YYYY-MM-DD")
    number_format: Mapped[str] = mapped_column(String(20), nullable=False, default="en-US")
    dashboard_layout: Mapped[str] = mapped_column(String(255), nullable=False, default="default")
    notification_settings: Mapped[str] = mapped_column(String(1000), nullable=False, default="{}")

    # Relationships
    user: Mapped["User"] = relationship(back_populates="preferences")
