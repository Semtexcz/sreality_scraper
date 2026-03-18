"""Enrichment-stage services for deterministic derived listing features."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from scraperweb.config import DATA_DIR
from scraperweb.enrichment.location_intelligence import LocationReferenceIndex
from scraperweb.enrichment.models import (
    EnrichedListingRecord,
    EnrichedLocationFeatures,
    EnrichedPriceFeatures,
    EnrichedPropertyFeatures,
    EnrichmentMetadata,
)
from scraperweb.normalization.models import NormalizedListingRecord


ENRICHMENT_VERSION = "enriched-listing-v6"
_DERIVATION_NOTES = (
    "asking_price_czk is derived from normalized typed price amounts only",
    "disposition is parsed from normalized title text only",
    (
        "canonical_area_sqm prefers normalized usable_area_sqm and falls back to "
        "normalized total_area_sqm when usable_area_sqm is missing"
    ),
    (
        "floor_area_sqm is kept as a compatibility alias of canonical_area_sqm and "
        "never parsed from title text"
    ),
    (
        "price_per_square_meter_czk uses canonical_area_sqm while "
        "price_per_usable_sqm_czk and price_per_total_sqm_czk use their matching "
        "normalized area fields only"
    ),
    (
        "ground-floor, upper-floor, top-floor, and relative floor-position "
        "semantics are derived from normalized building floor fields only"
    ),
    (
        "building material and condition buckets use conservative mappings from "
        "normalized building labels only"
    ),
    "is_new_build is derived from normalized building fields only",
    "energy_efficiency_bucket is derived from normalized energy efficiency classes only",
    "location_features use conservative reference joins against bundled municipality datasets",
    "municipality coordinates use souradnice.csv centroids rather than parcel-level geometry",
    (
        "macro distances use deterministic haversine calculations between municipality "
        "centroids and district-city or district-local ORP-center centroids"
    ),
)
_ENERGY_EFFICIENCY_BUCKETS = {
    "A": "efficient",
    "B": "efficient",
    "C": "efficient",
    "D": "average",
    "E": "inefficient",
    "F": "inefficient",
    "G": "inefficient",
    "Mimořádně úsporná": "efficient",
    "Velmi úsporná": "efficient",
    "Úsporná": "efficient",
    "Méně úsporná": "average",
    "Nehospodárná": "inefficient",
    "Velmi nehospodárná": "inefficient",
    "Mimořádně nehospodárná": "inefficient",
}
_BUILDING_MATERIAL_BUCKETS = {
    "Cihla": "masonry",
    "Cihlová": "masonry",
    "Panelová": "panel",
    "Skeletová": "skeleton",
}
_BUILDING_CONDITION_BUCKETS = {
    "Novostavba": "new_build",
    "Ve výstavbě": "new_build",
    "Projekt": "new_build",
    "Po rekonstrukci": "good",
    "V dobrém stavu": "good",
    "Ve velmi dobrém stavu": "good",
    "Před rekonstrukcí": "needs_work",
}


class NormalizedListingEnricher:
    """Compute explicit derived features from normalized listing records only."""

    def __init__(
        self,
        enriched_at_provider: Callable[[NormalizedListingRecord], datetime] | None = None,
        reference_data_dir: Path = DATA_DIR,
    ) -> None:
        """Store the timestamp provider used for enriched record creation.

        The default provider reuses the normalized timestamp so enrichment stays
        deterministic for identical normalized snapshots.
        """

        self._enriched_at_provider = enriched_at_provider or self._default_enriched_at
        self._location_reference_index = LocationReferenceIndex.from_data_dir(
            reference_data_dir,
        )

    def enrich(self, record: NormalizedListingRecord) -> EnrichedListingRecord:
        """Return the canonical enrichment-stage representation for one listing."""

        if not isinstance(record, NormalizedListingRecord):
            raise TypeError("NormalizedListingEnricher accepts NormalizedListingRecord only.")

        asking_price_czk = self._resolve_asking_price_czk(record)
        usable_area_sqm = self._normalize_area_value(record.area_details.usable_area_sqm)
        total_area_sqm = self._normalize_area_value(record.area_details.total_area_sqm)
        canonical_area_sqm = self._resolve_canonical_area_sqm(record)
        price_per_square_meter_czk = self._compute_price_per_square_meter(
            asking_price_czk=asking_price_czk,
            floor_area_sqm=canonical_area_sqm,
        )
        price_per_usable_sqm_czk = self._compute_price_per_square_meter(
            asking_price_czk=asking_price_czk,
            floor_area_sqm=usable_area_sqm,
        )
        price_per_total_sqm_czk = self._compute_price_per_square_meter(
            asking_price_czk=asking_price_czk,
            floor_area_sqm=total_area_sqm,
        )
        resolved_location = self._location_reference_index.resolve(record.location)

        return EnrichedListingRecord(
            listing_id=record.listing_id,
            source_url=record.source_url,
            captured_at_utc=record.captured_at_utc,
            enrichment_version=ENRICHMENT_VERSION,
            normalized_record=record,
            price_features=EnrichedPriceFeatures(
                asking_price_czk=asking_price_czk,
                price_per_square_meter_czk=price_per_square_meter_czk,
                price_per_usable_sqm_czk=price_per_usable_sqm_czk,
                price_per_total_sqm_czk=price_per_total_sqm_czk,
                has_price_note=record.core_attributes.price.note is not None,
            ),
            property_features=EnrichedPropertyFeatures(
                disposition=self._parse_disposition(record.core_attributes.title),
                canonical_area_sqm=canonical_area_sqm,
                usable_area_sqm=usable_area_sqm,
                total_area_sqm=total_area_sqm,
                floor_area_sqm=canonical_area_sqm,
                is_ground_floor=self._derive_is_ground_floor(record),
                is_upper_floor=self._derive_is_upper_floor(record),
                relative_floor_position=self._derive_relative_floor_position(record),
                is_top_floor=self._derive_is_top_floor(record),
                is_new_build=self._derive_is_new_build(record),
                building_material_bucket=self._derive_building_material_bucket(record),
                building_condition_bucket=self._derive_building_condition_bucket(record),
                energy_efficiency_bucket=self._derive_energy_efficiency_bucket(record),
                has_energy_efficiency_rating=(
                    record.energy_details.efficiency_class is not None
                ),
                has_city_district=record.location.city_district is not None,
                is_prague_listing=self._is_prague_listing(record),
            ),
            location_features=EnrichedLocationFeatures(
                municipality_name=resolved_location.municipality_name,
                municipality_code=resolved_location.municipality_code,
                district_name=resolved_location.district_name,
                district_code=resolved_location.district_code,
                region_name=resolved_location.region_name,
                region_code=resolved_location.region_code,
                orp_name=resolved_location.orp_name,
                orp_code=resolved_location.orp_code,
                municipality_latitude=resolved_location.municipality_latitude,
                municipality_longitude=resolved_location.municipality_longitude,
                distance_to_okresni_mesto_km=(
                    resolved_location.distance_to_okresni_mesto_km
                ),
                distance_to_orp_center_km=resolved_location.distance_to_orp_center_km,
                is_district_city=resolved_location.is_district_city,
                is_orp_center=resolved_location.is_orp_center,
                city_district_normalized=resolved_location.city_district_normalized,
                municipality_match_status=resolved_location.municipality_match_status,
                municipality_match_method=resolved_location.municipality_match_method,
                municipality_match_input=resolved_location.municipality_match_input,
                municipality_match_candidates=(
                    resolved_location.municipality_match_candidates
                ),
            ),
            enrichment_metadata=EnrichmentMetadata(
                enriched_at_utc=self._ensure_utc(self._enriched_at_provider(record)),
                source_normalization_version=record.normalization_version,
                derivation_notes=_DERIVATION_NOTES,
            ),
        )

    @staticmethod
    def _default_enriched_at(record: NormalizedListingRecord) -> datetime:
        """Return the deterministic enrichment timestamp for one normalized record."""

        return record.normalized_at_utc

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        """Normalize provided timestamps to explicit UTC datetimes."""

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _parse_disposition(title: str | None) -> str | None:
        """Extract the apartment disposition token from normalized title text."""

        if title is None:
            return None

        match = re.search(r"\b(\d+\+[A-Za-z0-9]+)\b", title)
        if match is None:
            return None
        return match.group(1)

    @staticmethod
    def _resolve_canonical_area_sqm(record: NormalizedListingRecord) -> float | None:
        """Return the preferred canonical area for downstream price-density features."""

        usable_area_sqm = NormalizedListingEnricher._normalize_area_value(
            record.area_details.usable_area_sqm,
        )
        if usable_area_sqm is not None:
            return usable_area_sqm

        return NormalizedListingEnricher._normalize_area_value(
            record.area_details.total_area_sqm,
        )

    @staticmethod
    def _normalize_area_value(value: float | None) -> float | None:
        """Keep only positive area values so zero-like inputs remain optional."""

        if value in (None, 0):
            return None
        if value < 0:
            return None
        return value

    @staticmethod
    def _resolve_asking_price_czk(record: NormalizedListingRecord) -> int | None:
        """Resolve the asking price from normalized typed fields only."""

        return record.core_attributes.price.amount_czk

    @staticmethod
    def _compute_price_per_square_meter(
        asking_price_czk: int | None,
        floor_area_sqm: float | None,
    ) -> float | None:
        """Compute price per square meter when both input values are available."""

        if asking_price_czk is None or floor_area_sqm in (None, 0):
            return None

        return round(asking_price_czk / floor_area_sqm, 2)

    @staticmethod
    def _is_prague_listing(record: NormalizedListingRecord) -> bool:
        """Return whether the normalized listing belongs to Prague."""

        city = record.location.city
        return city is not None and city.startswith("Praha")

    @staticmethod
    def _derive_is_ground_floor(record: NormalizedListingRecord) -> bool | None:
        """Return whether the normalized building position denotes ground floor."""

        floor_position = record.core_attributes.building.floor_position
        if floor_position is None or floor_position < 0:
            return None
        return floor_position == 0

    @staticmethod
    def _derive_is_upper_floor(record: NormalizedListingRecord) -> bool | None:
        """Return whether the normalized building position is above ground floor."""

        floor_position = record.core_attributes.building.floor_position
        if floor_position is None or floor_position < 0:
            return None
        return floor_position >= 1

    @staticmethod
    def _derive_relative_floor_position(
        record: NormalizedListingRecord,
    ) -> str | None:
        """Map floor position into a coarse relative bucket when both counts exist."""

        building = record.core_attributes.building
        if building.floor_position is None or building.total_floor_count is None:
            return None
        if building.floor_position < 0 or building.total_floor_count <= 0:
            return None
        if building.floor_position > building.total_floor_count:
            return None
        if building.floor_position == 0:
            return "ground"
        if building.floor_position == building.total_floor_count:
            return "top"
        if building.floor_position == 1:
            return "lower"
        if building.floor_position >= building.total_floor_count - 1:
            return "upper"
        return "middle"

    @staticmethod
    def _derive_is_top_floor(record: NormalizedListingRecord) -> bool | None:
        """Return whether the normalized building position is on the top floor."""

        building = record.core_attributes.building
        if building.floor_position is None or building.total_floor_count is None:
            return None
        if building.total_floor_count <= 0:
            return None
        return building.floor_position == building.total_floor_count

    @staticmethod
    def _derive_is_new_build(record: NormalizedListingRecord) -> bool | None:
        """Return whether the normalized building condition denotes a new build."""

        physical_condition = record.core_attributes.building.physical_condition
        if physical_condition is None:
            return None
        return physical_condition == "Novostavba"

    @staticmethod
    def _derive_building_material_bucket(
        record: NormalizedListingRecord,
    ) -> str | None:
        """Map the normalized building material into a coarse stable bucket."""

        material = record.core_attributes.building.material
        if material is None:
            return None
        return _BUILDING_MATERIAL_BUCKETS.get(material)

    @staticmethod
    def _derive_building_condition_bucket(
        record: NormalizedListingRecord,
    ) -> str | None:
        """Map the normalized building condition into a coarse stable bucket."""

        physical_condition = record.core_attributes.building.physical_condition
        if physical_condition is None:
            return None
        return _BUILDING_CONDITION_BUCKETS.get(physical_condition)

    @staticmethod
    def _derive_energy_efficiency_bucket(
        record: NormalizedListingRecord,
    ) -> str | None:
        """Map the normalized energy efficiency class into a coarse bucket."""

        efficiency_class = record.energy_details.efficiency_class
        if efficiency_class is None:
            return None
        return _ENERGY_EFFICIENCY_BUCKETS.get(efficiency_class)
