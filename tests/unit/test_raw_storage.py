"""Tests for raw storage models, adapters, and runtime wiring."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from scraperweb.application.acquisition_service import RawAcquisitionService
from scraperweb.cli_runtime_options import RuntimeCliOptions, StorageBackend
from scraperweb.estate_scraper import build_raw_record_repository
from scraperweb.persistence.repositories import FilesystemRawRecordRepository, MongoRawRecordRepository
from scraperweb.progress import ScrapeProgressReporter
from scraperweb.scraper.exceptions import ScraperResponseError, ScraperTransportError
from scraperweb.scraper.models import (
    DetailMarkupFailureArtifact,
    RawListingRecord,
    RawSourceMetadata,
)
from scraperweb.scraper.parsers import SrealityDetailPageParser, SrealityListingPageParser
from scraperweb.scraper.runtime import ListingPageStopDiagnostics, RawListingCollector


class FakeListingPageClient:
    """Return deterministic listing HTML for orchestration tests."""

    def __init__(self, html_by_url: dict[str, str]) -> None:
        """Store fake listing page responses."""

        self._html_by_url = html_by_url
        self.calls: list[str] = []

    def fetch(self, url: str) -> str:
        """Return the configured HTML response for the requested URL."""

        self.calls.append(url)
        return self._html_by_url[url]


class FakeDetailPageClient:
    """Return deterministic detail HTML for orchestration tests."""

    def __init__(self, html_by_url: dict[str, str]) -> None:
        """Store fake detail page responses."""

        self._html_by_url = html_by_url

    def fetch(self, url: str) -> str:
        """Return the configured HTML response for the requested URL."""

        return self._html_by_url[url]


class FakeListingPageParser:
    """Parse deterministic fake listing HTML into pagination hints and URLs."""

    def parse_range_of_estates(self, listing_html: str) -> int:
        """Extract the configured pagination hint from fake HTML."""

        lines = listing_html.splitlines()
        return int(lines[0].split(":", maxsplit=1)[1])

    def parse_estate_urls(self, listing_html: str) -> list[str]:
        """Extract fake estate URLs from fake HTML."""

        return [line for line in listing_html.splitlines()[1:] if line]


class FakeDetailPageParser:
    """Produce deterministic raw payloads from fake detail HTML."""

    def parse_raw_payload(self, detail_html: str) -> dict[str, Any]:
        """Convert fake detail HTML into a raw payload dictionary."""

        return {"payload": detail_html}


class RecordingRepository:
    """Collect stored records for assertions."""

    def __init__(self) -> None:
        """Initialize empty in-memory storage."""

        self.records: list[RawListingRecord] = []
        self.markup_failure_artifacts: list[DetailMarkupFailureArtifact] = []

    def save_record(self, record: RawListingRecord) -> None:
        """Record each stored raw listing snapshot."""

        self.records.append(record)

    def save_markup_failure_artifact(
        self,
        artifact: DetailMarkupFailureArtifact,
    ) -> None:
        """Record each stored detail-page markup failure artifact."""

        self.markup_failure_artifacts.append(artifact)

    def has_listing_record(self, *, region: str, listing_id: str, source_url: str) -> bool:
        """Return whether a matching stored raw record already exists."""

        del source_url
        return any(
            record.listing_id == listing_id and record.source_metadata.region == region
            for record in self.records
        )


class RecordingLogger:
    """Collect acquisition error logs for assertions."""

    def __init__(self) -> None:
        """Initialize captured error log calls."""

        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    def error(self, message: str, *args: Any) -> None:
        """Record one error log call."""

        self.calls.append((message, args))

    def debug(self, message: str, *args: Any) -> None:
        """Ignore debug logs emitted by the production logger surface."""

        del message, args

    def info(self, message: str, *args: Any) -> None:
        """Ignore info logs emitted by the production logger surface."""

        del message, args


class RecordingProgressReporter(ScrapeProgressReporter):
    """Capture listing traversal stop diagnostics for assertions."""

    def __init__(self) -> None:
        """Initialize empty captured stop events."""

        self.stop_events: list[tuple[str, ListingPageStopDiagnostics]] = []
        self.skipped_existing_events: list[tuple[str, int, int, str]] = []
        self.completed_regions: list[tuple[str, int, int]] = []

    def listing_traversal_stopped(
        self,
        *,
        region_slug: str,
        diagnostics: ListingPageStopDiagnostics,
    ) -> None:
        """Record each traversal stop event."""

        self.stop_events.append((region_slug, diagnostics))

    def existing_listing_skipped(
        self,
        *,
        region_slug: str,
        page_number: int,
        total_skipped: int,
        listing_url: str,
    ) -> None:
        """Record each resume-mode skip event."""

        self.skipped_existing_events.append(
            (region_slug, page_number, total_skipped, listing_url),
        )

    def region_completed(
        self,
        *,
        region_slug: str,
        processed_estates: int,
        skipped_existing_estates: int,
    ) -> None:
        """Record the final region summary."""

        self.completed_regions.append(
            (region_slug, processed_estates, skipped_existing_estates),
        )


class FailingListingPageClient:
    """Raise a configured scraper HTTP error for every listing-page fetch."""

    def __init__(self, error: ScraperTransportError | ScraperResponseError) -> None:
        """Store the scraper-owned HTTP error to raise."""

        self._error = error

    def fetch(self, url: str) -> str:
        """Raise the configured scraper-owned error."""

        raise self._error


class FailingDetailPageClient:
    """Raise a configured scraper HTTP error for every detail-page fetch."""

    def __init__(self, error: ScraperTransportError | ScraperResponseError) -> None:
        """Store the scraper-owned HTTP error to raise."""

        self._error = error

    def fetch(self, url: str) -> str:
        """Raise the configured scraper-owned error."""

        raise self._error


class RecordingDetailPageParser:
    """Produce nested JSON-safe payloads from fake detail HTML."""

    def parse_raw_payload(self, detail_html: str) -> dict[str, Any]:
        """Convert fake detail HTML into a nested raw payload dictionary."""

        return {
            "payload": detail_html,
            "sections": [
                {"label": "Disposition", "value": "2+kk"},
                {"label": "Area", "value": "58 m2"},
            ],
            "has_elevator": True,
            "note": None,
        }


class SourceCoordinateDetailPageParser:
    """Produce raw payloads that already include the approved source coordinate object."""

    def parse_raw_payload(self, detail_html: str) -> dict[str, Any]:
        """Convert fake detail HTML into a raw payload with source-backed coordinates."""

        return {
            "payload": detail_html,
            "source_coordinates": {
                "latitude": 50.0577347,
                "longitude": 14.3723456,
                "source": "detail_locality_payload",
                "precision": "listing",
            },
        }


class FakeCollection:
    """Minimal MongoDB collection stub for repository tests."""

    def __init__(self) -> None:
        """Initialize captured inserts and index declarations."""

        self.created_indexes: list[tuple[tuple[tuple[str, int], ...], dict[str, Any]]] = []
        self.inserted_documents: list[dict[str, Any]] = []

    def create_index(self, keys: list[tuple[str, int]], **kwargs: Any) -> None:
        """Capture index creation calls."""

        self.created_indexes.append((tuple(keys), kwargs))

    def insert_one(self, document: dict[str, Any]) -> None:
        """Capture inserted documents."""

        self.inserted_documents.append(document)

    def find_one(
        self,
        query: dict[str, Any],
        projection: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Return the first inserted document that matches a minimal query subset."""

        del projection
        for document in self.inserted_documents:
            if all(_read_nested_value(document, key) == value for key, value in query.items()):
                return document
        return None


