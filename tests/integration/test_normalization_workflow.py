"""Integration-style coverage for the operator-facing normalization workflow."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from datetime import timezone
from pathlib import Path

from scraperweb.normalization import (
    FilesystemNormalizationWorkflowService,
    FilesystemNormalizedRecordRepository,
    FilesystemRawSnapshotSource,
    NormalizationWorkflowSelection,
)
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata


def test_normalization_workflow_normalizes_all_snapshots_for_one_listing(
    tmp_path: Path,
) -> None:
    """Normalize every stored snapshot for one listing id into mirrored JSON outputs."""

    input_dir = _build_fixture_raw_dataset(
        tmp_path / "raw",
        (
            "data/raw/all-czechia/2664846156/2026-03-18T08-27-09.155474+00-00.json",
            "data/raw/all-czechia/2664846156/2026-03-18T08-40-57.671555+00-00.json",
            "data/raw/all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
        ),
    )
    output_dir = tmp_path / "normalized"
    service = FilesystemNormalizationWorkflowService(
        raw_snapshot_source=FilesystemRawSnapshotSource(input_dir=input_dir),
        normalized_record_repository=FilesystemNormalizedRecordRepository(output_dir=output_dir),
    )

    normalized_count = service.normalize(
        NormalizationWorkflowSelection(listing_id="2664846156"),
    )

    output_paths = sorted(output_dir.rglob("*.json"))
    assert normalized_count == 3
    assert output_paths == sorted(
        [
            output_dir / "all-czechia/2664846156/2026-03-18T08-27-09.155474+00-00.json",
            output_dir / "all-czechia/2664846156/2026-03-18T08-40-57.671555+00-00.json",
            output_dir / "all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
        ],
    )
    latest_record = json.loads(output_paths[-1].read_text(encoding="utf-8"))
    assert latest_record["listing_id"] == "2664846156"
    assert latest_record["normalization_version"] == "normalized-listing-v9"
    assert latest_record["normalization_metadata"]["source_contract_version"] == (
        "raw-listing-record-v1"
    )
    assert latest_record["normalization_metadata"]["source_region"] == "all-czechia"
    assert latest_record["normalized_at_utc"] == latest_record["captured_at_utc"]
    assert latest_record["location"]["street"] == "Cihlářská"
    assert latest_record["location"]["street_source"] == "title_fallback"
    assert latest_record["location"]["geocoding_query_text"] == "Cihlářská, Blansko"
    assert latest_record["location"]["geocoding_query_text_source"] == "title_fallback"
    assert latest_record["location"]["nearby_places"][0] == {
        "category": "bankomat",
        "source_key": "Bankomat:",
        "source_text": "Bankomat ČSOB(856 m)",
        "name": "Bankomat ČSOB",
        "distance_m": 856,
    }


def test_normalization_workflow_filters_raw_snapshots_by_scrape_run_id(
    tmp_path: Path,
) -> None:
    """Normalize only raw snapshots that belong to the selected scrape run id."""

    input_dir = _build_fixture_raw_dataset(
        tmp_path / "raw",
        (
            "data/raw/all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
            "data/raw/all-czechia/1118982988/2026-03-18T08-56-19.555927+00-00.json",
            "data/raw/all-czechia/10208076/2026-03-18T08-57-03.691606+00-00.json",
        ),
    )
    output_dir = tmp_path / "normalized"
    service = FilesystemNormalizationWorkflowService(
        raw_snapshot_source=FilesystemRawSnapshotSource(input_dir=input_dir),
        normalized_record_repository=FilesystemNormalizedRecordRepository(output_dir=output_dir),
    )

    normalized_count = service.normalize(
        NormalizationWorkflowSelection(
            scrape_run_id="dc733c67-1091-4a08-831f-f8243eb1b8f6",
        ),
    )

    output_paths = sorted(output_dir.rglob("*.json"))
    assert normalized_count == 3
    assert [path.parent.name for path in output_paths] == [
        "10208076",
        "1118982988",
        "2664846156",
    ]


def test_normalization_workflow_supports_region_scoped_dataset_runs(
    tmp_path: Path,
) -> None:
    """Normalize every raw snapshot stored under one region dataset directory."""

    input_dir = _build_fixture_raw_dataset(
        tmp_path / "raw",
        (
            "data/raw/all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
            "data/raw/all-czechia/1118982988/2026-03-18T08-56-19.555927+00-00.json",
        ),
    )
    output_dir = tmp_path / "normalized"
    service = FilesystemNormalizationWorkflowService(
        raw_snapshot_source=FilesystemRawSnapshotSource(input_dir=input_dir),
        normalized_record_repository=FilesystemNormalizedRecordRepository(output_dir=output_dir),
    )

    normalized_count = service.normalize(
        NormalizationWorkflowSelection(region="all-czechia"),
    )

    output_paths = sorted(output_dir.rglob("*.json"))
    assert normalized_count == 2
    assert output_paths == sorted(
        [
            output_dir / "all-czechia/1118982988/2026-03-18T08-56-19.555927+00-00.json",
            output_dir / "all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
        ],
    )


def test_normalization_workflow_replays_nearby_places_and_accessories_into_artifacts(
    tmp_path: Path,
) -> None:
    """Replay representative snapshots and validate typed artifact fields."""

    input_dir = _build_fixture_raw_dataset(
        tmp_path / "raw",
        (
            "data/raw/all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
            "data/raw/all-czechia/3218928460/2026-03-18T08-57-14.026076+00-00.json",
        ),
    )
    output_dir = tmp_path / "normalized"
    service = FilesystemNormalizationWorkflowService(
        raw_snapshot_source=FilesystemRawSnapshotSource(input_dir=input_dir),
        normalized_record_repository=FilesystemNormalizedRecordRepository(output_dir=output_dir),
    )

    normalized_count = service.normalize(
        NormalizationWorkflowSelection(region="all-czechia"),
    )

    assert normalized_count == 2

    nearby_places_record = json.loads(
        (
            output_dir
            / "all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json"
        ).read_text(encoding="utf-8"),
    )
    assert nearby_places_record["normalized_at_utc"] == nearby_places_record["captured_at_utc"]
    assert nearby_places_record["normalization_version"] == "normalized-listing-v9"
    assert nearby_places_record["normalization_metadata"] == {
        "source_captured_from": "detail_page",
        "source_contract_version": "raw-listing-record-v1",
        "source_http_status": 200,
        "source_listing_page_number": 3,
        "source_parser_version": "sreality-detail-v1",
        "source_region": "all-czechia",
        "source_scrape_run_id": "dc733c67-1091-4a08-831f-f8243eb1b8f6",
    }
    assert nearby_places_record["location"]["nearby_places"][0] == {
        "category": "bankomat",
        "source_key": "Bankomat:",
        "source_text": "Bankomat ČSOB(856 m)",
        "name": "Bankomat ČSOB",
        "distance_m": 856,
    }
    assert nearby_places_record["location"]["street"] == "Cihlářská"
    assert nearby_places_record["location"]["street_source"] == "title_fallback"
    assert nearby_places_record["location"]["address_text"] == "Cihlářská, Blansko"
    assert "Bankomat:" not in nearby_places_record["core_attributes"]["source_specific_attributes"]
    assert "Školka:" not in nearby_places_record["core_attributes"]["source_specific_attributes"]

    accessories_record = json.loads(
        (
            output_dir
            / "all-czechia/3218928460/2026-03-18T08-57-14.026076+00-00.json"
        ).read_text(encoding="utf-8"),
    )
    assert accessories_record["normalized_at_utc"] == accessories_record["captured_at_utc"]
    assert accessories_record["normalization_version"] == "normalized-listing-v9"
    assert accessories_record["location"]["street"] == "Šiklové"
    assert accessories_record["location"]["street_source"] == "title_fallback"
    assert accessories_record["location"]["geocoding_query_text"] == (
        "Šiklové, Praha"
    )
    assert accessories_record["core_attributes"]["accessories"] == {
        "source_text": (
            "VýtahBezbariérový přístupNezařízenoTerasa o ploše 204m²"
            "Sklep o ploše 3m²Parkovací stání s 4 místy, Výtah, "
            "Bezbariérový přístup, Nezařízeno, Terasa o ploše 204m², "
            "Sklep o ploše 3m², Parkovací stání s 4 místy"
        ),
        "has_elevator": True,
        "is_barrier_free": True,
        "furnishing_state": "unfurnished",
        "balcony": {
            "is_present": None,
            "area_sqm": None,
        },
        "loggia": {
            "is_present": None,
            "area_sqm": None,
        },
        "terrace": {
            "is_present": True,
            "area_sqm": 204.0,
        },
        "cellar": {
            "is_present": True,
            "area_sqm": 3.0,
        },
        "parking_space_count": 4,
        "unparsed_fragments": [],
    }


def test_normalization_workflow_persists_source_backed_detail_coordinates(
    tmp_path: Path,
) -> None:
    """Persist normalized source-backed coordinates from structured raw payloads."""

    input_dir = tmp_path / "raw"
    raw_record = RawListingRecord(
        listing_id="78467916",
        source_url="https://www.sreality.cz/detail/prodej/byt/2+kk/praha-brevnov/78467916",
        captured_at_utc=datetime(2026, 3, 19, 11, 27, 24, 855716, tzinfo=timezone.utc),
        source_payload={
            "Název": "Prodej bytu 2+kk 58 m², Praha 6 - Břevnov",
            "Celková cena:": "8 490 000 Kč",
            "Lokalita:": "Klidná část obce",
            "source_coordinates": {
                "latitude": 50.0577347,
                "longitude": 14.3723456,
                "source": "detail_locality_payload",
                "precision": "listing",
            },
        },
        source_metadata=RawSourceMetadata(
            region="all-czechia",
            listing_page_number=1,
            scrape_run_id="run-049",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    _write_raw_record_fixture(
        input_dir=input_dir,
        region="all-czechia",
        listing_id=raw_record.listing_id,
        snapshot_name="2026-03-19T11-27-24.855716+00-00.json",
        raw_record=raw_record,
    )
    output_dir = tmp_path / "normalized"
    service = FilesystemNormalizationWorkflowService(
        raw_snapshot_source=FilesystemRawSnapshotSource(input_dir=input_dir),
        normalized_record_repository=FilesystemNormalizedRecordRepository(output_dir=output_dir),
    )

    normalized_count = service.normalize(
        NormalizationWorkflowSelection(listing_id=raw_record.listing_id),
    )

    assert normalized_count == 1
    latest_record = json.loads(
        (
            output_dir
            / "all-czechia/78467916/2026-03-19T11-27-24.855716+00-00.json"
        ).read_text(encoding="utf-8"),
    )
    assert latest_record["normalization_version"] == "normalized-listing-v9"
    assert latest_record["location"]["source_coordinate_latitude"] == 50.0577347
    assert latest_record["location"]["source_coordinate_longitude"] == 14.3723456
    assert latest_record["location"]["source_coordinate_source"] == (
        "detail_locality_payload"
    )
    assert latest_record["location"]["source_coordinate_precision"] == "listing"


def test_normalization_workflow_keeps_legacy_snapshot_coordinate_fallback(
    tmp_path: Path,
) -> None:
    """Normalize older raw artifacts that still rely on persisted detail HTML replay."""

    input_dir = tmp_path / "raw"
    raw_record = RawListingRecord(
        listing_id="legacy-coordinates-1",
        source_url="https://www.sreality.cz/detail/prodej/byt/praha/legacy-coordinates-1",
        captured_at_utc=datetime(2026, 3, 19, 11, 27, 24, 855716, tzinfo=timezone.utc),
        source_payload={
            "Název": "Prodej bytu 2+kk 58 m², Praha 6 - Břevnov",
        },
        source_metadata=RawSourceMetadata(
            region="all-czechia",
            listing_page_number=1,
            scrape_run_id="run-049",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=(
            '<html><script>window.__INITIAL_STATE__={"locality":{"latitude":50.0577347,'
            '"longitude":14.3723456,"city":"Praha","cityPart":"Břevnov",'
            '"inaccuracyType":"gps"}};</script></html>'
        ),
    )
    _write_raw_record_fixture(
        input_dir=input_dir,
        region="all-czechia",
        listing_id=raw_record.listing_id,
        snapshot_name="2026-03-19T11-27-24.855716+00-00.json",
        raw_record=raw_record,
    )
    output_dir = tmp_path / "normalized"
    service = FilesystemNormalizationWorkflowService(
        raw_snapshot_source=FilesystemRawSnapshotSource(input_dir=input_dir),
        normalized_record_repository=FilesystemNormalizedRecordRepository(output_dir=output_dir),
    )

    normalized_count = service.normalize(
        NormalizationWorkflowSelection(listing_id=raw_record.listing_id),
    )

    assert normalized_count == 1
    latest_record = json.loads(
        (
            output_dir
            / "all-czechia/legacy-coordinates-1/2026-03-19T11-27-24.855716+00-00.json"
        ).read_text(encoding="utf-8"),
    )
    assert latest_record["location"]["source_coordinate_latitude"] == 50.0577347
    assert latest_record["location"]["source_coordinate_longitude"] == 14.3723456


def _build_fixture_raw_dataset(target_root: Path, fixture_paths: tuple[str, ...]) -> Path:
    """Copy representative raw fixtures into a temporary workflow input directory."""

    for fixture_path in fixture_paths:
        source_path = Path(fixture_path)
        relative_path = source_path.relative_to("data/raw")
        destination_path = target_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)
    return target_root


def _write_raw_record_fixture(
    *,
    input_dir: Path,
    region: str,
    listing_id: str,
    snapshot_name: str,
    raw_record: RawListingRecord,
) -> None:
    """Write one synthetic raw snapshot fixture into the workflow input directory."""

    destination = input_dir / region / listing_id / snapshot_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(raw_record.to_serializable_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
