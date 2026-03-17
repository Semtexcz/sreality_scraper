"""District-loading services for auxiliary coordinate datasets."""

from __future__ import annotations

import csv

import pymongo

from scraperweb.config import DATA_DIR, get_settings


def build_runtime() -> pymongo.database.Database:
    """Build the MongoDB database handle used by the district loader."""

    settings = get_settings()
    client = pymongo.MongoClient(settings.mongodb_uri)
    return client[settings.mongodb_database]


def load_districts() -> int:
    """Load district coordinate rows from the bundled CSV into MongoDB."""

    database = build_runtime()
    collection = database["Okresy"]
    inserted = 0

    with (DATA_DIR / "souradnice.csv").open(mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data = {
                "obec": row["Obec"],
                "okres": row["Okres"],
                "psc": row["PSČ"],
                "latitude": float(row["Latitude"]),
                "longitude": float(row["Longitude"]),
            }
            collection.insert_one(data)
            inserted += 1

    return inserted


def main() -> None:
    """Run the districts loader entrypoint."""

    load_districts()