class FakeDatabase:
    """Minimal MongoDB database stub for repository tests."""

    def __init__(self, collection: FakeCollection) -> None:
        """Store the collection returned for all collection lookups."""

        self._collection = collection

    def __getitem__(self, name: str) -> FakeCollection:
        """Return the configured fake collection."""

        return self._collection


class FakeMongoClient:
    """Minimal MongoDB client stub for repository tests."""

    def __init__(self, collection: FakeCollection) -> None:
        """Store the fake database exposed by the client."""

        self._database = FakeDatabase(collection)

    def __getitem__(self, name: str) -> FakeDatabase:
        """Return the configured fake database."""

        return self._database


def _read_nested_value(document: dict[str, Any], dotted_key: str) -> Any:
    """Return a nested dictionary value selected by dotted-key notation."""

    value: Any = document
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


@pytest.fixture
def sample_record() -> RawListingRecord:
    """Return a representative raw listing record for storage tests."""

    return RawListingRecord(
        listing_id="1234567890",
        source_url="https://www.sreality.cz/detail/prodej/byt/1234567890",
        captured_at_utc=datetime(2026, 3, 17, 11, 22, 33, tzinfo=timezone.utc),
        source_payload={
            "Nazev": "Byt 2+kk",
            "Cena": "7500000",
            "source_coordinates": {
                "latitude": 50.0577347,
                "longitude": 14.3723456,
                "source": "detail_locality_payload",
                "precision": "listing",
            },
        },
        source_metadata=RawSourceMetadata(
            region="praha",
            listing_page_number=2,
            scrape_run_id="run-001",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot="<html>detail</html>",
    )


def test_filesystem_repository_stores_json_and_optional_snapshot(
    tmp_path: Path,
    sample_record: RawListingRecord,
) -> None:
    """Persist JSON records and sibling HTML snapshots for filesystem storage."""

    repository = FilesystemRawRecordRepository(tmp_path)

    repository.save_record(sample_record)

    listing_directory = tmp_path / "praha" / "1234567890"
    stored_files = sorted(path.name for path in listing_directory.iterdir())

    assert stored_files == ["2026-03-17T11-22-33+00-00.html", "2026-03-17T11-22-33+00-00.json"]

    stored_record = json.loads((listing_directory / stored_files[1]).read_text(encoding="utf-8"))
    assert stored_record["listing_id"] == sample_record.listing_id
    assert stored_record["captured_at_utc"] == "2026-03-17T11:22:33+00:00"
    assert stored_record["source_metadata"]["region"] == "praha"
    assert stored_record["source_payload"]["source_coordinates"] == {
        "latitude": 50.0577347,
        "longitude": 14.3723456,
        "source": "detail_locality_payload",
        "precision": "listing",
    }
    assert (listing_directory / stored_files[0]).read_text(encoding="utf-8") == "<html>detail</html>"


def test_filesystem_repository_sanitizes_paths_and_preserves_raw_payload(
    tmp_path: Path,
) -> None:
    """Sanitize storage paths without mutating the serialized raw source payload."""

    record = RawListingRecord(
        listing_id=" detail id / 42 ",
        source_url="https://www.sreality.cz/detail/prodej/byt/detail-id-42",
        captured_at_utc=datetime(2026, 3, 17, 14, 0, 0, tzinfo=timezone.utc),
        source_payload={
            "Název": "Byt 2+kk",
            "Vybavení": ["Sklep", "Balkon"],
            "Cena": {"částka": "8 490 000 Kč"},
        },
        source_metadata=RawSourceMetadata(
            region=" Praha / Karlín ",
            listing_page_number=1,
            scrape_run_id="run-raw",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    repository = FilesystemRawRecordRepository(tmp_path)

    repository.save_record(record)

    json_path = (
        tmp_path
        / "Praha-Karl-n"
        / "detail-id-42"
        / "2026-03-17T14-00-00+00-00.json"
    )
    stored_record = json.loads(json_path.read_text(encoding="utf-8"))

    assert stored_record["source_payload"] == {
        "Název": "Byt 2+kk",
        "Vybavení": ["Sklep", "Balkon"],
        "Cena": {"částka": "8 490 000 Kč"},
    }
    assert not json_path.with_suffix(".html").exists()


def test_filesystem_repository_detects_existing_listing_records(
    tmp_path: Path,
    sample_record: RawListingRecord,
) -> None:
    """Treat one persisted raw JSON snapshot as an existing listing for resume mode."""

    repository = FilesystemRawRecordRepository(tmp_path)
    repository.save_record(sample_record)

    assert repository.has_listing_record(
        region="praha",
        listing_id="1234567890",
        source_url=sample_record.source_url,
    ) is True
    assert repository.has_listing_record(
        region="brno",
        listing_id="1234567890",
        source_url=sample_record.source_url,
    ) is False


def test_filesystem_repository_ignores_markup_failure_artifacts_for_existence_checks(
    tmp_path: Path,
) -> None:
    """Do not treat markup-failure artifacts as successfully persisted raw records."""

    repository = FilesystemRawRecordRepository(tmp_path)
    repository.save_markup_failure_artifact(
        DetailMarkupFailureArtifact(
            listing_id="123",
            source_url="https://www.sreality.cz/detail/prodej/byt/praha/123",
            captured_at_utc=datetime(2026, 3, 19, 10, 0, 0, tzinfo=timezone.utc),
            raw_page_snapshot="<html>broken</html>",
            failure_message="missing title",
            source_metadata=RawSourceMetadata(
                region="praha",
                listing_page_number=1,
                scrape_run_id="run-markup-failure",
                http_status=200,
                parser_version="sreality-detail-v1",
                captured_from="detail_page",
            ),
        ),
    )

    assert repository.has_listing_record(
        region="praha",
        listing_id="123",
        source_url="https://www.sreality.cz/detail/prodej/byt/praha/123",
    ) is False


def test_mongo_repository_creates_expected_indexes_and_inserts_document(
    monkeypatch: pytest.MonkeyPatch,
    sample_record: RawListingRecord,
) -> None:
    """Configure the expected MongoDB indexes and insert serialized records."""

    fake_collection = FakeCollection()

    def fake_mongo_client(uri: str) -> FakeMongoClient:
        """Return a deterministic fake client for repository construction."""

        assert uri == "mongodb://example.test:27017"
        return FakeMongoClient(fake_collection)

    monkeypatch.setattr("scraperweb.persistence.repositories.pymongo.MongoClient", fake_mongo_client)

    repository = MongoRawRecordRepository(
        mongodb_uri="mongodb://example.test:27017",
        mongodb_database="RawListings",
    )
    repository.save_record(sample_record)

    assert len(fake_collection.created_indexes) == 6
    assert fake_collection.inserted_documents[0]["listing_id"] == "1234567890"
    assert fake_collection.inserted_documents[0]["captured_at_utc"] == "2026-03-17T11:22:33+00:00"


def test_mongo_repository_detects_existing_listing_records(
    monkeypatch: pytest.MonkeyPatch,
    sample_record: RawListingRecord,
) -> None:
    """Check MongoDB for a same-region listing before resume-mode downloads."""

    fake_collection = FakeCollection()

    def fake_mongo_client(uri: str) -> FakeMongoClient:
        """Return a deterministic fake client for repository construction."""

        assert uri == "mongodb://example.test:27017"
        return FakeMongoClient(fake_collection)

    monkeypatch.setattr("scraperweb.persistence.repositories.pymongo.MongoClient", fake_mongo_client)

    repository = MongoRawRecordRepository(
        mongodb_uri="mongodb://example.test:27017",
        mongodb_database="RawListings",
    )
    repository.save_record(sample_record)

    assert repository.has_listing_record(
        region="praha",
        listing_id="1234567890",
        source_url=sample_record.source_url,
    ) is True
    assert repository.has_listing_record(
        region="brno",
        listing_id="1234567890",
        source_url=sample_record.source_url,
    ) is False


def test_raw_listing_collector_emits_source_faithful_raw_records() -> None:
    """Emit scraper-owned raw records before any persistence-specific adaptation."""

    collector = RawListingCollector(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": "pages:1\nhttps://detail/1",
            },
        ),
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail payload</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=RecordingDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-123",
        capture_raw_page_snapshots=True,
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/praha?strana=",
            max_pages=1,
        ),
    )

    assert len(collected_records) == 1
    collected_record = collected_records[0]
    assert collected_record.listing_id == "1"
    assert collected_record.source_metadata.region == "praha"
    assert collected_record.source_metadata.listing_page_number == 1
    assert collected_record.source_metadata.scrape_run_id == "run-123"
    assert collected_record.source_metadata.parser_version == "sreality-detail-v1"
    assert collected_record.raw_page_snapshot == "<html>detail payload</html>"
    assert collected_record.source_payload == {
        "payload": "<html>detail payload</html>",
        "sections": [
            {"label": "Disposition", "value": "2+kk"},
            {"label": "Area", "value": "58 m2"},
        ],
        "has_elevator": True,
        "note": None,
    }
    assert "price_per_square_meter" not in collected_record.to_serializable_dict()
    json.dumps(collected_record.to_serializable_dict())


