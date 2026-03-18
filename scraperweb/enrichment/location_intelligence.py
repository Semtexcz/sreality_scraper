"""Reference-backed location intelligence helpers for enrichment."""

from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path

from scraperweb.normalization.models import NormalizedLocation


_WHITESPACE_PATTERN = re.compile(r"\s+")
_PRAGUE_NUMBERED_PATTERN = re.compile(r"^Praha\s+\d{1,2}$", re.IGNORECASE)
_PRAGUE_CENTER_LATITUDE = 50.087451
_PRAGUE_CENTER_LONGITUDE = 14.420671
_PRAGUE_SPATIAL_CELL_SIZE_DEGREES = 0.01


@dataclass(frozen=True)
class MetropolitanDistrictReference:
    """One supported metropolitan district reference point."""

    metropolitan_area: str
    metropolitan_district: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class MunicipalityReference:
    """One municipality row loaded from the bundled coordinates reference file."""

    municipality_name: str
    municipality_code: str
    district_name: str
    district_code: str
    region_name: str
    region_code: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class OrpCenterReference:
    """One resolved ORP-center point used for macro-distance calculations."""

    orp_name: str
    orp_code: str
    district_code: str
    latitude: float
    longitude: float


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
    municipality_latitude: float | None = None
    municipality_longitude: float | None = None
    distance_to_okresni_mesto_km: float | None = None
    distance_to_orp_center_km: float | None = None
    metropolitan_area: str | None = None
    metropolitan_district: str | None = None
    spatial_cell_id: str | None = None
    distance_to_prague_center_km: float | None = None
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
        orp_centers_by_name: dict[str, OrpCenterReference],
    ) -> None:
        """Store indexed reference rows required for location enrichment."""

        self._municipalities_by_name = municipalities_by_name
        self._district_cities_by_code = district_cities_by_code
        self._orp_centers_by_name = orp_centers_by_name

    @classmethod
    def from_data_dir(cls, data_dir: Path) -> "LocationReferenceIndex":
        """Load location reference tables from the repository ``data`` directory."""

        municipality_rows = cls._load_municipality_rows(data_dir / "souradnice.csv")
        district_cities_by_code = cls._load_district_cities(
            data_dir / "OkresniMesta.csv",
        )
        orp_centers_by_name = cls._load_orp_centers(
            data_dir / "ObceSRozsirenouPusobnosti.csv",
            municipalities_by_name=tuple(municipality_rows),
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
            orp_centers_by_name=orp_centers_by_name,
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
                    latitude=float(row["Latitude"].strip()),
                    longitude=float(row["Longitude"].strip()),
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
    def _load_orp_centers(
        path: Path,
        *,
        municipalities_by_name: tuple[MunicipalityReference, ...],
    ) -> dict[str, OrpCenterReference]:
        """Load ORP-center points by joining ORP names to municipality coordinates."""

        municipality_candidates_by_name: dict[str, list[MunicipalityReference]] = {}
        for municipality in municipalities_by_name:
            key = _normalize_key(municipality.municipality_name)
            if key is None:
                continue
            municipality_candidates_by_name.setdefault(key, []).append(municipality)

        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            orp_centers: dict[str, OrpCenterReference] = {}
            for row in reader:
                orp_name = row["text"].strip()
                orp_code = row["chodnota"].strip()
                if not orp_name or not orp_code:
                    continue
                key = _normalize_key(orp_name)
                if key is None:
                    continue
                municipality_candidates = municipality_candidates_by_name.get(key, [])
                if len(municipality_candidates) != 1:
                    continue
                municipality = municipality_candidates[0]
                orp_centers[key] = OrpCenterReference(
                    orp_name=orp_name,
                    orp_code=orp_code,
                    district_code=municipality.district_code,
                    latitude=municipality.latitude,
                    longitude=municipality.longitude,
                )
            return orp_centers

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

        orp_center = self._orp_centers_by_name.get(_normalize_key(row.municipality_name))
        is_orp_center = orp_center is not None
        district_city_point = self._resolve_district_city_point(row)
        distance_to_okresni_mesto_km = _compute_distance_km(
            source_latitude=row.latitude,
            source_longitude=row.longitude,
            target_latitude=(
                district_city_point.latitude if district_city_point is not None else None
            ),
            target_longitude=(
                district_city_point.longitude if district_city_point is not None else None
            ),
        )
        distance_to_orp_center_km = self._resolve_orp_distance(row)

        return LocationResolution(
            municipality_name=row.municipality_name,
            municipality_code=row.municipality_code,
            district_name=row.district_name,
            district_code=row.district_code,
            region_name=row.region_name,
            region_code=row.region_code,
            orp_name=orp_center.orp_name if is_orp_center else None,
            orp_code=orp_center.orp_code if is_orp_center else None,
            municipality_latitude=row.latitude,
            municipality_longitude=row.longitude,
            distance_to_okresni_mesto_km=distance_to_okresni_mesto_km,
            distance_to_orp_center_km=distance_to_orp_center_km,
            metropolitan_area=_resolve_metropolitan_area_name(
                location_city=row.municipality_name,
                normalized_location_city=municipality_match_input,
            ),
            metropolitan_district=_resolve_metropolitan_district(
                location_city=municipality_match_input,
                city_district_normalized=city_district_normalized,
            ),
            spatial_cell_id=_resolve_spatial_cell_id(
                location_city=municipality_match_input,
                city_district_normalized=city_district_normalized,
            ),
            distance_to_prague_center_km=_resolve_prague_center_distance_km(
                location_city=municipality_match_input,
                city_district_normalized=city_district_normalized,
            ),
            is_district_city=is_district_city,
            is_orp_center=is_orp_center,
            city_district_normalized=city_district_normalized,
            municipality_match_status="matched",
            municipality_match_method=municipality_match_method,
            municipality_match_input=municipality_match_input,
        )

    def _resolve_district_city_point(
        self,
        row: MunicipalityReference,
    ) -> MunicipalityReference | None:
        """Resolve the district-city centroid used for district-distance features."""

        district_city_name = self._district_cities_by_code.get(row.district_code)
        if district_city_name is None:
            return None
        for candidate_name in _build_district_city_candidate_names(district_city_name):
            district_city_key = _normalize_key(candidate_name)
            if district_city_key is None:
                continue
            candidates = self._municipalities_by_name.get(district_city_key, ())
            if not candidates:
                continue
            exact_district_candidates = tuple(
                candidate
                for candidate in candidates
                if candidate.district_code == row.district_code
            )
            if len(exact_district_candidates) == 1:
                return exact_district_candidates[0]
            if len(candidates) == 1:
                return candidates[0]
        return None

    def _resolve_orp_distance(self, row: MunicipalityReference) -> float | None:
        """Resolve the ORP-center distance using district-local centroids when possible."""

        district_orp_centers = tuple(
            center
            for center in self._orp_centers_by_name.values()
            if center.district_code == row.district_code
        )
        if district_orp_centers:
            return round(
                min(
                    _compute_distance_km(
                        source_latitude=row.latitude,
                        source_longitude=row.longitude,
                        target_latitude=center.latitude,
                        target_longitude=center.longitude,
                    )
                    for center in district_orp_centers
                ),
                3,
            )

        if not self._orp_centers_by_name:
            return None

        return round(
            min(
                _compute_distance_km(
                    source_latitude=row.latitude,
                    source_longitude=row.longitude,
                    target_latitude=center.latitude,
                    target_longitude=center.longitude,
                )
                for center in self._orp_centers_by_name.values()
            ),
            3,
        )


def _compute_distance_km(
    *,
    source_latitude: float,
    source_longitude: float,
    target_latitude: float | None,
    target_longitude: float | None,
) -> float | None:
    """Return a rounded great-circle distance in kilometers between two points."""

    if target_latitude is None or target_longitude is None:
        return None
    return round(
        _haversine_distance_km(
            source_latitude=source_latitude,
            source_longitude=source_longitude,
            target_latitude=target_latitude,
            target_longitude=target_longitude,
        ),
        3,
    )


def _haversine_distance_km(
    *,
    source_latitude: float,
    source_longitude: float,
    target_latitude: float,
    target_longitude: float,
) -> float:
    """Compute deterministic great-circle distance in kilometers for two centroids."""

    earth_radius_km = 6_371.0088
    source_latitude_radians = math.radians(source_latitude)
    target_latitude_radians = math.radians(target_latitude)
    latitude_delta = math.radians(target_latitude - source_latitude)
    longitude_delta = math.radians(target_longitude - source_longitude)
    haversine = (
        math.sin(latitude_delta / 2) ** 2
        + math.cos(source_latitude_radians)
        * math.cos(target_latitude_radians)
        * math.sin(longitude_delta / 2) ** 2
    )
    central_angle = 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine))
    return earth_radius_km * central_angle


