"""Normalization-stage package boundary.

This package owns the typed normalization contract and the stage component that
maps raw scraper outputs into a stable internal structure.
"""

from scraperweb.normalization.models import (
    NormalizationMetadata,
    NormalizedBuilding,
    NormalizedCoreAttributes,
    NormalizedListingRecord,
    NormalizedLocation,
    NormalizedPrice,
)
from scraperweb.normalization.runtime import NORMALIZATION_VERSION, RawListingNormalizer

__all__ = [
    "NORMALIZATION_VERSION",
    "NormalizationMetadata",
    "NormalizedBuilding",
    "NormalizedCoreAttributes",
    "NormalizedListingRecord",
    "NormalizedLocation",
    "NormalizedPrice",
    "RawListingNormalizer",
]
