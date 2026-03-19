"""Operator-facing filesystem workflow for persisted normalized-to-enriched runs."""

from __future__ import annotations

from collections.abc import Iterable
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from scraperweb.enrichment.models import (
    EnrichedLifecycleFeatures,
    EnrichedListingRecord,
    EnrichedLocationFeatures,
    EnrichedPriceFeatures,
    EnrichedPropertyFeatures,
    EnrichmentMetadata,
)
from scraperweb.enrichment.runtime import NormalizedListingEnricher
from scraperweb.normalization.models import (
    NormalizedAccessories,
    NormalizedAccessoryAreaFeature,
    NormalizedAreaDetails,
    NormalizedBuilding,
    NormalizedCoreAttributes,
    NormalizedEnergyDetails,
    NormalizedListingLifecycle,
    NormalizedListingRecord,
    NormalizedLocation,
    NormalizedNearbyPlace,
    NormalizedOwnership,
    NormalizedPrice,
    NormalizedSourceIdentifiers,
    NormalizationMetadata,
)
from scraperweb.persistence.repositories import _sanitize_path_component, _timestamp_for_filename


@dataclass(frozen=True)
class EnrichmentWorkflowSelection:
    """Describe one supported enrichment scope selector."""

    region: str | None = None
    listing_id: str | None = None
    scrape_run_id: str | None = None

    def __post_init__(self) -> None:
        """Validate that exactly one enrichment scope is selected."""

        selected_values = (
            self.region is not None,
            self.listing_id is not None,
            self.scrape_run_id is not None,
        )
        if sum(selected_values) != 1:
            raise EnrichmentWorkflowError(
                "Exactly one enrichment selector must be provided: "
                "--region, --listing-id, or --scrape-run-id.",
            )

    def describe(self) -> str:
        """Return a human-readable description of the selected scope."""

        if self.region is not None:
            return f"region={self.region}"
        if self.listing_id is not None:
            return f"listing_id={self.listing_id}"
        return f"scrape_run_id={self.scrape_run_id}"


class EnrichmentWorkflowError(ValueError):
    """Raised when the operator-facing enrichment workflow cannot proceed."""


class FilesystemNormalizedSnapshotSource:
    """Load persisted normalized listing records from the filesystem."""

    def __init__(self, input_dir: Path) -> None:
        """Store the root directory that contains normalized listing snapshots."""

        self._input_dir = input_dir

    def iter_records(
        self,
        selection: EnrichmentWorkflowSelection,
    ) -> list[NormalizedListingRecord]:
        """Return persisted normalized records matching one supported workflow scope."""

        if not self._input_dir.exists():
            raise EnrichmentWorkflowError(
                f"Normalized input directory does not exist: {self._input_dir}",
            )

        if selection.region is not None:
            records = self._load_region_records(selection.region)
        elif selection.listing_id is not None:
            records = self._load_listing_records(selection.listing_id)
        else:
            records = self._load_scrape_run_records(selection.scrape_run_id or "")

        if not records:
            raise EnrichmentWorkflowError(
                "No persisted normalized snapshots matched the selected enrichment scope: "
                f"{selection.describe()}.",
            )
        return records

    def _load_region_records(self, region: str) -> list[NormalizedListingRecord]:
        """Load every normalized snapshot that belongs to one region dataset."""

        region_dir = self._input_dir / region
        if not region_dir.exists():
            raise EnrichmentWorkflowError(
                f"Normalized region directory does not exist: {region_dir}",
            )
        return [
            self._load_record(path)
            for path in self._iter_record_paths(region_dir.rglob("*.json"))
        ]

    def _load_listing_records(self, listing_id: str) -> list[NormalizedListingRecord]:
        """Load every normalized snapshot stored for one listing id."""

        listing_paths = sorted(
            self._input_dir.glob(f"*/{_sanitize_path_component(listing_id)}/*.json"),
        )
        return [self._load_record(path) for path in self._iter_record_paths(listing_paths)]

    def _load_scrape_run_records(self, scrape_run_id: str) -> list[NormalizedListingRecord]:
        """Load normalized snapshots captured during one scrape run id."""

        matching_records: list[NormalizedListingRecord] = []
        for path in self._iter_record_paths(self._input_dir.rglob("*.json")):
            record = self._load_record(path)
            if record.normalization_metadata.source_scrape_run_id == scrape_run_id:
                matching_records.append(record)
        return matching_records

    @staticmethod
    def _iter_record_paths(paths: Iterable[Path]) -> list[Path]:
        """Return sorted normalized-record paths."""

        return sorted(paths)

    @staticmethod
    def _load_record(path: Path) -> NormalizedListingRecord:
        """Deserialize one persisted normalized record snapshot from JSON."""

        serialized_record = json.loads(path.read_text(encoding="utf-8"))
        return _deserialize_normalized_record(serialized_record)


