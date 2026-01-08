"""
Configuration settings for the PE Compass API
"""
import os
from typing import Optional

class Settings:
    """Application settings."""
    
    # API Configuration
    API_TITLE: str = "PE Compass API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Backend API for PE Compass"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./PE_compass.db"
    )
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]  # Adjust in production
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
