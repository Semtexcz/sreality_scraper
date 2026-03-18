"""Enrichment-stage package boundary.

This package owns the typed enrichment contract and the stage component that
derives explicit features from normalized records only.
"""

from scraperweb.enrichment.models import (
    EnrichedListingRecord,
    EnrichedLifecycleFeatures,
    EnrichedLocationFeatures,
    EnrichedPriceFeatures,
    EnrichedPropertyFeatures,
    EnrichmentMetadata,
)
from scraperweb.enrichment.runtime import ENRICHMENT_VERSION, NormalizedListingEnricher
from scraperweb.enrichment.workflow import (
    EnrichmentWorkflowError,
    EnrichmentWorkflowSelection,
    FilesystemEnrichedRecordRepository,
    FilesystemEnrichmentWorkflowService,
    FilesystemNormalizedSnapshotSource,
    run_filesystem_enrichment_workflow,
)

__all__ = [
    "ENRICHMENT_VERSION",
    "EnrichedListingRecord",
    "EnrichedLifecycleFeatures",
    "EnrichedLocationFeatures",
    "EnrichedPriceFeatures",
    "EnrichedPropertyFeatures",
    "EnrichmentMetadata",
    "NormalizedListingEnricher",
    "EnrichmentWorkflowError",
    "EnrichmentWorkflowSelection",
    "FilesystemEnrichedRecordRepository",
    "FilesystemEnrichmentWorkflowService",
    "FilesystemNormalizedSnapshotSource",
    "run_filesystem_enrichment_workflow",
]
