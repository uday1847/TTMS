from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.refresh_token import RefreshToken
    from app.domain.entities.role import Role
    from app.domain.entities.user_session import UserSession
    from app.domain.entities.login_history import LoginHistory
    from app.domain.entities.password_history import PasswordHistory
    from app.domain.entities.user_preference import UserPreference
    from app.domain.entities.user_permission import UserPermission

from sqlalchemy.dialects.postgresql import ENUM
from app.domain.enums.user_status import UserStatus


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

    status: Mapped[UserStatus] = mapped_column(
        ENUM(UserStatus, name="user_status", create_type=False),
        nullable=False,
        default=UserStatus.ACTIVE,
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    locked_until: Mapped["datetime | None"] = mapped_column(
        nullable=True,
        default=None,
    )

    last_login_at: Mapped["datetime | None"] = mapped_column(
        nullable=True,
        default=None,
    )

    profile_picture_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
    )

    token_version: Mapped[int] = mapped_column(
        nullable=False,
        default=1,
    )

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        primaryjoin="User.id == UserRole.user_id",
        secondaryjoin="Role.id == UserRole.role_id",
        back_populates="users",
    )

    direct_permissions: Mapped[list["UserPermission"]] = relationship(
        back_populates=None,
        cascade="all, delete-orphan",
        foreign_keys="[UserPermission.user_id]"
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[UserSession.user_id]"
    )

    login_history: Mapped[list["LoginHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[LoginHistory.user_id]"
    )

    password_history: Mapped[list["PasswordHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[PasswordHistory.user_id]"
    )

    preferences: Mapped["UserPreference"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="[UserPreference.user_id]"
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