def _normalize_city_district(location: NormalizedLocation) -> str | None:
    """Normalize district text when it can be stabilized from source-backed fields."""

    city = _clean_text(location.city)
    if city is not None and _PRAGUE_NUMBERED_PATTERN.fullmatch(city):
        return city
    return _clean_text(location.city_district)


def _resolve_metropolitan_area_name(
    *,
    location_city: str | None,
    normalized_location_city: str | None,
) -> str | None:
    """Return the supported metropolitan area label for one resolved location."""

    if _is_prague_city_value(location_city) or _is_prague_city_value(normalized_location_city):
        return "Praha"
    return None


def _resolve_metropolitan_district(
    *,
    location_city: str | None,
    city_district_normalized: str | None,
) -> str | None:
    """Return a supported metropolitan district label when one is unambiguous."""

    district_reference = _resolve_prague_district_reference(
        location_city=location_city,
        city_district_normalized=city_district_normalized,
    )
    if district_reference is None:
        return None
    return district_reference.metropolitan_district


def _resolve_spatial_cell_id(
    *,
    location_city: str | None,
    city_district_normalized: str | None,
) -> str | None:
    """Return a deterministic metropolitan grid cell identifier."""

    district_reference = _resolve_prague_district_reference(
        location_city=location_city,
        city_district_normalized=city_district_normalized,
    )
    if district_reference is None:
        return None

    latitude_index = math.floor(
        district_reference.latitude / _PRAGUE_SPATIAL_CELL_SIZE_DEGREES,
    )
    longitude_index = math.floor(
        district_reference.longitude / _PRAGUE_SPATIAL_CELL_SIZE_DEGREES,
    )
    return f"praha-cell-{latitude_index}-{longitude_index}"


