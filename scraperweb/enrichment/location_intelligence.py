"""Reference-backed location intelligence helpers for enrichment."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from scraperweb.normalization.models import NormalizedLocation


_WHITESPACE_PATTERN = re.compile(r"\s+")
_PRAGUE_NUMBERED_PATTERN = re.compile(r"^Praha\s+\d{1,2}$", re.IGNORECASE)


@dataclass(frozen=True)
class MunicipalityReference:
    """One municipality row loaded from the bundled coordinates reference file."""

    municipality_name: str
    municipality_code: str
    district_name: str
    district_code: str
    region_name: str
    region_code: str


@dataclass(frozen=True)
class LocationResolution:
    """Resolved administrative identity and traceability for one location."""

    municipality_name: str | None = None
    municipality_code: str | None = None
    district_name: str | None = None
    district_code: str | None = None
    region_name: str | None = None
    region_code: str | None = None
    orp_name: str | None = None
    orp_code: str | None = None
    is_district_city: bool | None = None
    is_orp_center: bool | None = None
    city_district_normalized: str | None = None
    municipality_match_status: str = "unmatched"
    municipality_match_method: str | None = None
    municipality_match_input: str | None = None
    municipality_match_candidates: tuple[str, ...] = ()


class LocationReferenceIndex:
    """In-memory reference index for conservative municipality matching."""

    def __init__(
        self,
        *,
        municipalities_by_name: dict[str, tuple[MunicipalityReference, ...]],
        district_cities_by_code: dict[str, str],
        orp_codes_by_name: dict[str, str],
    ) -> None:
        """Store indexed reference rows required for location enrichment."""

        self._municipalities_by_name = municipalities_by_name
        self._district_cities_by_code = district_cities_by_code
        self._orp_codes_by_name = orp_codes_by_name

    @classmethod
    def from_data_dir(cls, data_dir: Path) -> "LocationReferenceIndex":
        """Load location reference tables from the repository ``data`` directory."""

        municipality_rows = cls._load_municipality_rows(data_dir / "souradnice.csv")
        district_cities_by_code = cls._load_district_cities(
            data_dir / "OkresniMesta.csv",
        )
        orp_codes_by_name = cls._load_orp_centers(
            data_dir / "ObceSRozsirenouPusobnosti.csv",
        )
        municipalities_by_name: dict[str, list[MunicipalityReference]] = {}
        for row in municipality_rows:
            key = _normalize_key(row.municipality_name)
            municipalities_by_name.setdefault(key, []).append(row)

        return cls(
            municipalities_by_name={
                key: tuple(rows) for key, rows in municipalities_by_name.items()
            },
            district_cities_by_code=district_cities_by_code,
            orp_codes_by_name=orp_codes_by_name,
        )

    def resolve(self, location: NormalizedLocation) -> LocationResolution:
        """Resolve one normalized location against bundled reference datasets."""

        city_district_normalized = _normalize_city_district(location)
        candidate_name, match_input, match_method = self._build_match_input(location)
        if candidate_name is None:
            return LocationResolution(city_district_normalized=city_district_normalized)

        candidates = self._municipalities_by_name.get(_normalize_key(candidate_name), ())
        if not candidates:
            return LocationResolution(
                city_district_normalized=city_district_normalized,
                municipality_match_method=match_method,
                municipality_match_input=match_input,
            )

        if len(candidates) > 1:
            disambiguated = self._disambiguate_by_location_text(
                candidates=candidates,
                location=location,
            )
            if disambiguated is not None:
                return self._build_resolution(
                    row=disambiguated,
                    city_district_normalized=city_district_normalized,
                    municipality_match_method="city_and_location_text_district",
                    municipality_match_input=match_input,
                )
            return LocationResolution(
                city_district_normalized=city_district_normalized,
                municipality_match_status="ambiguous",
                municipality_match_method=match_method,
                municipality_match_input=match_input,
                municipality_match_candidates=tuple(
                    _format_candidate(candidate) for candidate in candidates
                ),
            )

        return self._build_resolution(
            row=candidates[0],
            city_district_normalized=city_district_normalized,
            municipality_match_method=match_method,
            municipality_match_input=match_input,
        )

    @staticmethod
    def _load_municipality_rows(path: Path) -> tuple[MunicipalityReference, ...]:
        """Load municipality rows from the bundled reference CSV file."""

        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return tuple(
                MunicipalityReference(
                    municipality_name=row["Obec"].strip(),
                    municipality_code=row["Kód obce"].strip(),
                    district_name=row["Okres"].strip(),
                    district_code=row["Kód okresu"].strip(),
                    region_name=row["Kraj"].strip(),
                    region_code=row["Kód kraje"].strip(),
                )
                for row in reader
            )

    @staticmethod
    def _load_district_cities(path: Path) -> dict[str, str]:
        """Load district-center municipality names keyed by district code."""

        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return {
                row["chodnota"].strip(): row["text"].strip()
                for row in reader
                if row["chodnota"].strip() and row["text"].strip()
            }

    @staticmethod
    def _load_orp_centers(path: Path) -> dict[str, str]:
        """Load ORP-center codes keyed by municipality name."""

        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return {
                _normalize_key(row["text"]): row["chodnota"].strip()
                for row in reader
                if row["text"].strip() and row["chodnota"].strip()
            }

    @staticmethod
    def _build_match_input(
        location: NormalizedLocation,
    ) -> tuple[str | None, str | None, str | None]:
        """Return the normalized municipality input used for reference matching."""

        city = _clean_text(location.city)
        if city is None:
            return None, None, None
        if _PRAGUE_NUMBERED_PATTERN.fullmatch(city):
            return "Praha", city, "city_prague_numbered"
        return city, city, "city"

    @staticmethod
    def _disambiguate_by_location_text(
        *,
        candidates: tuple[MunicipalityReference, ...],
        location: NormalizedLocation,
    ) -> MunicipalityReference | None:
        """Resolve duplicate municipality names using district text from location."""

        location_text_key = _normalize_key(location.location_text)
        if location_text_key is None:
            return None

        matches = tuple(
            candidate
            for candidate in candidates
            if _normalize_key(candidate.district_name) in location_text_key
        )
        if len(matches) != 1:
            return None
        return matches[0]

    def _build_resolution(
        self,
        *,
        row: MunicipalityReference,
        city_district_normalized: str | None,
        municipality_match_method: str | None,
        municipality_match_input: str | None,
    ) -> LocationResolution:
        """Build the resolved output contract for one matched municipality row."""

        district_city_name = self._district_cities_by_code.get(row.district_code)
        is_district_city = None
        if district_city_name is not None:
            is_district_city = _is_district_city_match(
                municipality_name=row.municipality_name,
                district_city_name=district_city_name,
            )

        orp_code = self._orp_codes_by_name.get(_normalize_key(row.municipality_name))
        is_orp_center = orp_code is not None

        return LocationResolution(
            municipality_name=row.municipality_name,
            municipality_code=row.municipality_code,
            district_name=row.district_name,
            district_code=row.district_code,
            region_name=row.region_name,
            region_code=row.region_code,
            orp_name=row.municipality_name if is_orp_center else None,
            orp_code=orp_code,
            is_district_city=is_district_city,
            is_orp_center=is_orp_center,
            city_district_normalized=city_district_normalized,
            municipality_match_status="matched",
            municipality_match_method=municipality_match_method,
            municipality_match_input=municipality_match_input,
        )


def _normalize_city_district(location: NormalizedLocation) -> str | None:
    """Normalize district text when it can be stabilized from source-backed fields."""

    city = _clean_text(location.city)
    if city is not None and _PRAGUE_NUMBERED_PATTERN.fullmatch(city):
        return city
    return _clean_text(location.city_district)


def _format_candidate(candidate: MunicipalityReference) -> str:
    """Format one ambiguous municipality candidate for traceability output."""

    return (
        f"{candidate.municipality_name} ({candidate.district_name}) "
        f"[{candidate.municipality_code}]"
    )


def _is_district_city_match(*, municipality_name: str, district_city_name: str) -> bool:
    """Return whether a municipality matches one district-center reference name."""

    municipality_key = _normalize_key(municipality_name)
    district_city_key = _normalize_key(district_city_name)
    if municipality_key == district_city_key:
        return True
    if district_city_key is None:
        return False
    if district_city_key.endswith("-město"):
        return municipality_key == district_city_key.removesuffix("-město")
    return False


def _clean_text(value: str | None) -> str | None:
    """Trim one optional text value and collapse internal whitespace."""

    if value is None:
        return None
    cleaned = _WHITESPACE_PATTERN.sub(" ", value.replace("–", "-").strip())
    if not cleaned:
        return None
    return cleaned


def _normalize_key(value: str | None) -> str | None:
    """Normalize text into a case-insensitive lookup key."""

    cleaned = _clean_text(value)
    if cleaned is None:
        return None
    return cleaned.casefold()
