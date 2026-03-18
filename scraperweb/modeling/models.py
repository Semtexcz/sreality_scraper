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
    is_top_floor: bool | None = None
    is_new_build: bool | None = None
    energy_efficiency_bucket: str | None = None
    has_price_note: bool = False
    has_energy_efficiency_rating: bool = False
    has_city_district: bool = False
    is_prague_listing: bool = False


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
