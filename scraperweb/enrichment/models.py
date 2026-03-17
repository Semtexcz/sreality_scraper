"""Typed enrichment-stage contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from scraperweb.normalization.models import NormalizedListingRecord


@dataclass(frozen=True)
class EnrichmentMetadata:
    """Traceability metadata for enrichment outputs."""

    stage_version: str
    derivation_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EnrichedListingRecord:
    """Canonical enrichment-stage output contract."""

    listing_id: str
    source_url: str
    captured_at_utc: datetime
    normalized_record: NormalizedListingRecord
    derived_features: dict[str, Any] = field(default_factory=dict)
    enrichment_metadata: EnrichmentMetadata = field(
        default_factory=lambda: EnrichmentMetadata(stage_version="enrichment-v1"),
    )
