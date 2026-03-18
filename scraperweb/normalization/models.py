"""Typed normalization-stage contracts.

Missing source values are represented as ``None`` in known typed fields. When a raw
field can only be partially decomposed, the parsed sub-fields are populated and the
remaining known fields stay ``None``. Unmapped or source-specific raw values are
preserved verbatim under ``source_specific_attributes`` so downstream consumers keep
traceability without depending on source-shaped payloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from scraperweb.scraper.models import JsonValue


@dataclass(frozen=True)
class NormalizedPrice:
    """Stable price fields copied from raw source text without numeric derivation."""

    amount_text: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class NormalizedBuilding:
    """Stable building fields extracted from raw source facts only."""

    material: str | None = None
    condition: str | None = None
    energy_efficiency_class: str | None = None


@dataclass(frozen=True)
class NormalizedCoreAttributes:
    """Stable property attributes with source-specific overflow preserved explicitly."""

    title: str | None = None
    price: NormalizedPrice = field(default_factory=NormalizedPrice)
    building: NormalizedBuilding = field(default_factory=NormalizedBuilding)
    source_specific_attributes: dict[str, JsonValue] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedLocation:
    """Structured location fields derived directly from raw listing text."""

    location_text: str | None = None
    city: str | None = None
    city_district: str | None = None


@dataclass(frozen=True)
class NormalizedAreaDetails:
    """Structured area fields parsed directly from the raw detail payload."""

    source_text: str | None = None
    usable_area_sqm: float | None = None
    total_area_sqm: float | None = None
    built_up_area_sqm: float | None = None
    garden_area_sqm: float | None = None
    unparsed_fragments: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NormalizedOwnership:
    """Ownership fields copied directly from the raw detail payload."""

    ownership_type: str | None = None


@dataclass(frozen=True)
class NormalizedListingLifecycle:
    """Listing lifecycle dates parsed directly from raw source text."""

    listed_on: date | None = None
    listed_on_text: str | None = None
    updated_on: date | None = None
    updated_on_text: str | None = None


@dataclass(frozen=True)
class NormalizedSourceIdentifiers:
    """Source-side listing identifiers preserved from the raw detail payload."""

    source_listing_reference: str | None = None


@dataclass(frozen=True)
class NormalizationMetadata:
    """Traceability metadata linking the normalized record back to its raw capture."""

    source_contract_version: str
    source_parser_version: str
    source_region: str
    source_listing_page_number: int
    source_scrape_run_id: str
    source_captured_from: str
    source_http_status: int


@dataclass(frozen=True)
class NormalizedListingRecord:
    """Canonical normalization-stage output contract."""

    listing_id: str
    source_url: str
    captured_at_utc: datetime
    normalized_at_utc: datetime
    normalization_version: str
    core_attributes: NormalizedCoreAttributes
    location: NormalizedLocation
    normalization_metadata: NormalizationMetadata
    area_details: NormalizedAreaDetails = field(default_factory=NormalizedAreaDetails)
    ownership: NormalizedOwnership = field(default_factory=NormalizedOwnership)
    listing_lifecycle: NormalizedListingLifecycle = field(
        default_factory=NormalizedListingLifecycle,
    )
    source_identifiers: NormalizedSourceIdentifiers = field(
        default_factory=NormalizedSourceIdentifiers,
    )
