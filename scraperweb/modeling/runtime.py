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


MODELING_INPUT_VERSION = "modeling-input-v7"
MODEL_VERSION = "listing-baseline-v2"


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
                is_ground_floor=record.property_features.is_ground_floor,
                is_upper_floor=record.property_features.is_upper_floor,
                relative_floor_position=record.property_features.relative_floor_position,
                is_top_floor=record.property_features.is_top_floor,
                is_new_build=record.property_features.is_new_build,
                building_material_bucket=record.property_features.building_material_bucket,
                building_condition_bucket=record.property_features.building_condition_bucket,
                energy_efficiency_bucket=record.property_features.energy_efficiency_bucket,
                has_price_note=record.price_features.has_price_note,
                has_energy_efficiency_rating=(
                    record.property_features.has_energy_efficiency_rating
                ),
                has_city_district=record.property_features.has_city_district,
                is_prague_listing=record.property_features.is_prague_listing,
                municipality_code=record.location_features.municipality_code,
                district_code=record.location_features.district_code,
                region_code=record.location_features.region_code,
                orp_code=record.location_features.orp_code,
                metropolitan_area=record.location_features.metropolitan_area,
                metropolitan_district=record.location_features.metropolitan_district,
                spatial_grid_system=record.location_features.spatial_grid_system,
                spatial_grid_source_precision=(
                    record.location_features.spatial_grid_source_precision
                ),
                spatial_grid_is_approximate=(
                    record.location_features.spatial_grid_is_approximate
                ),
                spatial_grid_parent_cell_id=(
                    record.location_features.spatial_grid_parent_cell_id
                ),
                spatial_cell_id=record.location_features.spatial_cell_id,
                spatial_grid_fine_cell_id=(
                    record.location_features.spatial_grid_fine_cell_id
                ),
                municipality_latitude=record.location_features.municipality_latitude,
                municipality_longitude=record.location_features.municipality_longitude,
                distance_to_okresni_mesto_km=(
                    record.location_features.distance_to_okresni_mesto_km
                ),
                distance_to_orp_center_km=(
                    record.location_features.distance_to_orp_center_km
                ),
                urban_center_profile=record.location_features.urban_center_profile,
                distance_to_municipality_center_km=(
                    record.location_features.distance_to_municipality_center_km
                ),
                distance_to_historic_center_km=(
                    record.location_features.distance_to_historic_center_km
                ),
                distance_to_employment_center_km=(
                    record.location_features.distance_to_employment_center_km
                ),
                distance_to_primary_rail_hub_km=(
                    record.location_features.distance_to_primary_rail_hub_km
                ),
                distance_to_airport_km=record.location_features.distance_to_airport_km,
                distance_to_prague_center_km=(
                    record.location_features.distance_to_prague_center_km
                ),
                is_district_city=record.location_features.is_district_city,
                is_orp_center=record.location_features.is_orp_center,
                nearest_public_transport_m=(
                    record.location_features.nearest_public_transport_m
                ),
                nearest_backbone_public_transport_m=(
                    record.location_features.nearest_backbone_public_transport_m
                ),
                nearest_metro_m=record.location_features.nearest_metro_m,
                nearest_tram_m=record.location_features.nearest_tram_m,
                nearest_bus_m=record.location_features.nearest_bus_m,
                nearest_train_m=record.location_features.nearest_train_m,
                has_backbone_public_transport_within_500m=(
                    record.location_features.has_backbone_public_transport_within_500m
                ),
                has_backbone_public_transport_within_1000m=(
                    record.location_features.has_backbone_public_transport_within_1000m
                ),
                has_metro_within_1000m=(
                    record.location_features.has_metro_within_1000m
                ),
                has_tram_within_500m=record.location_features.has_tram_within_500m,
                has_train_within_1500m=(
                    record.location_features.has_train_within_1500m
                ),
                nearest_shop_m=record.location_features.nearest_shop_m,
                nearest_school_m=record.location_features.nearest_school_m,
                nearest_kindergarten_m=(
                    record.location_features.nearest_kindergarten_m
                ),
                amenities_within_300m_count=(
                    record.location_features.amenities_within_300m_count
                ),
                amenities_within_1000m_count=(
                    record.location_features.amenities_within_1000m_count
                ),
                daily_service_amenities_within_500m_count=(
                    record.location_features.daily_service_amenities_within_500m_count
                ),
                community_amenities_within_1000m_count=(
                    record.location_features.community_amenities_within_1000m_count
                ),
                leisure_amenities_within_1000m_count=(
                    record.location_features.leisure_amenities_within_1000m_count
                ),
                nearest_nature_m=record.location_features.nearest_nature_m,
                has_nature_within_1000m=(
                    record.location_features.has_nature_within_1000m
                ),
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
