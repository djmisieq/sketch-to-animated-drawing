"""Configuration module for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sketch-to-Animated-Drawing"
    
    # PostgreSQL configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "sketch"
    POSTGRES_PASSWORD: str = "sketch123"
    POSTGRES_DB: str = "sketch_app"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None
    
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    
    # Minio configuration
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_URL: str = "localhost:9000"
    MINIO_BUCKET: str = "sketches"
    
    # Rendering configuration
    MAX_IMAGE_SIZE_MB: int = 10
    VIDEO_WIDTH: int = 1920
    VIDEO_HEIGHT: int = 1080
    VIDEO_FPS: int = 30
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )


settings = Settings()