def test_raw_listing_collector_preserves_structured_source_coordinates() -> None:
    """Emit the approved raw source coordinate object verbatim for future replay."""

    collector = RawListingCollector(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": "pages:1\nhttps://detail/1",
            },
        ),
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail payload</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=SourceCoordinateDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-124",
        capture_raw_page_snapshots=False,
    )

    collected_record = next(
        collector.collect_region_records(
            district_link="https://example.test/praha?strana=",
            max_pages=1,
        ),
    )

    assert collected_record.source_payload["source_coordinates"] == {
        "latitude": 50.0577347,
        "longitude": 14.3723456,
        "source": "detail_locality_payload",
        "precision": "listing",
    }

    assert collected_record.to_serializable_dict()["source_payload"]["source_coordinates"] == {
        "latitude": 50.0577347,
        "longitude": 14.3723456,
        "source": "detail_locality_payload",
        "precision": "listing",
    }


def test_raw_listing_collector_stops_on_repeated_listing_page_signature() -> None:
    """Stop region traversal when a later page repeats an earlier estate URL set."""

    listing_page_client = FakeListingPageClient(
        {
            "https://example.test/praha?strana=1": (
                "pages:5\nhttps://detail/1\nhttps://detail/2"
            ),
            "https://example.test/praha?strana=2": (
                "pages:5\nhttps://detail/3\nhttps://detail/4"
            ),
            "https://example.test/praha?strana=3": (
                "pages:5\nhttps://detail/3\nhttps://detail/4"
            ),
        },
    )
    collector = RawListingCollector(
        listing_page_client=listing_page_client,
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
                "https://detail/3": "<html>detail 3</html>",
                "https://detail/4": "<html>detail 4</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-repeat",
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/praha?strana=",
            max_pages=5,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["1", "2", "3", "4"]
    assert listing_page_client.calls == [
        "https://example.test/praha?strana=1",
        "https://example.test/praha?strana=2",
        "https://example.test/praha?strana=3",
    ]


def test_raw_listing_collector_without_page_limit_relies_on_stop_conditions() -> None:
    """Traverse unbounded page numbers until observed listing outcomes stop the run."""

    listing_page_client = FakeListingPageClient(
        {
            "https://example.test/praha?strana=1": "pages:9\nhttps://detail/1",
            "https://example.test/praha?strana=2": "pages:9\nhttps://detail/2",
            "https://example.test/praha?strana=3": "pages:9\nhttps://detail/2",
        },
    )
    collector = RawListingCollector(
        listing_page_client=listing_page_client,
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-unbounded",
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/praha?strana=",
            max_pages=None,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["1", "2"]
    assert listing_page_client.calls == [
        "https://example.test/praha?strana=1",
        "https://example.test/praha?strana=2",
        "https://example.test/praha?strana=3",
    ]


def test_raw_listing_collector_stops_on_empty_listing_page() -> None:
    """Stop region traversal when the parser reports an empty listing page."""

    collector = RawListingCollector(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": (
                    "pages:5\nhttps://detail/1\nhttps://detail/2"
                ),
                "https://example.test/praha?strana=2": "pages:5",
            },
        ),
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-empty-page",
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/praha?strana=",
            max_pages=5,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["1", "2"]


