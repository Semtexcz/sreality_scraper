"""Typed normalization-stage contracts.

Missing source values are represented as ``None`` in known typed fields. When a raw
field can only be partially decomposed, the parsed sub-fields are populated and the
remaining known fields stay ``None``. Unmapped or source-specific raw values are
preserved verbatim under ``source_specific_attributes`` so downstream consumers keep
traceability without depending on source-shaped payloads.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from datetime import timezone

from scraperweb.scraper.models import JsonValue


@dataclass(frozen=True)
class NormalizedPrice:
    """Stable price fields copied from raw source text without business derivation."""

    amount_text: str | None = None
    amount_czk: int | None = None
    currency_code: str | None = None
    pricing_mode: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class NormalizedBuilding:
    """Stable building fields extracted from raw source facts only."""

    source_text: str | None = None
    material: str | None = None
    structural_attributes: tuple[str, ...] = field(default_factory=tuple)
    physical_condition: str | None = None
    floor_position: int | None = None
    total_floor_count: int | None = None
    underground_floor_count: int | None = None
    unparsed_fragments: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NormalizedEnergyDetails:
    """Structured energy-efficiency fields parsed directly from raw source text."""

    source_text: str | None = None
    efficiency_class: str | None = None
    regulation_reference: str | None = None
    consumption_kwh_per_sqm_year: float | None = None
    additional_descriptors: tuple[str, ...] = field(default_factory=tuple)
    unparsed_fragments: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NormalizedCoreAttributes:
    """Stable property attributes with source-specific overflow preserved explicitly."""

    title: str | None = None
    price: NormalizedPrice = field(default_factory=NormalizedPrice)
    building: NormalizedBuilding = field(default_factory=NormalizedBuilding)
    source_specific_attributes: dict[str, JsonValue] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedLocation:
    """Structured location fields with explicit source provenance per value."""

    location_text: str | None = None
    location_text_source: str | None = None
    city: str | None = None
    city_source: str | None = None
    city_district: str | None = None
    city_district_source: str | None = None
    location_descriptor: str | None = None
    location_descriptor_source: str | None = None
    nearby_places: tuple["NormalizedNearbyPlace", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NormalizedNearbyPlace:
    """Structured one nearby-place fact copied from supported source payload keys."""

    category: str
    source_key: str
    source_text: str
    name: str | None = None
    distance_m: int | None = None


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
    energy_details: NormalizedEnergyDetails = field(
        default_factory=NormalizedEnergyDetails,
    )
    ownership: NormalizedOwnership = field(default_factory=NormalizedOwnership)
    listing_lifecycle: NormalizedListingLifecycle = field(
        default_factory=NormalizedListingLifecycle,
    )
    source_identifiers: NormalizedSourceIdentifiers = field(
        default_factory=NormalizedSourceIdentifiers,
    )

    def to_serializable_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-serializable representation of the normalized record."""

        return _serialize_json_value(asdict(self))


def _serialize_json_value(value: object) -> JsonValue:
    """Convert nested dataclass output into JSON-compatible primitives."""

    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {
            str(key): _serialize_json_value(nested_value)
            for key, nested_value in value.items()
        }
    if isinstance(value, list):
        return [_serialize_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize_json_value(item) for item in value]
    return value  # type: ignore[return-value]
