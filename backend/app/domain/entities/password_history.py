import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.user import User

class PasswordHistory(BaseEntity):
    __tablename__ = "password_history"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="password_history", foreign_keys=[user_id])
