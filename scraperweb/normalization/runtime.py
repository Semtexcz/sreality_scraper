"""Normalization-stage services for stable listing contracts."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timezone
import re

from scraperweb.normalization.models import (
    NormalizedAreaDetails,
    NormalizedEnergyDetails,
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


NORMALIZATION_VERSION = "normalized-listing-v4"
RAW_CONTRACT_VERSION = "raw-listing-record-v1"
TITLE_FALLBACK_SOURCE = "title_fallback"
SOURCE_PAYLOAD_PREFIX = "source_payload:"
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
_TITLE_AREA_SUFFIX_PATTERN = re.compile(
    r"\d+(?:[.,]\d+)?\s*m²(?P<location>[A-ZÁ-Ž].+)$",
)
_TITLE_LOCATION_CANDIDATE_PATTERN = re.compile(
    r"^(?P<city>[A-ZÁ-Ž][A-Za-zÀ-ž0-9./'’-]*(?: [A-ZÁ-Ž0-9][A-Za-zÀ-ž0-9./'’-]*)*)(?: - (?P<district>[A-ZÁ-Ž0-9][A-Za-zÀ-ž0-9./'’-]*(?: [A-ZÁ-Ž0-9][A-Za-zÀ-ž0-9./'’-]*)*))?$",
)
_PRAGUE_NUMBERED_DISTRICT_PATTERN = re.compile(r"^Praha \d+$")
_BUILDING_FLOOR_PATTERN = re.compile(
    r"^(?P<position>\d+)\.\s*podlaží(?:\s+z\s+(?P<total>\d+))?$",
)
_BUILDING_UNDERGROUND_FLOOR_PATTERN = re.compile(
    r"^(?:(?P<count>\d+)\s+)?podzemní podlaží$",
    re.IGNORECASE,
)
_ENERGY_REGULATION_PATTERN = re.compile(r"^č\.\s*\d+/\d{4}\s*Sb\.$")
_ENERGY_CONSUMPTION_PATTERN = re.compile(
    r"^(?P<value>\d+(?:[.,]\d+)?)\s*kWh/m²\s*rok$",
)
_PRICE_AMOUNT_PATTERN = re.compile(r"^(?P<amount>\d[\d\s]*)\s*Kč$")
_PRICE_ON_REQUEST_TEXTS = frozenset(
    {
        "cena na vyžádání",
        "cenanavyžádání",
    },
)
_BUILDING_PHYSICAL_CONDITIONS = frozenset(
    {
        "Po rekonstrukci",
        "Před rekonstrukcí",
        "Projekt",
        "V dobrém stavu",
        "Ve velmi dobrém stavu",
        "Ve výstavbě",
        "Novostavba",
    },
)
_BUILDING_STRUCTURAL_ATTRIBUTES = frozenset(
    {
        "Jednopodlažní",
        "Mezonet",
        "Podkrovní",
    },
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
        price_text = self._get_text_value(record.source_payload, "Celková cena:")
        building_text = self._get_text_value(record.source_payload, "Stavba:")
        area_text = self._get_text_value(record.source_payload, "Plocha:")
        energy_text = self._get_text_value(record.source_payload, "Energetická náročnost:")
        location = self._build_location(title, record.source_payload)

        return NormalizedListingRecord(
            listing_id=record.listing_id,
            source_url=record.source_url,
            captured_at_utc=record.captured_at_utc,
            normalized_at_utc=self._ensure_utc(self._normalized_at_provider(record)),
            normalization_version=NORMALIZATION_VERSION,
            core_attributes=NormalizedCoreAttributes(
                title=title,
                price=self._build_price(price_text, record.source_payload),
                building=self._build_building(building_text),
                source_specific_attributes=self._build_source_specific_attributes(
                    record.source_payload,
                ),
            ),
            location=location,
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
            energy_details=self._build_energy_details(energy_text),
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
    def _build_price(
        cls,
        price_text: str | None,
        payload: dict[str, JsonValue],
    ) -> NormalizedPrice:
        """Split price source text into stable typed Czech listing price fields."""

        amount_czk, currency_code, pricing_mode = cls._parse_price_fields(price_text)
        return NormalizedPrice(
            amount_text=price_text,
            amount_czk=amount_czk,
            currency_code=currency_code,
            pricing_mode=pricing_mode,
            note=cls._get_text_value(payload, "Poznámka k ceně:"),
        )

    @classmethod
    def _build_building(
        cls,
        building_text: str | None,
    ) -> NormalizedBuilding:
        """Split raw building text into stable typed sub-fields."""

        if building_text is None:
            return NormalizedBuilding()

        fragments = cls._split_comma_delimited_value(building_text)
        material = fragments[0] if fragments else None
        structural_attributes: list[str] = []
        physical_condition: str | None = None
        floor_position: int | None = None
        total_floor_count: int | None = None
        underground_floor_count: int | None = None
        unparsed_fragments: list[str] = []

        for fragment in fragments[1:]:
            floor_match = _BUILDING_FLOOR_PATTERN.fullmatch(fragment)
            if floor_match is not None:
                parsed_position = int(floor_match.group("position"))
                parsed_total = floor_match.group("total")
                if floor_position is None:
                    floor_position = parsed_position
                    total_floor_count = (
                        int(parsed_total) if parsed_total is not None else None
                    )
                else:
                    unparsed_fragments.append(fragment)
                continue

            underground_match = _BUILDING_UNDERGROUND_FLOOR_PATTERN.fullmatch(fragment)
            if underground_match is not None:
                parsed_count = underground_match.group("count")
                if underground_floor_count is None:
                    underground_floor_count = (
                        int(parsed_count) if parsed_count is not None else 1
                    )
                else:
                    unparsed_fragments.append(fragment)
                continue

            if fragment in _BUILDING_PHYSICAL_CONDITIONS:
                if physical_condition is None:
                    physical_condition = fragment
                else:
                    unparsed_fragments.append(fragment)
                continue

            if fragment in _BUILDING_STRUCTURAL_ATTRIBUTES:
                structural_attributes.append(fragment)
            else:
                unparsed_fragments.append(fragment)

        return NormalizedBuilding(
            source_text=building_text,
            material=material,
            structural_attributes=tuple(structural_attributes),
            physical_condition=physical_condition,
            floor_position=floor_position,
            total_floor_count=total_floor_count,
            underground_floor_count=underground_floor_count,
            unparsed_fragments=tuple(unparsed_fragments),
        )

    @classmethod
    def _build_energy_details(cls, energy_text: str | None) -> NormalizedEnergyDetails:
        """Parse energy-efficiency source text into stable typed sub-fields."""

        if energy_text is None:
            return NormalizedEnergyDetails()

        fragments = cls._split_comma_delimited_value(energy_text)
        efficiency_class = fragments[0] if fragments else None
        regulation_reference: str | None = None
        consumption_kwh_per_sqm_year: float | None = None
        additional_descriptors: list[str] = []
        unparsed_fragments: list[str] = []

        for fragment in fragments[1:]:
            if _ENERGY_REGULATION_PATTERN.fullmatch(fragment) is not None:
                if regulation_reference is None:
                    regulation_reference = fragment
                else:
                    unparsed_fragments.append(fragment)
                continue

            consumption_match = _ENERGY_CONSUMPTION_PATTERN.fullmatch(fragment)
            if consumption_match is not None:
                parsed_value = cls._parse_decimal_number(
                    consumption_match.group("value"),
                )
                if parsed_value is not None and consumption_kwh_per_sqm_year is None:
                    consumption_kwh_per_sqm_year = parsed_value
                else:
                    unparsed_fragments.append(fragment)
                continue

            additional_descriptors.append(fragment)

        return NormalizedEnergyDetails(
            source_text=energy_text,
            efficiency_class=efficiency_class,
            regulation_reference=regulation_reference,
            consumption_kwh_per_sqm_year=consumption_kwh_per_sqm_year,
            additional_descriptors=tuple(additional_descriptors),
            unparsed_fragments=tuple(unparsed_fragments),
        )

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

    @classmethod
    def _parse_price_fields(
        cls,
        value: str | None,
    ) -> tuple[int | None, str | None, str | None]:
        """Parse one Czech listing price string into stable typed monetary fields."""

        if value is None:
            return None, None, None

        normalized_value = re.sub(r"\s+", " ", value.strip())
        if normalized_value.casefold() in _PRICE_ON_REQUEST_TEXTS:
            return None, None, "on_request"

        match = _PRICE_AMOUNT_PATTERN.fullmatch(normalized_value)
        if match is None:
            return None, None, None

        amount_text = match.group("amount").replace(" ", "")
        if not amount_text.isdigit():
            return None, None, None
        return int(amount_text), "CZK", "fixed_amount"

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

    @classmethod
    def _build_location(
        cls,
        title: str | None,
        payload: dict[str, JsonValue],
    ) -> NormalizedLocation:
        """Build the normalized location contract with explicit source precedence."""

        location_descriptor = cls._get_text_value(payload, "Lokalita:")
        location_text, location_text_source = cls._extract_location_text_from_title(title)
        city, city_district = cls._split_location_text(location_text)

        return NormalizedLocation(
            location_text=location_text,
            location_text_source=location_text_source,
            city=city,
            city_source=location_text_source if city is not None else None,
            city_district=city_district,
            city_district_source=(
                location_text_source if city_district is not None else None
            ),
            location_descriptor=location_descriptor,
            location_descriptor_source=(
                f"{SOURCE_PAYLOAD_PREFIX}Lokalita:"
                if location_descriptor is not None
                else None
            ),
        )

    @classmethod
    def _extract_location_fields(
        title: str | None,
    ) -> tuple[str | None, str | None, str | None]:
        """Extract legacy location fields from title fallback parsing only."""

        location_text, _ = RawListingNormalizer._extract_location_text_from_title(title)
        city, city_district = RawListingNormalizer._split_location_text(location_text)
        return location_text, city, city_district

    @classmethod
    def _extract_location_text_from_title(
        cls,
        title: str | None,
    ) -> tuple[str | None, str | None]:
        """Extract a location fragment from supported title fallback patterns."""

        if title is None:
            return None, None

        if "," in title:
            location_candidate = title.rsplit(",", maxsplit=1)[1].strip() or None
            if cls._is_supported_title_location(location_candidate):
                return location_candidate, TITLE_FALLBACK_SOURCE

        match = _TITLE_AREA_SUFFIX_PATTERN.search(title)
        if match is None:
            return None, None

        location_candidate = match.group("location").strip() or None
        if not cls._is_supported_title_location(location_candidate):
            return None, None

        return location_candidate, TITLE_FALLBACK_SOURCE

    @staticmethod
    def _is_supported_title_location(value: str | None) -> bool:
        """Return whether one title-derived location fragment matches known formats."""

        if value is None:
            return False

        normalized_value = re.sub(r"\s+", " ", value.strip())
        return _TITLE_LOCATION_CANDIDATE_PATTERN.fullmatch(normalized_value) is not None

    @classmethod
    def _split_location_text(
        cls,
        location_text: str | None,
    ) -> tuple[str | None, str | None]:
        """Split a supported location fragment into city and district parts."""

        if location_text is None:
            return None, None

        city, city_district = cls._split_dash_pair(location_text)
        if city is None:
            return None, None
        if _PRAGUE_NUMBERED_DISTRICT_PATTERN.fullmatch(city) is not None:
            return "Praha", city_district
        return city, city_district

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
            "Lokalita:",
        }
        return {
            key: payload[key]
            for key in sorted(payload)
            if key not in mapped_keys
        }
