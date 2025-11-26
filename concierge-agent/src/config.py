# src/config.py
"""
Simple env loader for the Concierge Agent.

Reads values from `.env` using python-dotenv + os.getenv.
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env (in project root)
load_dotenv()

class Settings:
    # LLM / OpenRouter
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE: str | None = os.getenv("OPENAI_API_BASE")

    # Google Custom Search
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID: str | None = os.getenv("GOOGLE_CSE_ID")

    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

settings = Settings()
