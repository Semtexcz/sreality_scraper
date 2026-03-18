"""Normalization-stage services for stable listing contracts."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timezone
import re

from scraperweb.normalization.models import (
    NormalizedAreaDetails,
    NormalizationMetadata,
    NormalizedBuilding,
    NormalizedCoreAttributes,
    NormalizedListingRecord,
    NormalizedListingLifecycle,
    NormalizedLocation,
    NormalizedOwnership,
    NormalizedPrice,
    NormalizedSourceIdentifiers,
)
from scraperweb.scraper.models import JsonValue, RawListingRecord


NORMALIZATION_VERSION = "normalized-listing-v2"
RAW_CONTRACT_VERSION = "raw-listing-record-v1"
_AREA_FRAGMENT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"^Užitná plocha (?P<value>\d+(?:[.,]\d+)?) m²$"),
        "usable_area_sqm",
    ),
    (
        re.compile(r"^Celková plocha (?P<value>\d+(?:[.,]\d+)?) m²$"),
        "total_area_sqm",
    ),
    (
        re.compile(r"^Zastavěná plocha (?P<value>\d+(?:[.,]\d+)?) m²$"),
        "built_up_area_sqm",
    ),
    (
        re.compile(r"^Zahrada o ploše (?P<value>\d+(?:[.,]\d+)?) m²$"),
        "garden_area_sqm",
    ),
)


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
        area_text = self._get_text_value(record.source_payload, "Plocha:")
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
            area_details=self._build_area_details(area_text),
            ownership=NormalizedOwnership(
                ownership_type=self._get_text_value(record.source_payload, "Vlastnictví:"),
            ),
            listing_lifecycle=self._build_listing_lifecycle(record.source_payload),
            source_identifiers=NormalizedSourceIdentifiers(
                source_listing_reference=self._get_text_value(
                    record.source_payload,
                    "ID zakázky:",
                ),
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

    @classmethod
    def _build_area_details(cls, area_text: str | None) -> NormalizedAreaDetails:
        """Parse supported area fragments from the raw detail payload text."""

        if area_text is None:
            return NormalizedAreaDetails()

        parsed_values: dict[str, float | None] = {
            "usable_area_sqm": None,
            "total_area_sqm": None,
            "built_up_area_sqm": None,
            "garden_area_sqm": None,
        }
        unparsed_fragments: list[str] = []

        for fragment in cls._split_comma_delimited_value(area_text):
            matched = False
            for pattern, field_name in _AREA_FRAGMENT_PATTERNS:
                match = pattern.fullmatch(fragment)
                if match is None:
                    continue

                parsed_value = cls._parse_decimal_number(match.group("value"))
                if parsed_value is None or parsed_values[field_name] is not None:
                    unparsed_fragments.append(fragment)
                else:
                    parsed_values[field_name] = parsed_value
                matched = True
                break

            if not matched:
                unparsed_fragments.append(fragment)

        return NormalizedAreaDetails(
            source_text=area_text,
            usable_area_sqm=parsed_values["usable_area_sqm"],
            total_area_sqm=parsed_values["total_area_sqm"],
            built_up_area_sqm=parsed_values["built_up_area_sqm"],
            garden_area_sqm=parsed_values["garden_area_sqm"],
            unparsed_fragments=tuple(unparsed_fragments),
        )

    @classmethod
    def _build_listing_lifecycle(
        cls,
        payload: dict[str, JsonValue],
    ) -> NormalizedListingLifecycle:
        """Parse source lifecycle dates while preserving the original raw text."""

        listed_on_text = cls._get_text_value(payload, "Vloženo:")
        updated_on_text = cls._get_text_value(payload, "Upraveno:")
        return NormalizedListingLifecycle(
            listed_on=cls._parse_czech_date(listed_on_text),
            listed_on_text=listed_on_text,
            updated_on=cls._parse_czech_date(updated_on_text),
            updated_on_text=updated_on_text,
        )

    @staticmethod
    def _split_comma_delimited_value(value: str) -> tuple[str, ...]:
        """Return stripped non-empty fragments from a comma-delimited source value."""

        return tuple(fragment.strip() for fragment in value.split(",") if fragment.strip())

    @staticmethod
    def _parse_decimal_number(value: str) -> float | None:
        """Parse one source decimal number with comma or dot decimal separators."""

        normalized_value = value.replace(",", ".").strip()
        try:
            return float(normalized_value)
        except ValueError:
            return None

    @staticmethod
    def _parse_czech_date(value: str | None) -> date | None:
        """Parse one Czech day-month-year date copied from the detail payload."""

        if value is None:
            return None

        match = re.fullmatch(r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})", value.strip())
        if match is None:
            return None

        day, month, year = (int(part) for part in match.groups())
        try:
            return date(year, month, day)
        except ValueError:
            return None

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
            "Plocha:",
            "Vlastnictví:",
            "Vloženo:",
            "Upraveno:",
            "ID zakázky:",
        }
        return {
            key: payload[key]
            for key in sorted(payload)
            if key not in mapped_keys
        }
