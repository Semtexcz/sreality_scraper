"""Town-loading services for auxiliary geodata used by the project."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import pymongo
from geopy.geocoders import Nominatim

from scraperweb.config import DATA_DIR, get_settings


REGION_TOWNS = [
    "Praha",
    "České Budějovice",
    "Plzeň",
    "Karlovy Vary",
    "Liberec",
    "Hradec Králové",
    "Pardubice",
    "Jihlava",
    "Brno",
    "Olomouc",
    "Ostrava",
    "Zlín",
]


def build_runtime() -> tuple[pymongo.database.Database, Nominatim]:
    """Build database and geocoding clients required for town loading."""

    settings = get_settings()
    client = pymongo.MongoClient(settings.mongodb_uri)
    database = client[settings.mongodb_database]
    geolocator = Nominatim(user_agent=settings.geopy_user_agent)
    return database, geolocator


def load_csv_column(path: Path) -> list[str]:
    """Load the `text` column from a CSV file as town names."""

    dataframe = pd.read_csv(path)
    return dataframe["text"].dropna().astype(str).tolist()


def build_town_document(
    name: str,
    latitude: float,
    longitude: float,
    *,
    regional: bool,
    district: bool,
) -> dict[str, object]:
    """Build one MongoDB document for a town geocoding result."""

    return {
        "Název": name,
        "Zeměpisná šířka": latitude,
        "Zeměpisná délka": longitude,
        "Krajské město": regional,
        "Okresní město": district,
        "S rozšířenou působností": True,
    }


def insert_towns(
    db: pymongo.database.Database,
    geolocator: Nominatim,
    town_names: list[str],
    *,
    regional: bool,
    district: bool,
) -> None:
    """Geocode and insert town documents into the MongoDB collection."""

    collection = db["Towns"]
    for town_name in town_names:
        location = geolocator.geocode(town_name)
        if not location:
            continue
        document = build_town_document(
            town_name,
            location.latitude,
            location.longitude,
            regional=regional,
            district=district,
        )
        collection.insert_one(document)
        print(document)
        time.sleep(1)


def load_towns() -> None:
    """Load regional, district, and extended-competence towns into MongoDB."""

    database, geolocator = build_runtime()
    district_towns = load_csv_column(DATA_DIR / "OkresniMesta.csv")
    extended_competence_towns = load_csv_column(DATA_DIR / "ObceSRozsirenouPusobnosti.csv")

    insert_towns(database, geolocator, REGION_TOWNS, regional=True, district=True)
    insert_towns(database, geolocator, district_towns, regional=False, district=True)
    insert_towns(
        database,
        geolocator,
        extended_competence_towns,
        regional=False,
        district=False,
    )


def main() -> None:
    """Run the towns loader entrypoint."""

    load_towns()
