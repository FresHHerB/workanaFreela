"""
Environment configuration module.
Centralizes all environment variable management.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""

    # Workana credentials (required for scraping)
    WORKANA_EMAIL: Optional[str] = os.getenv("WORKANA_EMAIL")
    WORKANA_PASSWORD: Optional[str] = os.getenv("WORKANA_PASSWORD")

    # Server configuration
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    @classmethod
    def validate(cls) -> bool:
        """Validate required environment variables."""
        required_vars = [
            ("WORKANA_EMAIL", cls.WORKANA_EMAIL),
            ("WORKANA_PASSWORD", cls.WORKANA_PASSWORD),
        ]

        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        return True

config = Config()