"""Runtime configuration values and path constants."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment with sensible defaults."""

    mongodb_uri: str = field(default_factory=lambda: os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    mongodb_database: str = field(default_factory=lambda: os.getenv("MONGODB_DATABASE", "RawListings"))


def get_settings() -> Settings:
    """Return runtime settings for the current process environment."""

    return Settings()
