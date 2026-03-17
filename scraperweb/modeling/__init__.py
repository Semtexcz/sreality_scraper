"""Modeling-stage package boundary.

This package owns the typed modeling input contract and the stage component that
maps enriched records into model-ready inputs.
"""

from scraperweb.modeling.models import (
    ModelingFeatureSet,
    ModelingInputRecord,
    ModelingMetadata,
    ModelingTargetSet,
)
from scraperweb.modeling.runtime import (
    MODEL_VERSION,
    MODELING_INPUT_VERSION,
    EnrichedListingModelingInputBuilder,
)

__all__ = [
    "MODEL_VERSION",
    "MODELING_INPUT_VERSION",
    "EnrichedListingModelingInputBuilder",
    "ModelingFeatureSet",
    "ModelingInputRecord",
    "ModelingMetadata",
    "ModelingTargetSet",
]
