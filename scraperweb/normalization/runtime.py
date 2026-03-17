"""Normalization-stage services for stable listing contracts."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from scraperweb.normalization.models import (
    NormalizationMetadata,
    NormalizedBuilding,
    NormalizedCoreAttributes,
    NormalizedListingRecord,
    NormalizedLocation,
    NormalizedPrice,
)
from scraperweb.scraper.models import JsonValue, RawListingRecord


NORMALIZATION_VERSION = "normalized-listing-v1"
RAW_CONTRACT_VERSION = "raw-listing-record-v1"


class RawListingNormalizer:
    """Convert scraper-stage raw records into the stable normalization contract."""

    def __init__(
        self,
        normalized_at_provider: Callable[[RawListingRecord], datetime] | None = None,
    ) -> None:
        """Store the timestamp provider used for normalized record creation.

        The default provider reuses the raw capture timestamp so normalization stays
        idempotent for identical raw snapshots.
        """

        self._normalized_at_provider = normalized_at_provider or self._default_normalized_at

    def normalize(self, record: RawListingRecord) -> NormalizedListingRecord:
        """Return the canonical normalized representation for one raw listing."""

        title = self._get_text_value(record.source_payload, "Název")
        building_text = self._get_text_value(record.source_payload, "Stavba:")
        location_text, city, city_district = self._extract_location_fields(title)

        return NormalizedListingRecord(
            listing_id=record.listing_id,
            source_url=record.source_url,
            captured_at_utc=record.captured_at_utc,
            normalized_at_utc=self._ensure_utc(self._normalized_at_provider(record)),
            normalization_version=NORMALIZATION_VERSION,
            core_attributes=NormalizedCoreAttributes(
                title=title,
                price=NormalizedPrice(
                    amount_text=self._get_text_value(record.source_payload, "Celková cena:"),
                    note=self._get_text_value(record.source_payload, "Poznámka k ceně:"),
                ),
                building=self._build_building(building_text, record.source_payload),
                source_specific_attributes=self._build_source_specific_attributes(
                    record.source_payload,
                ),
            ),
            location=NormalizedLocation(
                location_text=location_text,
                city=city,
                city_district=city_district,
            ),
            normalization_metadata=NormalizationMetadata(
                source_contract_version=RAW_CONTRACT_VERSION,
                source_parser_version=record.source_metadata.parser_version,
                source_region=record.source_metadata.region,
                source_listing_page_number=record.source_metadata.listing_page_number,
                source_scrape_run_id=record.source_metadata.scrape_run_id,
                source_captured_from=record.source_metadata.captured_from,
                source_http_status=record.source_metadata.http_status,
            ),
        )

    @staticmethod
    def _default_normalized_at(record: RawListingRecord) -> datetime:
        """Return the deterministic normalization timestamp for one raw record."""

        return record.captured_at_utc

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        """Normalize provided timestamps to explicit UTC datetimes."""

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _get_text_value(payload: dict[str, JsonValue], key: str) -> str | None:
        """Return a raw payload value only when it is already a string."""

        value = payload.get(key)
        return value if isinstance(value, str) else None

    @classmethod
    def _build_building(
        cls,
        building_text: str | None,
        payload: dict[str, JsonValue],
    ) -> NormalizedBuilding:
        """Split raw building text into stable typed sub-fields."""

        material, condition = cls._split_pair(building_text)
        return NormalizedBuilding(
            material=material,
            condition=condition,
            energy_efficiency_class=cls._get_text_value(payload, "Energetická náročnost:"),
        )

    @staticmethod
    def _split_pair(value: str | None) -> tuple[str | None, str | None]:
        """Split a two-part comma-delimited raw value into stable positions."""

        if value is None:
            return None, None

        parts = [part.strip() for part in value.split(",", maxsplit=1)]
        first = parts[0] or None
        second = parts[1] or None if len(parts) > 1 else None
        return first, second

    @staticmethod
    def _extract_location_fields(
        title: str | None,
    ) -> tuple[str | None, str | None, str | None]:
        """Extract stable location text, city, and district from the raw title."""

        if title is None or "," not in title:
            return None, None, None

        location_text = title.split(",", maxsplit=1)[1].strip() or None
        if location_text is None:
            return None, None, None

        city, city_district = RawListingNormalizer._split_dash_pair(location_text)
        return location_text, city, city_district

    @staticmethod
    def _split_dash_pair(value: str) -> tuple[str | None, str | None]:
        """Split a dash-delimited location string into city and district parts."""

        parts = [part.strip() for part in value.split(" - ", maxsplit=1)]
        city = parts[0] or None
        district = parts[1] or None if len(parts) > 1 else None
        return city, district

    @staticmethod
    def _build_source_specific_attributes(
        payload: dict[str, JsonValue],
    ) -> dict[str, JsonValue]:
        """Preserve unmapped raw fields in sorted order for traceability."""

        mapped_keys = {
            "Název",
            "Celková cena:",
            "Poznámka k ceně:",
            "Stavba:",
            "Energetická náročnost:",
        }
        return {
            key: payload[key]
            for key in sorted(payload)
            if key not in mapped_keys
        }
