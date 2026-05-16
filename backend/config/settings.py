from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://app:app@localhost:5433/dummyjson",
        description="SQLAlchemy async database URL.",
    )
    dummyjson_base_url: str = Field(default="https://dummyjson.com")
    dummyjson_timeout_seconds: float = Field(default=10.0, gt=0)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    log_level: str = Field(default="INFO")
