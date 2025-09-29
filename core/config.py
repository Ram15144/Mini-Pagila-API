"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    ENVIRONMENT: str = "local"
    
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'local')}",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    DATABASE_URL: str = ""
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_ID: str = "gpt-4o-mini"
    
    # Application
    log_level: str = "INFO"
    debug: bool = True
    
    # Authentication
    auth_token: str = "dvd_admin"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000


# Global settings instance
settings = Settings()
