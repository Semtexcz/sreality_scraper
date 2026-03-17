"""Modeling-stage package boundary.

The active runtime does not implement modeling yet. This package owns the typed
modeling input contract and must depend only on enrichment-stage contracts.
"""

from scraperweb.modeling.models import ModelingInputRecord, ModelingMetadata

__all__ = [
    "ModelingInputRecord",
    "ModelingMetadata",
]
