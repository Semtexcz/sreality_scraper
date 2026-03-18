"""Typed modeling-stage contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from scraperweb.enrichment.models import EnrichedListingRecord


@dataclass(frozen=True)
class ModelingFeatureSet:
    """Explicit model-ready features derived from an enriched listing record."""

    disposition: str | None = None
    floor_area_sqm: float | None = None
    asking_price_czk: int | None = None
    price_per_square_meter_czk: float | None = None
    is_ground_floor: bool | None = None
    is_upper_floor: bool | None = None
    relative_floor_position: str | None = None
    is_top_floor: bool | None = None
    is_new_build: bool | None = None
    building_material_bucket: str | None = None
    building_condition_bucket: str | None = None
    energy_efficiency_bucket: str | None = None
    has_price_note: bool = False
    has_energy_efficiency_rating: bool = False
    has_city_district: bool = False
    is_prague_listing: bool = False
    municipality_code: str | None = None
    district_code: str | None = None
    region_code: str | None = None
    orp_code: str | None = None
    metropolitan_area: str | None = None
    metropolitan_district: str | None = None
    spatial_cell_id: str | None = None
    municipality_latitude: float | None = None
    municipality_longitude: float | None = None
    distance_to_okresni_mesto_km: float | None = None
    distance_to_orp_center_km: float | None = None
    distance_to_prague_center_km: float | None = None
    is_district_city: bool | None = None
    is_orp_center: bool | None = None
    nearest_public_transport_m: int | None = None
    nearest_metro_m: int | None = None
    nearest_tram_m: int | None = None
    nearest_bus_m: int | None = None
    nearest_train_m: int | None = None
    nearest_shop_m: int | None = None
    nearest_school_m: int | None = None
    nearest_kindergarten_m: int | None = None
    amenities_within_300m_count: int = 0
    amenities_within_1000m_count: int = 0


@dataclass(frozen=True)
class ModelingTargetSet:
    """Optional supervised-learning targets exposed at the modeling boundary."""

    asking_price_czk: int | None = None


@dataclass(frozen=True)
class ModelingMetadata:
    """Traceability metadata for deterministic modeling inputs."""

    modeled_at_utc: datetime
    source_enrichment_version: str
    source_normalization_version: str
    dataset_lineage: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelingInputRecord:
    """Canonical modeling-stage output contract."""

    listing_id: str
    source_url: str
    captured_at_utc: datetime
    model_version: str
    modeling_input_version: str
    features: ModelingFeatureSet = field(default_factory=ModelingFeatureSet)
    targets: ModelingTargetSet = field(default_factory=ModelingTargetSet)
    modeling_metadata: ModelingMetadata | None = None
    enriched_record: EnrichedListingRecord | None = None
