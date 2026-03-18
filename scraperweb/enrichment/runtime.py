"""Enrichment-stage services for deterministic derived listing features."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime, timezone

from scraperweb.enrichment.models import (
    EnrichedListingRecord,
    EnrichedPriceFeatures,
    EnrichedPropertyFeatures,
    EnrichmentMetadata,
)
from scraperweb.normalization.models import NormalizedListingRecord


ENRICHMENT_VERSION = "enriched-listing-v1"
_DERIVATION_NOTES = (
    "asking_price_czk prefers normalized typed price fields and falls back to price text parsing",
    "floor_area_sqm and disposition are parsed from normalized title text",
    "price_per_square_meter_czk is computed only when both price and floor area exist",
)


class NormalizedListingEnricher:
    """Compute explicit derived features from normalized listing records only."""

    def __init__(
        self,
        enriched_at_provider: Callable[[NormalizedListingRecord], datetime] | None = None,
    ) -> None:
        """Store the timestamp provider used for enriched record creation.

        The default provider reuses the normalized timestamp so enrichment stays
        deterministic for identical normalized snapshots.
        """

        self._enriched_at_provider = enriched_at_provider or self._default_enriched_at

    def enrich(self, record: NormalizedListingRecord) -> EnrichedListingRecord:
        """Return the canonical enrichment-stage representation for one listing."""

        if not isinstance(record, NormalizedListingRecord):
            raise TypeError("NormalizedListingEnricher accepts NormalizedListingRecord only.")

        floor_area_sqm = self._parse_floor_area_sqm(record.core_attributes.title)
        asking_price_czk = self._resolve_asking_price_czk(record)
        price_per_square_meter_czk = self._compute_price_per_square_meter(
            asking_price_czk=asking_price_czk,
            floor_area_sqm=floor_area_sqm,
        )

        return EnrichedListingRecord(
            listing_id=record.listing_id,
            source_url=record.source_url,
            captured_at_utc=record.captured_at_utc,
            enrichment_version=ENRICHMENT_VERSION,
            normalized_record=record,
            price_features=EnrichedPriceFeatures(
                asking_price_czk=asking_price_czk,
                price_per_square_meter_czk=price_per_square_meter_czk,
                has_price_note=record.core_attributes.price.note is not None,
            ),
            property_features=EnrichedPropertyFeatures(
                disposition=self._parse_disposition(record.core_attributes.title),
                floor_area_sqm=floor_area_sqm,
                has_energy_efficiency_rating=(
                    record.energy_details.efficiency_class is not None
                ),
                has_city_district=record.location.city_district is not None,
                is_prague_listing=self._is_prague_listing(record),
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
    def _parse_floor_area_sqm(title: str | None) -> float | None:
        """Extract floor area in square meters from normalized title text."""

        if title is None:
            return None

        match = re.search(r"(\d+(?:[.,]\d+)?)\s*m²", title)
        if match is None:
            return None

        return float(match.group(1).replace(",", "."))

    @staticmethod
    def _resolve_asking_price_czk(record: NormalizedListingRecord) -> int | None:
        """Resolve the asking price from normalized typed fields or legacy text."""

        amount_czk = record.core_attributes.price.amount_czk
        if amount_czk is not None:
            return amount_czk
        return NormalizedListingEnricher._parse_asking_price_czk(
            record.core_attributes.price.amount_text,
        )

    @staticmethod
    def _parse_asking_price_czk(amount_text: str | None) -> int | None:
        """Parse the numeric asking price from normalized price text."""

        if amount_text is None:
            return None

        digits = "".join(character for character in amount_text if character.isdigit())
        if not digits:
            return None

        return int(digits)

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
