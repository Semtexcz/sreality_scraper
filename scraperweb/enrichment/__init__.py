"""Enrichment-stage package boundary.

This package owns the typed enrichment contract and the stage component that
derives explicit features from normalized records only.
"""

from scraperweb.enrichment.models import (
    EnrichedListingRecord,
    EnrichedPriceFeatures,
    EnrichedPropertyFeatures,
    EnrichmentMetadata,
)
from scraperweb.enrichment.runtime import ENRICHMENT_VERSION, NormalizedListingEnricher

__all__ = [
    "ENRICHMENT_VERSION",
    "EnrichedListingRecord",
    "EnrichedPriceFeatures",
    "EnrichedPropertyFeatures",
    "EnrichmentMetadata",
    "NormalizedListingEnricher",
]
