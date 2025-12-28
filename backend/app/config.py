from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "PetHope API"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True)

    # Security
    secret_key: str = Field(..., alias="SECRET_KEY")
    admin_password: str = Field(..., alias="ADMIN_PASSWORD")
    access_token_expire_minutes: int = Field(default=60 * 24 * 7)  # 7 days

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost",
        alias="ALLOWED_ORIGINS",
    )

    # Database
    database_url: str = Field(..., alias="DATABASE_URL")

    # MinIO/S3
    minio_endpoint: str = Field(..., alias="MINIO_ENDPOINT")
    minio_public_url: str = Field(default="", alias="MINIO_PUBLIC_URL")
    minio_access_key: str = Field(..., alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="pethope-images", alias="MINIO_BUCKET")
    minio_use_ssl: bool = Field(default=False, alias="MINIO_USE_SSL")

    # Image upload
    max_image_size_mb: int = Field(default=5)
    allowed_image_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".webp"]
    )
    thumbnail_size: tuple[int, int] = Field(default=(400, 400))

    # Pagination
    default_page_size: int = Field(default=20)
    max_page_size: int = Field(default=100)

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v: str | bool) -> bool:
        """Parse debug from string or bool."""
        if isinstance(v, bool):
            return v
        return v.lower() in ("true", "1", "yes")

    @field_validator("minio_use_ssl", mode="before")
    @classmethod
    def parse_ssl(cls, v: str | bool) -> bool:
        """Parse SSL flag from string or bool."""
        if isinstance(v, bool):
            return v
        return v.lower() in ("true", "1", "yes")

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def max_image_size_bytes(self) -> int:
        """Convert max image size to bytes."""
        return self.max_image_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
