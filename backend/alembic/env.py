import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.core.settings import settings
from app.infrastructure.database.base import Base

# Import all models to ensure they register their metadata with Base.metadata
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.domain.entities.role_permission import RolePermission
from app.domain.entities.user_role import UserRole
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.entities.quarry import Quarry
from app.domain.entities.material import Material
from app.domain.entities.expense_category import ExpenseCategory
from app.domain.entities.expense import Expense
from app.domain.entities.payment import Payment
from app.domain.entities.audit_log import AuditLog
from app.domain.entities.notification import Notification
from app.domain.entities.settings import Settings as DatabaseSettingsModel
from app.domain.entities.trip import Trip


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
