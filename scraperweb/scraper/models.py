"""Typed scraper-stage contracts for raw listing capture."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import TypeAlias


JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass(frozen=True)
class RawSourceMetadata:
    """Capture metadata attached to one raw listing snapshot."""

    region: str
    listing_page_number: int
    scrape_run_id: str
    http_status: int
    parser_version: str
    captured_from: str


@dataclass(frozen=True)
class RawListingRecord:
    """Canonical raw listing record produced by the scraper stage."""

    listing_id: str
    source_url: str
    captured_at_utc: datetime
    source_payload: dict[str, JsonValue]
    source_metadata: RawSourceMetadata
    raw_page_snapshot: str | None = None

    def to_serializable_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-serializable representation of the record."""

        serialized = asdict(self)
        serialized["captured_at_utc"] = self.captured_at_utc.astimezone(
            timezone.utc,
        ).isoformat()
        return serialized
