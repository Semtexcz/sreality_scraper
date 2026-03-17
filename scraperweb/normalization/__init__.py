"""Normalization-stage package boundary.

The active runtime does not implement normalization yet. This package owns the
typed normalization contract so follow-up work can depend on a stable boundary
without importing enrichment or modeling modules.
"""

from scraperweb.normalization.models import (
    NormalizationMetadata,
    NormalizedCoreAttributes,
    NormalizedListingRecord,
    NormalizedLocation,
)

__all__ = [
    "NormalizationMetadata",
    "NormalizedCoreAttributes",
    "NormalizedListingRecord",
    "NormalizedLocation",
]
