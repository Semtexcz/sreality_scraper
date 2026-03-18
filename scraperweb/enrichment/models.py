"""Typed enrichment-stage contracts.

The enrichment stage computes explicit derived features from normalized records only.
It preserves the full normalized input record for traceability so downstream
consumers can inspect original normalized values alongside derived fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from scraperweb.normalization.models import NormalizedListingRecord


@dataclass(frozen=True)
class EnrichedPriceFeatures:
    """Derived price features computed from normalized price text fields."""

    asking_price_czk: int | None = None
    price_per_square_meter_czk: float | None = None
    price_per_usable_sqm_czk: float | None = None
    price_per_total_sqm_czk: float | None = None
    has_price_note: bool = False


@dataclass(frozen=True)
class EnrichedPropertyFeatures:
    """Derived listing features computed from normalized listing fields."""

    disposition: str | None = None
    canonical_area_sqm: float | None = None
    usable_area_sqm: float | None = None
    total_area_sqm: float | None = None
    floor_area_sqm: float | None = None
    is_ground_floor: bool | None = None
    is_upper_floor: bool | None = None
    relative_floor_position: str | None = None
    is_top_floor: bool | None = None
    is_new_build: bool | None = None
    building_material_bucket: str | None = None
    building_condition_bucket: str | None = None
    energy_efficiency_bucket: str | None = None
    has_energy_efficiency_rating: bool = False
    has_city_district: bool = False
    is_prague_listing: bool = False


@dataclass(frozen=True)
class EnrichedLocationFeatures:
    """Reference-backed location features derived during enrichment."""

    municipality_name: str | None = None
    municipality_code: str | None = None
    district_name: str | None = None
    district_code: str | None = None
    region_name: str | None = None
    region_code: str | None = None
    orp_name: str | None = None
    orp_code: str | None = None
    municipality_latitude: float | None = None
    municipality_longitude: float | None = None
    distance_to_okresni_mesto_km: float | None = None
    distance_to_orp_center_km: float | None = None
    is_district_city: bool | None = None
    is_orp_center: bool | None = None
    city_district_normalized: str | None = None
    municipality_match_status: str = "unmatched"
    municipality_match_method: str | None = None
    municipality_match_input: str | None = None
    municipality_match_candidates: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EnrichmentMetadata:
    """Traceability metadata for enrichment outputs."""

    enriched_at_utc: datetime
    source_normalization_version: str
    derivation_notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EnrichedListingRecord:
    """Canonical enrichment-stage output contract."""

    listing_id: str
    source_url: str
    captured_at_utc: datetime
    enrichment_version: str
    normalized_record: NormalizedListingRecord
    price_features: EnrichedPriceFeatures = field(default_factory=EnrichedPriceFeatures)
    property_features: EnrichedPropertyFeatures = field(
        default_factory=EnrichedPropertyFeatures,
    )
    location_features: EnrichedLocationFeatures = field(
        default_factory=EnrichedLocationFeatures,
    )
    enrichment_metadata: EnrichmentMetadata | None = None
