from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.core.settings import settings

DATABASE_URL = settings.DATABASE_URL

# Create async engine with configured SQL echo setting
engine = create_async_engine(DATABASE_URL, echo=settings.SQL_ECHO, future=True)

# Define async sessionmaker factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
