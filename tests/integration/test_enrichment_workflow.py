"""Integration-style coverage for the operator-facing enrichment workflow."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from datetime import timezone
from pathlib import Path

from scraperweb.enrichment import (
    FilesystemEnrichedRecordRepository,
    FilesystemEnrichmentWorkflowService,
    FilesystemNormalizedSnapshotSource,
    EnrichmentWorkflowSelection,
)
from scraperweb.normalization import RawListingNormalizer
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata


def test_enrichment_workflow_enriches_all_snapshots_for_one_listing(
    tmp_path: Path,
) -> None:
    """Enrich every stored normalized snapshot for one listing id into mirrored outputs."""

    input_dir = _build_fixture_normalized_dataset(
        tmp_path / "normalized",
        (
            "data/normalized/all-czechia/2664846156/2026-03-18T08-27-09.155474+00-00.json",
            "data/normalized/all-czechia/2664846156/2026-03-18T08-40-57.671555+00-00.json",
            "data/normalized/all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
        ),
    )
    output_dir = tmp_path / "enriched"
    service = FilesystemEnrichmentWorkflowService(
        normalized_snapshot_source=FilesystemNormalizedSnapshotSource(input_dir=input_dir),
        enriched_record_repository=FilesystemEnrichedRecordRepository(output_dir=output_dir),
    )

    enriched_count = service.enrich(
        EnrichmentWorkflowSelection(listing_id="2664846156"),
    )

    output_paths = sorted(output_dir.rglob("*.json"))
    assert enriched_count == 3
    assert output_paths == sorted(
        [
            output_dir / "all-czechia/2664846156/2026-03-18T08-27-09.155474+00-00.json",
            output_dir / "all-czechia/2664846156/2026-03-18T08-40-57.671555+00-00.json",
            output_dir / "all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
        ],
    )
    latest_record = json.loads(output_paths[-1].read_text(encoding="utf-8"))
    assert latest_record["listing_id"] == "2664846156"
    assert latest_record["enrichment_version"] == "enriched-listing-v16"
    assert latest_record["enrichment_metadata"]["source_normalization_version"] == (
        "normalized-listing-v8"
    )
    assert latest_record["enrichment_metadata"]["enriched_at_utc"] == (
        latest_record["normalized_record"]["normalized_at_utc"]
    )
    assert latest_record["location_features"]["municipality_name"] == "Blansko"
    assert latest_record["location_features"]["street"] == "Cihlářská"
    assert latest_record["location_features"]["street_source"] == "title_fallback"
    assert latest_record["location_features"]["location_precision"] == "street"
    assert latest_record["location_features"]["geocoding_source"] == (
        "deterministic_query_projection"
    )
    assert latest_record["location_features"]["geocoding_query_text"] == (
        "Cihlářská, Blansko"
    )
    assert latest_record["location_features"]["spatial_grid_system"] == (
        "deterministic_square_grid_v1"
    )
    assert latest_record["location_features"]["spatial_grid_source_precision"] == "street"
    assert latest_record["location_features"]["spatial_grid_parent_cell_id"] is not None
    assert latest_record["location_features"]["spatial_cell_id"] is not None
    assert latest_record["location_features"]["spatial_grid_fine_cell_id"] is not None
    assert latest_record["location_features"]["district_name"] == "Blansko"
    assert latest_record["location_features"]["distance_to_orp_center_km"] == 0.0
    assert latest_record["location_features"]["urban_center_profile"] == (
        "municipality_centroid_only"
    )
    assert latest_record["location_features"]["distance_to_municipality_center_km"] > 0
    assert latest_record["location_features"]["nearest_public_transport_m"] == 43
    assert latest_record["location_features"]["nearest_backbone_public_transport_m"] == 1786
    assert latest_record["location_features"]["has_backbone_public_transport_within_500m"] is False
    assert latest_record["location_features"]["nearest_shop_m"] == 231
    assert latest_record["location_features"]["daily_service_amenities_within_500m_count"] == 1
    assert latest_record["location_features"]["community_amenities_within_1000m_count"] == 5
    assert latest_record["location_features"]["leisure_amenities_within_1000m_count"] == 2
    assert latest_record["location_features"]["nearest_nature_m"] is None
    assert latest_record["location_features"]["has_nature_within_1000m"] is None
    assert latest_record["lifecycle_features"] == {
        "is_fresh_listing_7d": True,
        "is_recently_updated_3d": True,
        "listing_age_days": 2,
        "updated_recency_days": 0,
    }


def test_enrichment_workflow_filters_normalized_snapshots_by_scrape_run_id(
    tmp_path: Path,
) -> None:
    """Enrich only normalized snapshots that belong to the selected scrape run id."""

    input_dir = _build_fixture_normalized_dataset(
        tmp_path / "normalized",
        (
            "data/normalized/all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
            "data/normalized/all-czechia/3218928460/2026-03-18T08-57-14.026076+00-00.json",
        ),
    )
    output_dir = tmp_path / "enriched"
    service = FilesystemEnrichmentWorkflowService(
        normalized_snapshot_source=FilesystemNormalizedSnapshotSource(input_dir=input_dir),
        enriched_record_repository=FilesystemEnrichedRecordRepository(output_dir=output_dir),
    )

    enriched_count = service.enrich(
        EnrichmentWorkflowSelection(
            scrape_run_id="dc733c67-1091-4a08-831f-f8243eb1b8f6",
        ),
    )

    assert enriched_count == 2

    prague_record = json.loads(
        (
            output_dir
            / "all-czechia/3218928460/2026-03-18T08-57-14.026076+00-00.json"
        ).read_text(encoding="utf-8"),
    )
    assert prague_record["enrichment_version"] == "enriched-listing-v16"
    assert prague_record["price_features"]["price_per_square_meter_czk"] == 286588.63
    assert prague_record["property_features"]["is_top_floor"] is True
    assert prague_record["property_features"]["outdoor_accessory_area_sqm"] == 204.0
    assert prague_record["location_features"]["municipality_name"] == "Praha"
    assert prague_record["location_features"]["street"] == "Šiklové"
    assert prague_record["location_features"]["street_source"] == "title_fallback"
    assert prague_record["location_features"]["location_precision"] == "street"
    assert prague_record["location_features"]["geocoding_source"] == (
        "deterministic_query_projection"
    )
    assert prague_record["location_features"]["metropolitan_area"] == "Praha"
    assert prague_record["location_features"]["urban_center_profile"] == (
        "prague_polycentric_v1"
    )
    assert prague_record["location_features"]["spatial_grid_system"] == (
        "deterministic_square_grid_v1"
    )
    assert prague_record["location_features"]["municipality_match_status"] == "matched"
    assert prague_record["location_features"]["nearest_metro_m"] == 160
    assert prague_record["location_features"]["nearest_backbone_public_transport_m"] == 105
    assert prague_record["location_features"]["has_metro_within_1000m"] is True
    assert prague_record["location_features"]["amenities_within_300m_count"] == 7
    assert prague_record["location_features"]["daily_service_amenities_within_500m_count"] == 2
    assert prague_record["location_features"]["community_amenities_within_1000m_count"] == 5
    assert prague_record["location_features"]["leisure_amenities_within_1000m_count"] == 5
    assert prague_record["location_features"]["nearest_nature_m"] == 4095
    assert prague_record["location_features"]["has_nature_within_1000m"] is False
    assert prague_record["normalized_record"]["normalization_metadata"] == {
        "source_captured_from": "detail_page",
        "source_contract_version": "raw-listing-record-v1",
        "source_http_status": 200,
        "source_listing_page_number": 5,
        "source_parser_version": "sreality-detail-v1",
        "source_region": "all-czechia",
        "source_scrape_run_id": "dc733c67-1091-4a08-831f-f8243eb1b8f6",
    }


def test_enrichment_workflow_prefers_source_backed_detail_coordinates(
    tmp_path: Path,
) -> None:
    """Enrich normalized snapshots with source-backed listing coordinates ahead of fallback geocoding."""

    normalized_record = RawListingNormalizer().normalize(
        RawListingRecord(
            listing_id="78467916",
            source_url="https://www.sreality.cz/detail/prodej/byt/2+kk/praha-brevnov/78467916",
            captured_at_utc=datetime(2026, 3, 19, 11, 27, 24, tzinfo=timezone.utc),
            source_payload={
                "Název": "Prodej bytu 2+kk 58 m², Bělohorská 123, Praha 6 - Břevnov",
                "Celková cena:": "8 490 000 Kč",
                "Lokalita:": "Klidná část obce",
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
        ),
    )
    input_dir = _write_normalized_fixture(
        target_root=tmp_path / "normalized",
        region="all-czechia",
        listing_id=normalized_record.listing_id,
        snapshot_name="2026-03-19T11-27-24.855716+00-00.json",
        payload=normalized_record.to_serializable_dict(),
    )
    output_dir = tmp_path / "enriched"
    service = FilesystemEnrichmentWorkflowService(
        normalized_snapshot_source=FilesystemNormalizedSnapshotSource(input_dir=input_dir),
        enriched_record_repository=FilesystemEnrichedRecordRepository(output_dir=output_dir),
    )

    enriched_count = service.enrich(
        EnrichmentWorkflowSelection(listing_id=normalized_record.listing_id),
    )

    assert enriched_count == 1
    output_paths = sorted(output_dir.rglob("*.json"))
    assert len(output_paths) == 1
    latest_record = json.loads(output_paths[0].read_text(encoding="utf-8"))
    assert latest_record["enrichment_version"] == "enriched-listing-v16"
    assert latest_record["location_features"]["latitude"] == 50.0577347
    assert latest_record["location_features"]["longitude"] == 14.3723456
    assert latest_record["location_features"]["location_precision"] == "listing"
    assert latest_record["location_features"]["geocoding_source"] == (
        "detail_locality_payload"
    )
    assert latest_record["location_features"]["geocoding_match_strategy"] == (
        "source_detail_coordinate"
    )
    assert latest_record["location_features"]["geocoding_fallback_level"] == "none"
    assert latest_record["location_features"]["geocoding_is_fallback"] is False
    assert latest_record["location_features"]["spatial_grid_source_precision"] == "listing"
    assert latest_record["location_features"]["spatial_grid_is_approximate"] is False


def _build_fixture_normalized_dataset(target_root: Path, fixture_paths: tuple[str, ...]) -> Path:
    """Copy representative normalized fixtures into a temporary workflow input directory."""

    for fixture_path in fixture_paths:
        source_path = Path(fixture_path)
        relative_path = source_path.relative_to("data/normalized")
        destination_path = target_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)
    return target_root


def _write_normalized_fixture(
    *,
    target_root: Path,
    region: str,
    listing_id: str,
    snapshot_name: str,
    payload: dict[str, object],
) -> Path:
    """Write one serialized normalized snapshot into a temporary workflow directory."""

    destination_path = target_root / region / listing_id / snapshot_name
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target_root
