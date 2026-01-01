"""
Configuration Management

Purpose: Load environment variables and application configuration.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    INSIGHTSENTRY_API_KEY: str = Field(..., env="INSIGHTSENTRY_API_KEY")

    # Server Configuration
    BACKEND_PORT: int = Field(8000, env="BACKEND_PORT")
    FRONTEND_PORT: int = Field(3000, env="FRONTEND_PORT")

    # Logging
    LOG_LEVEL: str = Field("DEBUG", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).

    Returns:
        Settings instance

    Raises:
        ValidationError: If required environment variables are missing
    """
    return Settings()


# Convenience function to get API key
def get_api_key() -> str:
    """
    Get InsightSentry API key from environment.

    Returns:
        API key string

    Raises:
        ValueError: If API key not found in environment
    """
    api_key = os.getenv("INSIGHTSENTRY_API_KEY")
    if not api_key:
        raise ValueError(
            "INSIGHTSENTRY_API_KEY environment variable not set. "
            "Please create backend/.env file with your API key."
        )
    return api_key
