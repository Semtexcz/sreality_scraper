"""Storage ports and adapters for raw listing records and failure artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Protocol

import pymongo

from scraperweb.scraper.models import DetailMarkupFailureArtifact, RawListingRecord


class RawRecordRepository(Protocol):
    """Persistence port for storing immutable raw listing snapshots."""

    def save_record(self, record: RawListingRecord) -> None:
        """Persist one raw listing snapshot."""

    def save_markup_failure_artifact(
        self,
        artifact: DetailMarkupFailureArtifact,
    ) -> None:
        """Persist one detail-page markup failure artifact."""


class FilesystemRawRecordRepository:
    """Persist raw listing snapshots and failure artifacts on the local filesystem."""

    def __init__(self, output_dir: Path) -> None:
        """Store the configured filesystem root and ensure it exists."""

        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def save_record(self, record: RawListingRecord) -> None:
        """Persist one raw listing snapshot into a listing-specific directory."""

        listing_directory = self._build_listing_directory(
            region=record.source_metadata.region,
            listing_id=record.listing_id,
        )

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

    def save_markup_failure_artifact(
        self,
        artifact: DetailMarkupFailureArtifact,
    ) -> None:
        """Persist one detail-page markup failure artifact beside raw records."""

        listing_directory = self._build_listing_directory(
            region=artifact.source_metadata.region,
            listing_id=artifact.listing_id,
        )
        base_name = _timestamp_for_filename(artifact.captured_at_utc.isoformat())
        metadata_path = listing_directory / f"{base_name}.markup-failure.json"
        snapshot_path = listing_directory / f"{base_name}.markup-failure.html"

        with metadata_path.open("w", encoding="utf-8") as output_file:
            json.dump(
                artifact.to_serializable_dict(),
                output_file,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            output_file.write("\n")

        snapshot_path.write_text(artifact.raw_page_snapshot, encoding="utf-8")

    def _build_listing_directory(self, region: str, listing_id: str) -> Path:
        """Return the stable filesystem directory for one listing."""

        listing_directory = (
            self._output_dir
            / _sanitize_path_component(region)
            / _sanitize_path_component(listing_id)
        )
        listing_directory.mkdir(parents=True, exist_ok=True)
        return listing_directory


class MongoRawRecordRepository:
    """Persist raw listing snapshots and failure artifacts as MongoDB documents."""

    def __init__(
        self,
        mongodb_uri: str,
        mongodb_database: str,
        collection_name: str = "raw_listings",
        markup_failure_collection_name: str = "raw_listing_markup_failures",
    ) -> None:
        """Create a MongoDB client and prepare collection indexes."""

        self._client = pymongo.MongoClient(mongodb_uri)
        self._collection = self._client[mongodb_database][collection_name]
        self._markup_failure_collection = self._client[mongodb_database][
            markup_failure_collection_name
        ]
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
        self._markup_failure_collection.create_index(
            [("listing_id", pymongo.ASCENDING), ("captured_at_utc", pymongo.ASCENDING)],
            unique=True,
            name="listing_id_captured_at_utc_unique",
        )
        self._markup_failure_collection.create_index(
            [("captured_at_utc", pymongo.ASCENDING)],
            name="captured_at_utc_index",
        )
        self._markup_failure_collection.create_index(
            [("source_metadata.region", pymongo.ASCENDING)],
            name="source_metadata_region_index",
        )

    def save_record(self, record: RawListingRecord) -> None:
        """Insert one raw listing snapshot as an immutable MongoDB document."""

        self._collection.insert_one(record.to_serializable_dict())

    def save_markup_failure_artifact(
        self,
        artifact: DetailMarkupFailureArtifact,
    ) -> None:
        """Insert one detail-page markup failure artifact as an immutable document."""

        self._markup_failure_collection.insert_one(artifact.to_serializable_dict())


_SANITIZE_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_path_component(value: str) -> str:
    """Return a stable path-safe string for filesystem storage."""

    sanitized = _SANITIZE_PATTERN.sub("-", value.strip())
    return sanitized.strip("-._") or "unknown"


def _timestamp_for_filename(value: str) -> str:
    """Convert an ISO timestamp into a filename-safe representation."""

    return value.replace(":", "-")