def _resolve_prague_center_distance_km(
    *,
    location_city: str | None,
    city_district_normalized: str | None,
) -> float | None:
    """Return district-reference distance to the documented Prague center point."""

    district_reference = _resolve_prague_district_reference(
        location_city=location_city,
        city_district_normalized=city_district_normalized,
    )
    if district_reference is None:
        return None
    return _compute_distance_km(
        source_latitude=district_reference.latitude,
        source_longitude=district_reference.longitude,
        target_latitude=_PRAGUE_CENTER_LATITUDE,
        target_longitude=_PRAGUE_CENTER_LONGITUDE,
    )


def _resolve_prague_district_reference(
    *,
    location_city: str | None,
    city_district_normalized: str | None,
) -> MetropolitanDistrictReference | None:
    """Resolve the Prague district reference point used for metropolitan features."""

    if not _is_prague_city_value(location_city):
        return None

    district_key = _normalize_key(city_district_normalized)
    if district_key is not None:
        alias_target = _PRAGUE_DISTRICT_ALIASES.get(district_key, district_key)
        district_reference = _PRAGUE_DISTRICT_REFERENCES.get(alias_target)
        if district_reference is not None:
            return district_reference

    city_key = _normalize_key(location_city)
    if city_key is None:
        return None
    return _PRAGUE_DISTRICT_REFERENCES.get(city_key)


def _is_prague_city_value(value: str | None) -> bool:
    """Return whether one city-like value belongs to Prague."""

    cleaned = _clean_text(value)
    if cleaned is None:
        return False
    cleaned_key = cleaned.casefold()
    return cleaned_key == "praha" or _PRAGUE_NUMBERED_PATTERN.fullmatch(cleaned) is not None


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


def _build_district_city_candidate_names(district_city_name: str) -> tuple[str, ...]:
    """Return deterministic municipality-name candidates for one district city."""

    candidates = [district_city_name]
    normalized_name = _normalize_key(district_city_name)
    if normalized_name is not None and normalized_name.endswith("-město"):
        candidates.append(district_city_name.removesuffix("-město"))
    return tuple(candidates)


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


_PRAGUE_DISTRICT_REFERENCES = {
    "praha 1": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 1",
        latitude=50.087451,
        longitude=14.420671,
    ),
    "praha 2": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 2",
        latitude=50.075514,
        longitude=14.4378,
    ),
    "praha 3": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 3",
        latitude=50.08367,
        longitude=14.46598,
    ),
    "praha 4": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 4",
        latitude=50.056051,
        longitude=14.439944,
    ),
    "praha 5": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 5",
        latitude=50.068504,
        longitude=14.404237,
    ),
    "praha 6": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 6",
        latitude=50.100702,
        longitude=14.392124,
    ),
    "praha 7": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 7",
        latitude=50.105981,
        longitude=14.447356,
    ),
    "praha 8": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 8",
        latitude=50.106109,
        longitude=14.474073,
    ),
    "praha 9": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 9",
        latitude=50.111836,
        longitude=14.503557,
    ),
    "praha 10": MetropolitanDistrictReference(
        metropolitan_area="Praha",
        metropolitan_district="Praha 10",
        latitude=50.073978,
        longitude=14.491639,
    ),
}

_PRAGUE_DISTRICT_ALIASES = {
    "stare mesto": "praha 1",
    "staré město": "praha 1",
    "nove mesto": "praha 2",
    "nové město": "praha 2",
    "vinohrady": "praha 2",
    "zizkov": "praha 3",
    "žižkov": "praha 3",
    "nusle": "praha 4",
    "smichov": "praha 5",
    "smíchov": "praha 5",
    "dejvice": "praha 6",
    "holesovice": "praha 7",
    "holešovice": "praha 7",
    "karlin": "praha 8",
    "karlín": "praha 8",
    "vysocany": "praha 9",
    "vysočany": "praha 9",
    "hostivar": "praha 10",
    "hostivař": "praha 10",
}
