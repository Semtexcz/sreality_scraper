"""Normalization-stage package boundary.

This package owns the typed normalization contract and the stage component that
maps raw scraper outputs into a stable internal structure.
"""

from scraperweb.normalization.models import (
    NormalizedAreaDetails,
    NormalizedEnergyDetails,
    NormalizationMetadata,
    NormalizedBuilding,
    NormalizedCoreAttributes,
    NormalizedListingRecord,
    NormalizedListingLifecycle,
    NormalizedLocation,
    NormalizedNearbyPlace,
    NormalizedOwnership,
    NormalizedPrice,
    NormalizedSourceIdentifiers,
)
from scraperweb.normalization.runtime import NORMALIZATION_VERSION, RawListingNormalizer
from scraperweb.normalization.workflow import (
    FilesystemNormalizationWorkflowService,
    FilesystemNormalizedRecordRepository,
    FilesystemRawSnapshotSource,
    NormalizationWorkflowError,
    NormalizationWorkflowSelection,
    run_filesystem_normalization_workflow,
)

__all__ = [
    "NORMALIZATION_VERSION",
    "NormalizedAreaDetails",
    "NormalizedEnergyDetails",
    "NormalizationMetadata",
    "NormalizedBuilding",
    "NormalizedCoreAttributes",
    "NormalizedListingRecord",
    "NormalizedListingLifecycle",
    "NormalizedLocation",
    "NormalizedNearbyPlace",
    "NormalizedOwnership",
    "NormalizedPrice",
    "NormalizedSourceIdentifiers",
    "RawListingNormalizer",
    "FilesystemNormalizationWorkflowService",
    "FilesystemNormalizedRecordRepository",
    "FilesystemRawSnapshotSource",
    "NormalizationWorkflowError",
    "NormalizationWorkflowSelection",
    "run_filesystem_normalization_workflow",
]
