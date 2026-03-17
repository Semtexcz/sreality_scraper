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
    has_price_note: bool = False


@dataclass(frozen=True)
class EnrichedPropertyFeatures:
    """Derived listing features computed from normalized title and location fields."""

    disposition: str | None = None
    floor_area_sqm: float | None = None
    has_energy_efficiency_rating: bool = False
    has_city_district: bool = False
    is_prague_listing: bool = False


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
    enrichment_metadata: EnrichmentMetadata | None = None
