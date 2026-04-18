"""Application configuration using Pydantic Settings"""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str = ""

    @model_validator(mode="after")
    def derive_sync_url(self) -> "Settings":
        if not self.DATABASE_URL_SYNC:
            url = self.DATABASE_URL
            url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
            url = url.replace("postgresql://", "postgresql+psycopg2://")
            self.DATABASE_URL_SYNC = url
        return self

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # Application
    APP_NAME: str = "MGA Soap Calculator API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
