from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.refresh_token import RefreshToken
    from app.domain.entities.role import Role


class User(BaseEntity):
    """
    Represents system users, including contact profiles, authorization roles,
    and login credentials.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        primaryjoin="User.id == UserRole.user_id",
        secondaryjoin="Role.id == UserRole.role_id",
        back_populates="users",
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Partial unique indexes for email and username compatibility with soft-deletes
    __table_args__ = (
        Index(
            "uq_users_email",
            "email",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "uq_users_username",
            "username",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )
