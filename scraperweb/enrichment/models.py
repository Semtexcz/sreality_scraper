"""Typed enrichment-stage contracts.

The enrichment stage computes explicit derived features from normalized records only.
It preserves the full normalized input record for traceability so downstream
consumers can inspect original normalized values alongside derived fields.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone

from scraperweb.scraper.models import JsonValue
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
    has_balcony: bool | None = None
    has_loggia: bool | None = None
    has_terrace: bool | None = None
    has_cellar: bool | None = None
    has_elevator: bool | None = None
    is_barrier_free: bool | None = None
    outdoor_accessory_area_sqm: float | None = None
    furnishing_bucket: str | None = None
    has_city_district: bool = False
    is_prague_listing: bool = False


@dataclass(frozen=True)
class EnrichedLocationFeatures:
    """Reference-backed location features derived during enrichment."""

    street: str | None = None
    street_source: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_precision: str | None = None
    geocoding_source: str | None = None
    geocoding_confidence: str | None = None
    geocoding_match_strategy: str | None = None
    geocoding_query_text: str | None = None
    geocoding_query_text_source: str | None = None
    resolved_address_text: str | None = None
    resolved_street: str | None = None
    resolved_house_number: str | None = None
    resolved_city_district: str | None = None
    resolved_municipality_name: str | None = None
    resolved_municipality_code: str | None = None
    resolved_region_code: str | None = None
    geocoding_fallback_level: str | None = None
    geocoding_is_fallback: bool | None = None
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
    urban_center_profile: str | None = None
    distance_to_municipality_center_km: float | None = None
    distance_to_historic_center_km: float | None = None
    distance_to_employment_center_km: float | None = None
    distance_to_primary_rail_hub_km: float | None = None
    distance_to_airport_km: float | None = None
    metropolitan_area: str | None = None
    metropolitan_district: str | None = None
    spatial_grid_system: str | None = None
    spatial_grid_source_precision: str | None = None
    spatial_grid_is_approximate: bool | None = None
    spatial_grid_parent_cell_id: str | None = None
    spatial_cell_id: str | None = None
    spatial_grid_fine_cell_id: str | None = None
    distance_to_prague_center_km: float | None = None
    is_district_city: bool | None = None
    is_orp_center: bool | None = None
    city_district_normalized: str | None = None
    municipality_match_status: str = "unmatched"
    municipality_match_method: str | None = None
    municipality_match_input: str | None = None
    municipality_match_candidates: tuple[str, ...] = field(default_factory=tuple)
    nearest_public_transport_m: int | None = None
    nearest_backbone_public_transport_m: int | None = None
    nearest_metro_m: int | None = None
    nearest_tram_m: int | None = None
    nearest_bus_m: int | None = None
    nearest_train_m: int | None = None
    has_backbone_public_transport_within_500m: bool | None = None
    has_backbone_public_transport_within_1000m: bool | None = None
    has_metro_within_1000m: bool | None = None
    has_tram_within_500m: bool | None = None
    has_train_within_1500m: bool | None = None
    nearest_shop_m: int | None = None
    nearest_school_m: int | None = None
    nearest_kindergarten_m: int | None = None
    amenities_within_300m_count: int = 0
    amenities_within_1000m_count: int = 0
    daily_service_amenities_within_500m_count: int = 0
    community_amenities_within_1000m_count: int = 0
    leisure_amenities_within_1000m_count: int = 0
    nearest_nature_m: int | None = None
    has_nature_within_1000m: bool | None = None


@dataclass(frozen=True)
class EnrichedLifecycleFeatures:
    """Listing freshness and lifecycle features derived from normalized dates."""

    listing_age_days: int | None = None
    updated_recency_days: int | None = None
    is_fresh_listing_7d: bool | None = None
    is_recently_updated_3d: bool | None = None


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
    lifecycle_features: EnrichedLifecycleFeatures = field(
        default_factory=EnrichedLifecycleFeatures,
    )
    enrichment_metadata: EnrichmentMetadata | None = None

    def to_serializable_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-serializable representation of the enriched record."""

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
