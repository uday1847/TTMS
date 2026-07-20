import sys
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Metadata Settings
    APP_NAME: str = "TTMS"
    PROJECT_NAME: str = "Transport Tractor Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"

    # Required Database and Security Settings
    DATABASE_URL: str
    JWT_SECRET_KEY: str

    # Security Defaults
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RUN_DATABASE_SEED: bool = False

    # Utilities
    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"])
    TIMEZONE: str = "Asia/Kolkata"
    ACCESS_LOG: bool = True
    SQL_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


try:
    settings = Settings()
except ValidationError as e:
    print("❌ Application configuration validation failed!", file=sys.stderr)
    for error in e.errors():
        loc = " -> ".join(str(x) for x in error["loc"])
        print(f"  - {loc}: {error['msg']} (type={error['type']})", file=sys.stderr)
    sys.exit(1)