from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "RealEstates")
    scraper_api_url: str = os.getenv("SCRAPER_API_URL", "http://localhost:8000/receivedData")
    geopy_user_agent: str = os.getenv("GEOPY_USER_AGENT", "scraperweb")


def get_settings() -> Settings:
    return Settings()
