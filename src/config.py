"""Configuration module for the Watchlist API."""

import os
from dotenv import load_dotenv

load_dotenv()


# pylint: disable=too-few-public-methods
class Config:
    """Application configuration class.

    This class holds all configuration variables for the application,
    loaded from environment variables.
    """

    DATABASE_URL = os.getenv("DATABASE_URL")
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
