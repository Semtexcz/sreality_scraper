"""Enrichment-stage package boundary.

The active runtime does not implement enrichment yet. This package owns the
typed enrichment contract and must depend only on normalization-stage contracts.
"""

from scraperweb.enrichment.models import EnrichedListingRecord, EnrichmentMetadata

__all__ = [
    "EnrichedListingRecord",
    "EnrichmentMetadata",
]