class FilesystemEnrichedRecordRepository:
    """Persist enriched listing records into a stable filesystem layout."""

    def __init__(self, output_dir: Path) -> None:
        """Store the configured enrichment output root and ensure it exists."""

        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def save_record(self, record: EnrichedListingRecord) -> Path:
        """Persist one enriched listing snapshot and return the written path."""

        listing_directory = (
            self._output_dir
            / _sanitize_path_component(
                record.normalized_record.normalization_metadata.source_region,
            )
            / _sanitize_path_component(record.listing_id)
        )
        listing_directory.mkdir(parents=True, exist_ok=True)
        base_name = _timestamp_for_filename(record.captured_at_utc.isoformat())
        output_path = listing_directory / f"{base_name}.json"
        with output_path.open("w", encoding="utf-8") as output_file:
            json.dump(
                record.to_serializable_dict(),
                output_file,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            output_file.write("\n")
        return output_path


class FilesystemEnrichmentWorkflowService:
    """Enrich persisted normalized filesystem snapshots into stable JSON artifacts."""

    def __init__(
        self,
        normalized_snapshot_source: FilesystemNormalizedSnapshotSource,
        enriched_record_repository: FilesystemEnrichedRecordRepository,
        normalized_listing_enricher: NormalizedListingEnricher | None = None,
    ) -> None:
        """Store collaborators used by the filesystem enrichment workflow."""

        self._normalized_snapshot_source = normalized_snapshot_source
        self._enriched_record_repository = enriched_record_repository
        self._normalized_listing_enricher = normalized_listing_enricher or (
            NormalizedListingEnricher()
        )

    def enrich(self, selection: EnrichmentWorkflowSelection) -> int:
        """Enrich every normalized snapshot in the selected workflow scope."""

        enriched_records = 0
        for normalized_record in self._normalized_snapshot_source.iter_records(selection):
            enriched_record = self._normalized_listing_enricher.enrich(normalized_record)
            self._enriched_record_repository.save_record(enriched_record)
            enriched_records += 1
        return enriched_records


def run_filesystem_enrichment_workflow(
    *,
    input_dir: Path,
    output_dir: Path,
    region: str | None = None,
    listing_id: str | None = None,
    scrape_run_id: str | None = None,
) -> int:
    """Run the public filesystem enrichment workflow for one selected scope."""

    selection = EnrichmentWorkflowSelection(
        region=region,
        listing_id=listing_id,
        scrape_run_id=scrape_run_id,
    )
    service = FilesystemEnrichmentWorkflowService(
        normalized_snapshot_source=FilesystemNormalizedSnapshotSource(input_dir=input_dir),
        enriched_record_repository=FilesystemEnrichedRecordRepository(output_dir=output_dir),
    )
    return service.enrich(selection)


def _deserialize_normalized_record(payload: dict[str, object]) -> NormalizedListingRecord:
    """Build a normalized record from one serialized filesystem artifact payload."""

    return NormalizedListingRecord(
        listing_id=str(payload["listing_id"]),
        source_url=str(payload["source_url"]),
        captured_at_utc=datetime.fromisoformat(str(payload["captured_at_utc"])),
        normalized_at_utc=datetime.fromisoformat(str(payload["normalized_at_utc"])),
        normalization_version=str(payload["normalization_version"]),
        core_attributes=_deserialize_core_attributes(_as_dict(payload["core_attributes"])),
        location=_deserialize_location(_as_dict(payload["location"])),
        normalization_metadata=_deserialize_normalization_metadata(
            _as_dict(payload["normalization_metadata"]),
        ),
        area_details=_deserialize_area_details(_as_dict(payload["area_details"])),
        energy_details=_deserialize_energy_details(_as_dict(payload["energy_details"])),
        ownership=_deserialize_ownership(_as_dict(payload["ownership"])),
        listing_lifecycle=_deserialize_listing_lifecycle(
            _as_dict(payload["listing_lifecycle"]),
        ),
        source_identifiers=_deserialize_source_identifiers(
            _as_dict(payload["source_identifiers"]),
        ),
    )


def _deserialize_core_attributes(payload: dict[str, object]) -> NormalizedCoreAttributes:
    """Build normalized core attributes from serialized payload data."""

    return NormalizedCoreAttributes(
        title=_optional_str(payload.get("title")),
        price=_deserialize_price(_as_dict(payload["price"])),
        building=_deserialize_building(_as_dict(payload["building"])),
        accessories=_deserialize_accessories(_as_dict(payload["accessories"])),
        source_specific_attributes=dict(_as_dict(payload["source_specific_attributes"])),
    )


def _deserialize_price(payload: dict[str, object]) -> NormalizedPrice:
    """Build normalized price data from serialized payload data."""

    return NormalizedPrice(
        amount_text=_optional_str(payload.get("amount_text")),
        amount_czk=_optional_int(payload.get("amount_czk")),
        currency_code=_optional_str(payload.get("currency_code")),
        pricing_mode=_optional_str(payload.get("pricing_mode")),
        note=_optional_str(payload.get("note")),
    )


def _deserialize_building(payload: dict[str, object]) -> NormalizedBuilding:
    """Build normalized building data from serialized payload data."""

    return NormalizedBuilding(
        source_text=_optional_str(payload.get("source_text")),
        material=_optional_str(payload.get("material")),
        structural_attributes=_as_str_tuple(payload.get("structural_attributes")),
        physical_condition=_optional_str(payload.get("physical_condition")),
        floor_position=_optional_int(payload.get("floor_position")),
        total_floor_count=_optional_int(payload.get("total_floor_count")),
        underground_floor_count=_optional_int(payload.get("underground_floor_count")),
        unparsed_fragments=_as_str_tuple(payload.get("unparsed_fragments")),
    )


def _deserialize_accessories(payload: dict[str, object]) -> NormalizedAccessories:
    """Build normalized accessories data from serialized payload data."""

    return NormalizedAccessories(
        source_text=_optional_str(payload.get("source_text")),
        has_elevator=_optional_bool(payload.get("has_elevator")),
        is_barrier_free=_optional_bool(payload.get("is_barrier_free")),
        furnishing_state=_optional_str(payload.get("furnishing_state")),
        balcony=_deserialize_accessory_area_feature(_as_dict(payload["balcony"])),
        loggia=_deserialize_accessory_area_feature(_as_dict(payload["loggia"])),
        terrace=_deserialize_accessory_area_feature(_as_dict(payload["terrace"])),
        cellar=_deserialize_accessory_area_feature(_as_dict(payload["cellar"])),
        parking_space_count=_optional_int(payload.get("parking_space_count")),
        unparsed_fragments=_as_str_tuple(payload.get("unparsed_fragments")),
    )


def _deserialize_accessory_area_feature(
    payload: dict[str, object],
) -> NormalizedAccessoryAreaFeature:
    """Build one normalized area-bearing accessory feature from serialized payload data."""

    return NormalizedAccessoryAreaFeature(
        is_present=_optional_bool(payload.get("is_present")),
        area_sqm=_optional_float(payload.get("area_sqm")),
    )


def _deserialize_location(payload: dict[str, object]) -> NormalizedLocation:
    """Build normalized location data from serialized payload data."""

    return NormalizedLocation(
        location_text=_optional_str(payload.get("location_text")),
        location_text_source=_optional_str(payload.get("location_text_source")),
        street=_optional_str(payload.get("street")),
        street_source=_optional_str(payload.get("street_source")),
        city=_optional_str(payload.get("city")),
        city_source=_optional_str(payload.get("city_source")),
        city_district=_optional_str(payload.get("city_district")),
        city_district_source=_optional_str(payload.get("city_district_source")),
        location_descriptor=_optional_str(payload.get("location_descriptor")),
        location_descriptor_source=_optional_str(payload.get("location_descriptor_source")),
        nearby_places=tuple(
            _deserialize_nearby_place(_as_dict(item))
            for item in _as_list(payload.get("nearby_places"))
        ),
    )


def _deserialize_nearby_place(payload: dict[str, object]) -> NormalizedNearbyPlace:
    """Build one normalized nearby-place record from serialized payload data."""

    return NormalizedNearbyPlace(
        category=str(payload["category"]),
        source_key=str(payload["source_key"]),
        source_text=str(payload["source_text"]),
        name=_optional_str(payload.get("name")),
        distance_m=_optional_int(payload.get("distance_m")),
    )


def _deserialize_area_details(payload: dict[str, object]) -> NormalizedAreaDetails:
    """Build normalized area details from serialized payload data."""

    return NormalizedAreaDetails(
        source_text=_optional_str(payload.get("source_text")),
        usable_area_sqm=_optional_float(payload.get("usable_area_sqm")),
        total_area_sqm=_optional_float(payload.get("total_area_sqm")),
        built_up_area_sqm=_optional_float(payload.get("built_up_area_sqm")),
        garden_area_sqm=_optional_float(payload.get("garden_area_sqm")),
        unparsed_fragments=_as_str_tuple(payload.get("unparsed_fragments")),
    )


def _deserialize_energy_details(payload: dict[str, object]) -> NormalizedEnergyDetails:
    """Build normalized energy details from serialized payload data."""

    return NormalizedEnergyDetails(
        source_text=_optional_str(payload.get("source_text")),
        efficiency_class=_optional_str(payload.get("efficiency_class")),
        regulation_reference=_optional_str(payload.get("regulation_reference")),
        consumption_kwh_per_sqm_year=_optional_float(payload.get("consumption_kwh_per_sqm_year")),
        additional_descriptors=_as_str_tuple(payload.get("additional_descriptors")),
        unparsed_fragments=_as_str_tuple(payload.get("unparsed_fragments")),
    )


def _deserialize_ownership(payload: dict[str, object]) -> NormalizedOwnership:
    """Build normalized ownership data from serialized payload data."""

    return NormalizedOwnership(
        ownership_type=_optional_str(payload.get("ownership_type")),
    )


def _deserialize_listing_lifecycle(
    payload: dict[str, object],
) -> NormalizedListingLifecycle:
    """Build normalized listing lifecycle data from serialized payload data."""

    return NormalizedListingLifecycle(
        listed_on=_optional_date(payload.get("listed_on")),
        listed_on_text=_optional_str(payload.get("listed_on_text")),
        updated_on=_optional_date(payload.get("updated_on")),
        updated_on_text=_optional_str(payload.get("updated_on_text")),
    )


def _deserialize_source_identifiers(
    payload: dict[str, object],
) -> NormalizedSourceIdentifiers:
    """Build normalized source identifiers from serialized payload data."""

    return NormalizedSourceIdentifiers(
        source_listing_reference=_optional_str(payload.get("source_listing_reference")),
    )


def _deserialize_normalization_metadata(
    payload: dict[str, object],
) -> NormalizationMetadata:
    """Build normalization traceability metadata from serialized payload data."""

    return NormalizationMetadata(
        source_contract_version=str(payload["source_contract_version"]),
        source_parser_version=str(payload["source_parser_version"]),
        source_region=str(payload["source_region"]),
        source_listing_page_number=int(payload["source_listing_page_number"]),
        source_scrape_run_id=str(payload["source_scrape_run_id"]),
        source_captured_from=str(payload["source_captured_from"]),
        source_http_status=int(payload["source_http_status"]),
    )


def _as_dict(value: object) -> dict[str, object]:
    """Return a typed dictionary view for one nested payload fragment."""

    if not isinstance(value, dict):
        raise TypeError("Expected a dictionary payload fragment.")
    return {str(key): nested_value for key, nested_value in value.items()}


def _as_list(value: object) -> list[object]:
    """Return a typed list view for one nested payload fragment."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("Expected a list payload fragment.")
    return value


def _as_str_tuple(value: object) -> tuple[str, ...]:
    """Return one serialized string collection as an immutable tuple."""

    return tuple(str(item) for item in _as_list(value))


def _optional_str(value: object) -> str | None:
    """Convert one optional serialized string value back into Python data."""

    if value is None:
        return None
    return str(value)


def _optional_int(value: object) -> int | None:
    """Convert one optional serialized integer value back into Python data."""

    if value is None:
        return None
    return int(value)


def _optional_float(value: object) -> float | None:
    """Convert one optional serialized float value back into Python data."""

    if value is None:
        return None
    return float(value)


def _optional_bool(value: object) -> bool | None:
    """Convert one optional serialized boolean value back into Python data."""

    if value is None:
        return None
    if not isinstance(value, bool):
        raise TypeError("Expected a boolean payload fragment.")
    return value


def _optional_date(value: object) -> date | None:
    """Convert one optional serialized ISO date string back into Python data."""

    if value is None:
        return None
    return date.fromisoformat(str(value))
