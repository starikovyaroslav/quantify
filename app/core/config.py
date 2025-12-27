"""
Application configuration
"""
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "QuantTxt"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["*"]

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/quanttxt"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    RESULT_DIR: str = "./results"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000

    # Processing
    DEFAULT_WIDTH: int = 200
    DEFAULT_HEIGHT: int = 200
    MAX_WIDTH: int = 1000
    MAX_HEIGHT: int = 1000
    DEFAULT_QUALITY: int = 5
    TASK_TIMEOUT_SECONDS: int = 300  # 5 minutes hard timeout
    TASK_SOFT_TIMEOUT_SECONDS: int = 240  # 4 minutes soft timeout

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

