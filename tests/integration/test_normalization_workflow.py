"""Integration-style coverage for the operator-facing normalization workflow."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from scraperweb.normalization import (
    FilesystemNormalizationWorkflowService,
    FilesystemNormalizedRecordRepository,
    FilesystemRawSnapshotSource,
    NormalizationWorkflowSelection,
)


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
    assert latest_record["normalization_version"] == "normalized-listing-v7"
    assert latest_record["normalization_metadata"]["source_contract_version"] == (
        "raw-listing-record-v1"
    )
    assert latest_record["normalization_metadata"]["source_region"] == "all-czechia"
    assert latest_record["normalized_at_utc"] == latest_record["captured_at_utc"]
    assert latest_record["location"]["street"] == "Cihlářská"
    assert latest_record["location"]["street_source"] == "title_fallback"
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
    assert nearby_places_record["normalization_version"] == "normalized-listing-v7"
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
    assert "Bankomat:" not in nearby_places_record["core_attributes"]["source_specific_attributes"]
    assert "Školka:" not in nearby_places_record["core_attributes"]["source_specific_attributes"]

    accessories_record = json.loads(
        (
            output_dir
            / "all-czechia/3218928460/2026-03-18T08-57-14.026076+00-00.json"
        ).read_text(encoding="utf-8"),
    )
    assert accessories_record["normalized_at_utc"] == accessories_record["captured_at_utc"]
    assert accessories_record["normalization_version"] == "normalized-listing-v7"
    assert accessories_record["location"]["street"] == "Šiklové"
    assert accessories_record["location"]["street_source"] == "title_fallback"
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
    assert "Příslušenství:" not in accessories_record["core_attributes"]["source_specific_attributes"]


def _build_fixture_raw_dataset(target_root: Path, fixture_paths: tuple[str, ...]) -> Path:
    """Copy representative raw fixtures into a temporary workflow input directory."""

    for fixture_path in fixture_paths:
        source_path = Path(fixture_path)
        relative_path = source_path.relative_to("data/raw")
        destination_path = target_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)
    return target_root
