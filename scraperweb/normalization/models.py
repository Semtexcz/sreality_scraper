"""Typed normalization-stage contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class NormalizedCoreAttributes:
    """Stable structured property attributes derived from raw payloads."""

    values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedLocation:
    """Structured location fields derived from raw source facts only."""

    values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizationMetadata:
    """Traceability metadata for normalization outputs."""

    stage_version: str
    normalized_at_utc: datetime
    source_contract_version: str = "raw-listing-record-v1"


@dataclass(frozen=True)
class NormalizedListingRecord:
    """Canonical normalization-stage output contract."""

    listing_id: str
    source_url: str
    captured_at_utc: datetime
    normalized_at_utc: datetime
    core_attributes: NormalizedCoreAttributes
    location: NormalizedLocation
    normalization_metadata: NormalizationMetadata
