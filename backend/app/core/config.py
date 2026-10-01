"""Application settings, read from environment variables.

Only one setting exists so far. See backend/.env.example for the full list.
"""

import os
from dataclasses import dataclass

# Relative to the folder the backend runs in: backend/ locally, /app in Docker.
DEFAULT_DATABASE_URL = "sqlite:///./data/uttt.db"


@dataclass(frozen=True)
class Settings:
    database_url: str


def load_settings() -> Settings:
    return Settings(database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))


settings = load_settings()
