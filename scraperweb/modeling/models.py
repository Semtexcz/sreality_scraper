"""Typed modeling-stage contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from scraperweb.enrichment.models import EnrichedListingRecord


@dataclass(frozen=True)
class ModelingMetadata:
    """Traceability metadata for modeling inputs."""

    stage_version: str
    dataset_lineage: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelingInputRecord:
    """Canonical modeling-stage output contract."""

    listing_id: str
    captured_at_utc: datetime
    feature_vector: dict[str, Any] = field(default_factory=dict)
    target_values: dict[str, Any] = field(default_factory=dict)
    modeling_metadata: ModelingMetadata = field(
        default_factory=lambda: ModelingMetadata(stage_version="modeling-v1"),
    )
    enriched_record: EnrichedListingRecord | None = None
