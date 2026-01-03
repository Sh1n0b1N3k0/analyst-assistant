"""Configuration settings for the Requirements Management System."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Requirements Management System"
    app_version: str = "1.4.1"
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/requirements_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

