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
    settings = get_settings()
    client = pymongo.MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    geolocator = Nominatim(user_agent=settings.geopy_user_agent)
    return db, geolocator


def load_csv_column(path: Path) -> list[str]:
    dataframe = pd.read_csv(path)
    return dataframe["text"].dropna().astype(str).tolist()


def build_town_document(name: str, latitude: float, longitude: float, *, regional: bool, district: bool) -> dict[str, object]:
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
    db, geolocator = build_runtime()
    district_towns = load_csv_column(DATA_DIR / "OkresniMesta.csv")
    extended_competence_towns = load_csv_column(DATA_DIR / "ObceSRozsirenouPusobnosti.csv")

    insert_towns(db, geolocator, REGION_TOWNS, regional=True, district=True)
    insert_towns(db, geolocator, district_towns, regional=False, district=True)
    insert_towns(db, geolocator, extended_competence_towns, regional=False, district=False)


def main() -> None:
    load_towns()
