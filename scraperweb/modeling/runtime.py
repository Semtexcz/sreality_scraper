"""Modeling-stage services for deterministic model-ready inputs."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from scraperweb.enrichment.models import EnrichedListingRecord
from scraperweb.modeling.models import (
    ModelingFeatureSet,
    ModelingInputRecord,
    ModelingMetadata,
    ModelingTargetSet,
)


MODELING_INPUT_VERSION = "modeling-input-v2"
MODEL_VERSION = "listing-baseline-v1"


class EnrichedListingModelingInputBuilder:
    """Build model-ready inputs from enriched listing records only."""

    def __init__(
        self,
        modeled_at_provider: Callable[[EnrichedListingRecord], datetime] | None = None,
        model_version: str = MODEL_VERSION,
    ) -> None:
        """Store deterministic collaborators used during modeling input creation."""

        self._modeled_at_provider = modeled_at_provider or self._default_modeled_at
        self._model_version = model_version

    def build(self, record: EnrichedListingRecord) -> ModelingInputRecord:
        """Return the canonical model-ready representation for one listing."""

        if not isinstance(record, EnrichedListingRecord):
            raise TypeError(
                "EnrichedListingModelingInputBuilder accepts EnrichedListingRecord only.",
            )

        return ModelingInputRecord(
            listing_id=record.listing_id,
            source_url=record.source_url,
            captured_at_utc=record.captured_at_utc,
            model_version=self._model_version,
            modeling_input_version=MODELING_INPUT_VERSION,
            features=ModelingFeatureSet(
                disposition=record.property_features.disposition,
                floor_area_sqm=record.property_features.floor_area_sqm,
                asking_price_czk=record.price_features.asking_price_czk,
                price_per_square_meter_czk=record.price_features.price_per_square_meter_czk,
                is_top_floor=record.property_features.is_top_floor,
                is_new_build=record.property_features.is_new_build,
                energy_efficiency_bucket=record.property_features.energy_efficiency_bucket,
                has_price_note=record.price_features.has_price_note,
                has_energy_efficiency_rating=(
                    record.property_features.has_energy_efficiency_rating
                ),
                has_city_district=record.property_features.has_city_district,
                is_prague_listing=record.property_features.is_prague_listing,
            ),
            targets=ModelingTargetSet(
                asking_price_czk=record.price_features.asking_price_czk,
            ),
            modeling_metadata=ModelingMetadata(
                modeled_at_utc=self._ensure_utc(self._modeled_at_provider(record)),
                source_enrichment_version=record.enrichment_version,
                source_normalization_version=record.normalized_record.normalization_version,
                dataset_lineage=(
                    record.normalized_record.normalization_metadata.source_contract_version,
                    record.normalized_record.normalization_version,
                    record.enrichment_version,
                    MODELING_INPUT_VERSION,
                ),
            ),
            enriched_record=record,
        )

    @staticmethod
    def _default_modeled_at(record: EnrichedListingRecord) -> datetime:
        """Return the deterministic modeling timestamp for one enriched record."""

        metadata = record.enrichment_metadata
        if metadata is not None:
            return metadata.enriched_at_utc
        return record.captured_at_utc

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        """Normalize provided timestamps to explicit UTC datetimes."""

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
