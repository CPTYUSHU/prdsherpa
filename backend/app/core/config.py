"""
Application configuration management using pydantic-settings.
All sensitive information is loaded from .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # AI Models - Gemini (Primary)
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3-flash-preview"

    # AI Models - OpenAI (Optional)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # AI Models - Claude (Optional)
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # AI Model Selection
    DEFAULT_AI_PROVIDER: str = "gemini"  # "gemini", "openai", or "claude"

    # Network Proxy (Optional)
    HTTP_PROXY: str = ""
    HTTPS_PROXY: str = ""

    # Redis
    REDIS_URL: str
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    MAX_FILES_PER_PROJECT: int = 50
    
    # Application
    DEBUG: bool = False
    SECRET_KEY: str
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()