def test_raw_listing_collector_stops_when_listing_page_has_no_new_estates() -> None:
    """Stop region traversal when a later page contributes no unseen estate URLs."""

    listing_page_client = FakeListingPageClient(
        {
            "https://example.test/praha?strana=1": (
                "pages:5\nhttps://detail/1\nhttps://detail/2"
            ),
            "https://example.test/praha?strana=2": (
                "pages:5\nhttps://detail/2\nhttps://detail/1"
            ),
        },
    )
    collector = RawListingCollector(
        listing_page_client=listing_page_client,
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-drift",
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/praha?strana=",
            max_pages=5,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["1", "2"]
    assert listing_page_client.calls == [
        "https://example.test/praha?strana=1",
        "https://example.test/praha?strana=2",
    ]


def test_raw_listing_collector_all_czechia_tolerates_temporary_duplicate_window() -> None:
    """Keep unbounded nationwide traversal alive across one stale duplicate window."""

    listing_page_client = FakeListingPageClient(
        {
            "https://example.test/all-czechia?strana=1": (
                "pages:999\nhttps://detail/1\nhttps://detail/2"
            ),
            "https://example.test/all-czechia?strana=2": (
                "pages:999\nhttps://detail/3\nhttps://detail/4"
            ),
            "https://example.test/all-czechia?strana=3": (
                "pages:999\nhttps://detail/2\nhttps://detail/1"
            ),
            "https://example.test/all-czechia?strana=4": (
                "pages:999\nhttps://detail/5\nhttps://detail/6"
            ),
            "https://example.test/all-czechia?strana=5": "pages:999",
        },
    )
    collector = RawListingCollector(
        listing_page_client=listing_page_client,
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
                "https://detail/3": "<html>detail 3</html>",
                "https://detail/4": "<html>detail 4</html>",
                "https://detail/5": "<html>detail 5</html>",
                "https://detail/6": "<html>detail 6</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="all-czechia",
        scrape_run_id="run-all-czechia-transient-duplicate",
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/all-czechia?strana=",
            max_pages=None,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["1", "2", "3", "4", "5", "6"]
    assert listing_page_client.calls == [
        "https://example.test/all-czechia?strana=1",
        "https://example.test/all-czechia?strana=2",
        "https://example.test/all-czechia?strana=3",
        "https://example.test/all-czechia?strana=4",
        "https://example.test/all-czechia?strana=5",
    ]


def test_raw_listing_collector_all_czechia_stops_after_repeated_tail_page() -> None:
    """Stop unbounded nationwide traversal on a repeated duplicate-tail signature."""

    progress_reporter = RecordingProgressReporter()
    listing_page_client = FakeListingPageClient(
        {
            "https://example.test/all-czechia?strana=1": (
                "pages:999\nhttps://detail/1\nhttps://detail/2"
            ),
            "https://example.test/all-czechia?strana=2": (
                "pages:999\nhttps://detail/3\nhttps://detail/4"
            ),
            "https://example.test/all-czechia?strana=3": (
                "pages:999\nhttps://detail/2\nhttps://detail/1"
            ),
            "https://example.test/all-czechia?strana=4": (
                "pages:999\nhttps://detail/2\nhttps://detail/1"
            ),
        },
    )
    collector = RawListingCollector(
        listing_page_client=listing_page_client,
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
                "https://detail/3": "<html>detail 3</html>",
                "https://detail/4": "<html>detail 4</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="all-czechia",
        scrape_run_id="run-all-czechia-repeated-tail",
        progress_reporter=progress_reporter,
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/all-czechia?strana=",
            max_pages=None,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["1", "2", "3", "4"]
    assert progress_reporter.stop_events == [
        (
            "all-czechia",
            ListingPageStopDiagnostics(
                reason="repeated_listing_page_signature",
                page_number=4,
                observed_estates=2,
                new_estates=0,
                consecutive_stale_pages=2,
                repeated_page_first_seen_at=3,
            ),
        ),
    ]


def test_raw_listing_collector_all_czechia_stops_after_stale_window_limit() -> None:
    """Stop unbounded nationwide traversal after several stale pages with no recovery."""

    progress_reporter = RecordingProgressReporter()
    listing_page_client = FakeListingPageClient(
        {
            "https://example.test/all-czechia?strana=1": (
                "pages:999\nhttps://detail/1\nhttps://detail/2"
            ),
            "https://example.test/all-czechia?strana=2": (
                "pages:999\nhttps://detail/3\nhttps://detail/4"
            ),
            "https://example.test/all-czechia?strana=3": (
                "pages:999\nhttps://detail/2\nhttps://detail/1"
            ),
            "https://example.test/all-czechia?strana=4": (
                "pages:999\nhttps://detail/4\nhttps://detail/3"
            ),
            "https://example.test/all-czechia?strana=5": (
                "pages:999\nhttps://detail/1\nhttps://detail/4"
            ),
        },
    )
    collector = RawListingCollector(
        listing_page_client=listing_page_client,
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
                "https://detail/3": "<html>detail 3</html>",
                "https://detail/4": "<html>detail 4</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="all-czechia",
        scrape_run_id="run-all-czechia-stale-limit",
        progress_reporter=progress_reporter,
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/all-czechia?strana=",
            max_pages=None,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["1", "2", "3", "4"]
    assert progress_reporter.stop_events == [
        (
            "all-czechia",
            ListingPageStopDiagnostics(
                reason="stale_listing_window_limit",
                page_number=5,
                observed_estates=2,
                new_estates=0,
                consecutive_stale_pages=3,
                repeated_page_first_seen_at=None,
            ),
        ),
    ]


def test_acquisition_service_persists_emitted_raw_records() -> None:
    """Persist scraper-emitted raw records without altering their raw payload."""

    repository = RecordingRepository()
    service = RawAcquisitionService(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": "pages:1\nhttps://detail/1",
            },
        ),
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail payload</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        raw_record_repository=repository,
        region_slug="praha",
        scrape_run_id="run-123",
        capture_raw_page_snapshots=True,
    )

    tracked_estates = service.collect_for_region(
        district_link="https://example.test/praha?strana=",
        max_pages=1,
        max_estates=10,
        tracked_estates=0,
    )

    assert tracked_estates == 1
    assert len(repository.records) == 1
    stored_record = repository.records[0]
    assert stored_record.listing_id == "1"
    assert stored_record.source_metadata.region == "praha"
    assert stored_record.source_payload == {"payload": "<html>detail payload</html>"}


def test_acquisition_service_respects_max_pages_and_max_estates_limits() -> None:
    """Stop collection when the configured page and estate bounds are reached."""

    repository = RecordingRepository()
    listing_page_client = FakeListingPageClient(
        {
            "https://example.test/praha?strana=1": (
                "pages:3\nhttps://detail/1\nhttps://detail/2"
            ),
            "https://example.test/praha?strana=2": (
                "pages:3\nhttps://detail/3\nhttps://detail/4"
            ),
        },
    )
    service = RawAcquisitionService(
        listing_page_client=listing_page_client,
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
                "https://detail/3": "<html>detail 3</html>",
                "https://detail/4": "<html>detail 4</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        raw_record_repository=repository,
        region_slug="praha",
        scrape_run_id="run-limits",
        capture_raw_page_snapshots=False,
    )

    tracked_estates = service.collect_for_region(
        district_link="https://example.test/praha?strana=",
        max_pages=2,
        max_estates=3,
        tracked_estates=0,
    )

    assert tracked_estates == 3
    assert [record.listing_id for record in repository.records] == ["1", "2", "3"]
    assert all(record.raw_page_snapshot is None for record in repository.records)


def test_acquisition_service_resume_existing_skips_detail_downloads_for_saved_listings() -> None:
    """Skip already-persisted listings before detail fetches when resume mode is enabled."""

    repository = RecordingRepository()
    existing_record = RawListingRecord(
        listing_id="1",
        source_url="https://detail/1",
        captured_at_utc=datetime(2026, 3, 19, 9, 0, 0, tzinfo=timezone.utc),
        source_payload={"payload": "<html>existing</html>"},
        source_metadata=RawSourceMetadata(
            region="praha",
            listing_page_number=1,
            scrape_run_id="run-existing",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    repository.save_record(existing_record)
    detail_page_client = FakeDetailPageClient(
        {
            "https://detail/2": "<html>detail 2</html>",
        },
    )
    progress_reporter = RecordingProgressReporter()
    service = RawAcquisitionService(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": (
                    "pages:1\nhttps://detail/1\nhttps://detail/2"
                ),
            },
        ),
        detail_page_client=detail_page_client,
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        raw_record_repository=repository,
        region_slug="praha",
        scrape_run_id="run-resume-existing",
        resume_existing=True,
        capture_raw_page_snapshots=False,
        progress_reporter=progress_reporter,
    )

    tracked_estates = service.collect_for_region(
        district_link="https://example.test/praha?strana=",
        max_pages=1,
        max_estates=10,
        tracked_estates=0,
    )

    assert tracked_estates == 1
    assert [record.listing_id for record in repository.records] == ["1", "2"]
    assert progress_reporter.skipped_existing_events == [
        ("praha", 1, 1, "https://detail/1"),
    ]
    assert progress_reporter.completed_regions == [("praha", 1, 1)]


def test_acquisition_service_collects_until_pagination_exhaustion_without_estate_limit() -> None:
    """Keep collecting records until the listing traversal itself stops."""

    repository = RecordingRepository()
    listing_page_client = FakeListingPageClient(
        {
            "https://example.test/praha?strana=1": (
                "pages:3\nhttps://detail/1\nhttps://detail/2"
            ),
            "https://example.test/praha?strana=2": (
                "pages:3\nhttps://detail/3\nhttps://detail/4"
            ),
            "https://example.test/praha?strana=3": "",
        },
    )
    service = RawAcquisitionService(
        listing_page_client=listing_page_client,
        detail_page_client=FakeDetailPageClient(
            {
                "https://detail/1": "<html>detail 1</html>",
                "https://detail/2": "<html>detail 2</html>",
                "https://detail/3": "<html>detail 3</html>",
                "https://detail/4": "<html>detail 4</html>",
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        raw_record_repository=repository,
        region_slug="praha",
        scrape_run_id="run-unbounded-estates",
        capture_raw_page_snapshots=False,
    )

    tracked_estates = service.collect_for_region(
        district_link="https://example.test/praha?strana=",
        max_pages=None,
        max_estates=None,
        tracked_estates=0,
    )

    assert tracked_estates == 4
    assert [record.listing_id for record in repository.records] == ["1", "2", "3", "4"]


def test_raw_listing_collector_preserves_listing_page_context_on_transport_failure() -> None:
    """Propagate listing-page failures with region and page context attached."""

    collector = RawListingCollector(
        listing_page_client=FailingListingPageClient(
            ScraperTransportError(
                message="timed out",
                request_url="https://example.test/praha?strana=1",
                timeout_seconds=30,
                attempts=3,
            ),
        ),
        detail_page_client=FakeDetailPageClient({}),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-transport",
    )

    with pytest.raises(ScraperTransportError) as exc_info:
        list(
            collector.collect_region_records(
                district_link="https://example.test/praha?strana=",
                max_pages=1,
            ),
        )

    assert exc_info.value.region_slug == "praha"
    assert exc_info.value.listing_page_number == 1
    assert exc_info.value.listing_url is None


def test_raw_listing_collector_preserves_detail_page_context_on_response_failure() -> None:
    """Propagate detail-page failures with region, page, and listing URL context."""

    collector = RawListingCollector(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": "pages:1\nhttps://detail/1",
            },
        ),
        detail_page_client=FailingDetailPageClient(
            ScraperResponseError(
                message="received empty response",
                request_url="https://detail/1",
                status_code=200,
            ),
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-response",
        fail_on_detail_http_error=True,
    )

    with pytest.raises(ScraperResponseError) as exc_info:
        list(
            collector.collect_region_records(
                district_link="https://example.test/praha?strana=",
                max_pages=1,
            ),
        )

    assert exc_info.value.region_slug == "praha"
    assert exc_info.value.listing_page_number == 1
    assert exc_info.value.listing_url == "https://detail/1"


def test_raw_listing_collector_skips_failed_detail_pages_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Log and skip failed detail pages so later listings still get collected."""

    recording_logger = RecordingLogger()
    monkeypatch.setattr("scraperweb.scraper.runtime.logger", recording_logger)

    class SelectiveFailingDetailPageClient:
        """Fail for one configured detail page and succeed for the rest."""

        def fetch(self, url: str) -> str:
            """Raise for one detail URL and return fake HTML for the next one."""

            if url == "https://detail/1":
                raise ScraperResponseError(
                    message="Received non-success HTTP status for 'https://detail/1': 404",
                    request_url="https://detail/1",
                    status_code=404,
                )
            return "<html>detail 2</html>"

    collector = RawListingCollector(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": (
                    "pages:1\nhttps://detail/1\nhttps://detail/2"
                ),
            },
        ),
        detail_page_client=SelectiveFailingDetailPageClient(),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-skip-detail-error",
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/praha?strana=",
            max_pages=1,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["2"]
    assert recording_logger.calls == [
        (
            "Skipping listing after scraper HTTP failure for region={} page={} listing_url={} request_url={}: {}",
            (
                "praha",
                1,
                "https://detail/1",
                "https://detail/1",
                "Received non-success HTTP status for 'https://detail/1': 404",
            ),
        ),
    ]


def test_raw_listing_collector_surfaces_listing_markup_validation_failures() -> None:
    """Convert invalid listing markup into contextual scraper response errors."""

    collector = RawListingCollector(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": "<html><body><a href=\"/search\">Search</a></body></html>",
            },
        ),
        detail_page_client=FakeDetailPageClient({}),
        listing_page_parser=SrealityListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-listing-markup",
    )

    with pytest.raises(ScraperResponseError) as exc_info:
        list(
            collector.collect_region_records(
                district_link="https://example.test/praha?strana=",
                max_pages=1,
            ),
        )

    assert exc_info.value.region_slug == "praha"
    assert exc_info.value.listing_page_number == 1
    assert exc_info.value.listing_url is None
    assert exc_info.value.request_url == "https://example.test/praha?strana=1"
    assert "expected at least one detail link" in exc_info.value.message


def test_raw_listing_collector_surfaces_detail_markup_validation_failures() -> None:
    """Convert invalid detail markup into contextual scraper response errors."""

    collector = RawListingCollector(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": (
                    "pages:1\nhttps://www.sreality.cz/detail/prodej/byt/praha/1"
                ),
            },
        ),
        detail_page_client=FakeDetailPageClient(
            {
                "https://www.sreality.cz/detail/prodej/byt/praha/1": (
                    "<html><body><dl><dt>Celková cena:</dt></dl></body></html>"
                ),
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=SrealityDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-detail-markup",
        fail_on_detail_http_error=True,
    )

    with pytest.raises(ScraperResponseError) as exc_info:
        list(
            collector.collect_region_records(
                district_link="https://example.test/praha?strana=",
                max_pages=1,
            ),
        )

    assert exc_info.value.region_slug == "praha"
    assert exc_info.value.listing_page_number == 1
    assert exc_info.value.listing_url == "https://www.sreality.cz/detail/prodej/byt/praha/1"
    assert exc_info.value.request_url == "https://www.sreality.cz/detail/prodej/byt/praha/1"
    assert "missing non-empty listing title" in exc_info.value.message


def test_raw_listing_collector_skips_detail_markup_failures_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Log and skip invalid detail markup so later listings still get collected."""

    recording_logger = RecordingLogger()
    monkeypatch.setattr("scraperweb.scraper.runtime.logger", recording_logger)

    collector = RawListingCollector(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": (
                    "pages:1\n"
                    "https://www.sreality.cz/detail/prodej/byt/praha/1\n"
                    "https://www.sreality.cz/detail/prodej/byt/praha/2"
                ),
            },
        ),
        detail_page_client=FakeDetailPageClient(
            {
                "https://www.sreality.cz/detail/prodej/byt/praha/1": (
                    "<html><body><dl><dt>Celková cena:</dt></dl></body></html>"
                ),
                "https://www.sreality.cz/detail/prodej/byt/praha/2": (
                    "<html><body><h1>Byt 2+kk</h1><dl><dt>Celková cena:</dt><dd>7 500 000 Kč</dd></dl></body></html>"
                ),
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=SrealityDetailPageParser(),
        region_slug="praha",
        scrape_run_id="run-skip-detail-markup",
    )

    collected_records = list(
        collector.collect_region_records(
            district_link="https://example.test/praha?strana=",
            max_pages=1,
        ),
    )

    assert [record.listing_id for record in collected_records] == ["2"]
    assert recording_logger.calls == [
        (
            "Skipping listing after scraper markup failure for region={} page={} listing_url={} request_url={}: {}",
            (
                "praha",
                1,
                "https://www.sreality.cz/detail/prodej/byt/praha/1",
                "https://www.sreality.cz/detail/prodej/byt/praha/1",
                "detail page validation failed: missing non-empty listing title",
            ),
        ),
    ]


def test_filesystem_repository_persists_detail_markup_failure_artifacts(
    tmp_path: Path,
) -> None:
    """Persist failed detail HTML snapshots and metadata for later inspection."""

    repository = FilesystemRawRecordRepository(tmp_path)
    service = RawAcquisitionService(
        listing_page_client=FakeListingPageClient(
            {
                "https://example.test/praha?strana=1": (
                    "pages:1\n"
                    "https://www.sreality.cz/detail/prodej/byt/praha/1"
                ),
            },
        ),
        detail_page_client=FakeDetailPageClient(
            {
                "https://www.sreality.cz/detail/prodej/byt/praha/1": (
                    "<html><body><h1>Byt 2+kk</h1><dl><dt></dt><dd>7 500 000 Kč</dd></dl></body></html>"
                ),
            },
        ),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=SrealityDetailPageParser(),
        raw_record_repository=repository,
        region_slug="praha",
        scrape_run_id="run-store-markup-failure",
        fail_on_http_error=False,
    )

    tracked_estates = service.collect_for_region(
        district_link="https://example.test/praha?strana=",
        max_pages=1,
        max_estates=10,
        tracked_estates=0,
    )

    assert tracked_estates == 0
    listing_directory = tmp_path / "praha" / "1"
    failure_snapshot_paths = sorted(listing_directory.glob("*.markup-failure.html"))
    failure_metadata_paths = sorted(listing_directory.glob("*.markup-failure.json"))
    assert len(failure_snapshot_paths) == 1
    assert len(failure_metadata_paths) == 1
    assert "Byt 2+kk" in failure_snapshot_paths[0].read_text(encoding="utf-8")

    stored_metadata = json.loads(failure_metadata_paths[0].read_text(encoding="utf-8"))
    assert stored_metadata["listing_id"] == "1"
    assert stored_metadata["failure_message"] == (
        "detail page validation failed: encountered empty attribute name or value"
    )
    assert stored_metadata["source_metadata"]["region"] == "praha"


def test_acquisition_service_logs_context_before_propagating_scraper_http_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Log failure context and re-raise scraper HTTP errors to callers."""

    recording_logger = RecordingLogger()
    monkeypatch.setattr("scraperweb.application.acquisition_service.logger", recording_logger)
    service = RawAcquisitionService(
        listing_page_client=FailingListingPageClient(
            ScraperTransportError(
                message="timed out",
                request_url="https://example.test/praha?strana=1",
                timeout_seconds=30,
                attempts=3,
            ),
        ),
        detail_page_client=FakeDetailPageClient({}),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        raw_record_repository=RecordingRepository(),
        region_slug="praha",
        scrape_run_id="run-logging",
        fail_on_http_error=True,
    )

    with pytest.raises(ScraperTransportError):
        service.collect_for_region(
            district_link="https://example.test/praha?strana=",
            max_pages=1,
            max_estates=10,
            tracked_estates=0,
        )

    assert recording_logger.calls == [
        (
            "Scraper HTTP failure for region={} page={} listing_url={} request_url={}: {}",
            (
                "praha",
                1,
                None,
                "https://example.test/praha?strana=1",
                "timed out",
            ),
        ),
    ]


def test_acquisition_service_logs_and_returns_when_fail_fast_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Log scraper HTTP failures without raising when fail-fast mode is disabled."""

    recording_logger = RecordingLogger()
    monkeypatch.setattr("scraperweb.application.acquisition_service.logger", recording_logger)
    service = RawAcquisitionService(
        listing_page_client=FailingListingPageClient(
            ScraperTransportError(
                message="timed out",
                request_url="https://example.test/praha?strana=1",
                timeout_seconds=30,
                attempts=3,
            ),
        ),
        detail_page_client=FakeDetailPageClient({}),
        listing_page_parser=FakeListingPageParser(),
        detail_page_parser=FakeDetailPageParser(),
        raw_record_repository=RecordingRepository(),
        region_slug="praha",
        scrape_run_id="run-nonfatal-http",
        fail_on_http_error=False,
    )

    tracked_estates = service.collect_for_region(
        district_link="https://example.test/praha?strana=",
        max_pages=1,
        max_estates=10,
        tracked_estates=4,
    )

    assert tracked_estates == 4
    assert recording_logger.calls == [
        (
            "Scraper HTTP failure for region={} page={} listing_url={} request_url={}: {}",
            (
                "praha",
                1,
                None,
                "https://example.test/praha?strana=1",
                "timed out",
            ),
        ),
    ]


def test_build_raw_record_repository_uses_filesystem_backend(tmp_path: Path) -> None:
    """Build the filesystem repository when runtime options select it."""

    repository = build_raw_record_repository(
        RuntimeCliOptions(
            regions=("praha",),
            max_pages=1,
            max_estates=1,
            resume_existing=False,
            fail_on_http_error=False,
            verbose=False,
            quiet=False,
            storage_backend=StorageBackend.FILESYSTEM,
            mongodb_uri=None,
            mongodb_database=None,
            output_dir=tmp_path,
        ),
    )

    assert isinstance(repository, FilesystemRawRecordRepository)


def test_build_raw_record_repository_uses_mongodb_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    """Build the MongoDB repository when runtime options select it."""

    fake_collection = FakeCollection()

    def fake_mongo_client(uri: str) -> FakeMongoClient:
        """Return a deterministic fake client for repository construction."""

        assert uri == "mongodb://example.test:27017"
        return FakeMongoClient(fake_collection)

    monkeypatch.setattr("scraperweb.persistence.repositories.pymongo.MongoClient", fake_mongo_client)

    repository = build_raw_record_repository(
        RuntimeCliOptions(
            regions=("praha",),
            max_pages=1,
            max_estates=1,
            resume_existing=False,
            fail_on_http_error=False,
            verbose=False,
            quiet=False,
            storage_backend=StorageBackend.MONGODB,
            mongodb_uri="mongodb://example.test:27017",
            mongodb_database="RawListings",
            output_dir=None,
        ),
    )

    assert isinstance(repository, MongoRawRecordRepository)
