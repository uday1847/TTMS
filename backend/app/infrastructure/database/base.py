import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Root declarative base class for all SQLAlchemy models in the application.
    Serves as the central registry for Declarative Mapping.
    """
    pass


class BaseEntity(Base):
    """
    Abstract Base Entity class that provides common audit tracking, logical soft-delete,
    and optimistic concurrency attributes for every domain entity in the system.
    """
    __abstract__ = True

    # 1. UUID Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        sort_order=-10,  # Forces primary key column to be at the top of generated tables
    )

    # 2. Timezone-Aware Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
        onupdate=func.clock_timestamp(),
        nullable=False,
    )

    # 3. User Audit Fields (Foreign Key refers to 'users' table via string reference)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )

    # 4. Soft Delete Timestamp
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # 5. Logical Status Flag
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    # 6. Optimistic Concurrency Control (OCC) Version
    version_id: Mapped[int] = mapped_column(
        nullable=False,
        default=1,
    )

    # Bind version_id to SQLAlchemy's internal versioning engine
    __mapper_args__: dict[str, Any] = {
        "version_id_col": version_id,
    }


# Import all entity modules to populate the declarative registry.
# Using full module imports to prevent partially-initialized circular import errors in scripts/tests.
import app.domain.entities.user
import app.domain.entities.role
import app.domain.entities.permission
import app.domain.entities.role_permission
import app.domain.entities.user_role
import app.domain.entities.refresh_token
import app.domain.entities.driver
import app.domain.entities.tractor
import app.domain.entities.party
import app.domain.entities.quarry
import app.domain.entities.material
import app.domain.entities.expense_category
import app.domain.entities.expense
import app.domain.entities.payment
import app.domain.entities.audit_log
import app.domain.entities.notification
import app.domain.entities.settings
import app.domain.entities.trip
