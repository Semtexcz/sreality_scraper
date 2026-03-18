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
    assert latest_record["normalization_version"] == "normalized-listing-v5"
    assert latest_record["normalization_metadata"]["source_contract_version"] == (
        "raw-listing-record-v1"
    )
    assert latest_record["normalization_metadata"]["source_region"] == "all-czechia"
    assert latest_record["normalized_at_utc"] == latest_record["captured_at_utc"]
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


def _build_fixture_raw_dataset(target_root: Path, fixture_paths: tuple[str, ...]) -> Path:
    """Copy representative raw fixtures into a temporary workflow input directory."""

    for fixture_path in fixture_paths:
        source_path = Path(fixture_path)
        relative_path = source_path.relative_to("data/raw")
        destination_path = target_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)
    return target_root
