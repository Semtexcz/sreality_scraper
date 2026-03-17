"""Storage ports and adapters for raw listing records."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Protocol

import pymongo

from scraperweb.persistence.models import RawListingRecord


class RawRecordRepository(Protocol):
    """Persistence port for storing immutable raw listing snapshots."""

    def save_record(self, record: RawListingRecord) -> None:
        """Persist one raw listing snapshot."""


class FilesystemRawRecordRepository:
    """Persist raw listing snapshots as JSON files on the local filesystem."""

    def __init__(self, output_dir: Path) -> None:
        """Store the configured filesystem root and ensure it exists."""

        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def save_record(self, record: RawListingRecord) -> None:
        """Persist one raw listing snapshot into a listing-specific directory."""

        listing_directory = (
            self._output_dir
            / _sanitize_path_component(record.source_metadata.region)
            / _sanitize_path_component(record.listing_id)
        )
        listing_directory.mkdir(parents=True, exist_ok=True)

        base_name = _timestamp_for_filename(record.captured_at_utc.isoformat())
        json_path = listing_directory / f"{base_name}.json"

        with json_path.open("w", encoding="utf-8") as output_file:
            json.dump(
                record.to_serializable_dict(),
                output_file,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            output_file.write("\n")

        if record.raw_page_snapshot is not None:
            snapshot_path = listing_directory / f"{base_name}.html"
            snapshot_path.write_text(record.raw_page_snapshot, encoding="utf-8")


class MongoRawRecordRepository:
    """Persist raw listing snapshots as MongoDB documents."""

    def __init__(
        self,
        mongodb_uri: str,
        mongodb_database: str,
        collection_name: str = "raw_listings",
    ) -> None:
        """Create a MongoDB client and prepare collection indexes."""

        self._client = pymongo.MongoClient(mongodb_uri)
        self._collection = self._client[mongodb_database][collection_name]
        self._collection.create_index(
            [("listing_id", pymongo.ASCENDING), ("captured_at_utc", pymongo.ASCENDING)],
            unique=True,
            name="listing_id_captured_at_utc_unique",
        )
        self._collection.create_index(
            [("captured_at_utc", pymongo.ASCENDING)],
            name="captured_at_utc_index",
        )
        self._collection.create_index(
            [("source_metadata.region", pymongo.ASCENDING)],
            name="source_metadata_region_index",
        )

    def save_record(self, record: RawListingRecord) -> None:
        """Insert one raw listing snapshot as an immutable MongoDB document."""

        self._collection.insert_one(record.to_serializable_dict())


_SANITIZE_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_path_component(value: str) -> str:
    """Return a stable path-safe string for filesystem storage."""

    sanitized = _SANITIZE_PATTERN.sub("-", value.strip())
    return sanitized.strip("-._") or "unknown"


def _timestamp_for_filename(value: str) -> str:
    """Convert an ISO timestamp into a filename-safe representation."""

    return value.replace(":", "-")
