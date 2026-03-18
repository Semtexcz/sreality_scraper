"""Normalization-stage package boundary.

This package owns the typed normalization contract and the stage component that
maps raw scraper outputs into a stable internal structure.
"""

from scraperweb.normalization.models import (
    NormalizedAreaDetails,
    NormalizationMetadata,
    NormalizedBuilding,
    NormalizedCoreAttributes,
    NormalizedListingRecord,
    NormalizedListingLifecycle,
    NormalizedLocation,
    NormalizedOwnership,
    NormalizedPrice,
    NormalizedSourceIdentifiers,
)
from scraperweb.normalization.runtime import NORMALIZATION_VERSION, RawListingNormalizer

__all__ = [
    "NORMALIZATION_VERSION",
    "NormalizedAreaDetails",
    "NormalizationMetadata",
    "NormalizedBuilding",
    "NormalizedCoreAttributes",
    "NormalizedListingRecord",
    "NormalizedListingLifecycle",
    "NormalizedLocation",
    "NormalizedOwnership",
    "NormalizedPrice",
    "NormalizedSourceIdentifiers",
    "RawListingNormalizer",
]
