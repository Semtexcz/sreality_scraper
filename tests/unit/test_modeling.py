"""Tests for modeling-stage contracts and the full linear pipeline handoff."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

import pytest

from scraperweb.application.linear_pipeline_service import LinearListingPipelineService
from scraperweb.enrichment import ENRICHMENT_VERSION, NormalizedListingEnricher
from scraperweb.modeling import (
    MODEL_VERSION,
    MODELING_INPUT_VERSION,
    EnrichedListingModelingInputBuilder,
)
from scraperweb.normalization import NORMALIZATION_VERSION, RawListingNormalizer
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata


class StubRawListingCollector:
    """Minimal collector stub that emits configured raw listing records."""

    def __init__(self, records: list[RawListingRecord]) -> None:
        """Store deterministic raw records for pipeline tests."""

        self._records = records
        self.calls: list[tuple[str, int | None]] = []

    def collect_region_records(
        self,
        district_link: str,
        max_pages: int | None,
    ) -> Iterator[RawListingRecord]:
        """Yield configured records while recording invocation arguments."""

        self.calls.append((district_link, max_pages))
        yield from self._records


def test_modeling_builder_maps_enriched_record_into_model_ready_contract() -> None:
    """Build the current model-ready contract from enriched records only."""

    enriched_record = NormalizedListingEnricher().enrich(
        _build_raw_listing_normalizer().normalize(_build_raw_record()),
    )
    builder = EnrichedListingModelingInputBuilder()

    modeling_record = builder.build(enriched_record)

    assert modeling_record.listing_id == enriched_record.listing_id
    assert modeling_record.source_url == enriched_record.source_url
    assert modeling_record.captured_at_utc == enriched_record.captured_at_utc
    assert modeling_record.model_version == MODEL_VERSION
    assert modeling_record.modeling_input_version == MODELING_INPUT_VERSION
    assert modeling_record.features.disposition == "2+kk"
    assert modeling_record.features.floor_area_sqm == 58.0
    assert modeling_record.features.asking_price_czk == 8_490_000
    assert modeling_record.features.price_per_square_meter_czk == 146_379.31
    assert modeling_record.features.is_ground_floor is None
    assert modeling_record.features.is_upper_floor is None
    assert modeling_record.features.relative_floor_position is None
    assert modeling_record.features.is_top_floor is None
    assert modeling_record.features.is_new_build is None
    assert modeling_record.features.building_material_bucket == "masonry"
    assert modeling_record.features.building_condition_bucket is None
    assert modeling_record.features.energy_efficiency_bucket == "efficient"
    assert modeling_record.features.has_price_note is True
    assert modeling_record.features.has_energy_efficiency_rating is True
    assert modeling_record.features.has_city_district is True
    assert modeling_record.features.is_prague_listing is True
    assert modeling_record.targets.asking_price_czk == 8_490_000
    assert modeling_record.modeling_metadata is not None
    assert modeling_record.modeling_metadata.modeled_at_utc == (
        enriched_record.enrichment_metadata.enriched_at_utc
    )
    assert modeling_record.modeling_metadata.source_enrichment_version == (
        enriched_record.enrichment_version
    )
    assert modeling_record.modeling_metadata.source_normalization_version == (
        enriched_record.normalized_record.normalization_version
    )
    assert modeling_record.enriched_record == enriched_record


def test_modeling_builder_rejects_non_enriched_inputs() -> None:
    """Keep modeling isolated from normalization contracts and raw payloads."""

    normalized_record = _build_raw_listing_normalizer().normalize(_build_raw_record())
    builder = EnrichedListingModelingInputBuilder()

    with pytest.raises(
        TypeError,
        match=(
            "EnrichedListingModelingInputBuilder accepts "
            "EnrichedListingRecord only."
        ),
    ):
        builder.build(normalized_record)  # type: ignore[arg-type]


def test_linear_pipeline_service_composes_full_stage_handoffs() -> None:
    """Emit model-ready records through scraper, normalization, enrichment, and modeling."""

    raw_record = _build_raw_record()
    collector = StubRawListingCollector(records=[raw_record])
    pipeline = LinearListingPipelineService(
        raw_listing_collector=collector,
        raw_listing_normalizer=_build_raw_listing_normalizer(),
        normalized_listing_enricher=NormalizedListingEnricher(),
        modeling_input_builder=EnrichedListingModelingInputBuilder(),
    )

    modeling_records = list(
        pipeline.collect_modeling_inputs(
            district_link="https://example.test/praha/",
            max_pages=3,
            max_estates=5,
        ),
    )

    assert collector.calls == [("https://example.test/praha/", 3)]
    assert len(modeling_records) == 1
    modeling_record = modeling_records[0]
    assert modeling_record.listing_id == raw_record.listing_id
    assert modeling_record.modeling_metadata is not None
    assert modeling_record.modeling_metadata.dataset_lineage == (
        "raw-listing-record-v1",
        NORMALIZATION_VERSION,
        ENRICHMENT_VERSION,
        "modeling-input-v3",
    )
    assert modeling_record.enriched_record is not None
    assert modeling_record.enriched_record.normalized_record.listing_id == raw_record.listing_id


def test_linear_pipeline_service_keeps_modeling_path_optional() -> None:
    """Allow the dedicated linear pipeline to stay separate from raw acquisition flow."""

    collector = StubRawListingCollector(records=[_build_raw_record(), _build_raw_record()])
    pipeline = LinearListingPipelineService(raw_listing_collector=collector)

    modeling_records = list(
        pipeline.collect_modeling_inputs(
            district_link="https://example.test/praha/",
            max_pages=1,
            max_estates=1,
        ),
    )

    assert len(modeling_records) == 1


def _build_raw_listing_normalizer() -> RawListingNormalizer:
    """Build a normalizer instance for modeling-stage tests."""

    return RawListingNormalizer()


def _build_raw_record() -> RawListingRecord:
    """Build a representative raw record fixture for full pipeline tests."""

    return RawListingRecord(
        listing_id="2222222222",
        source_url="https://www.sreality.cz/detail/prodej/byt/praha-karlin/2222222222",
        captured_at_utc=datetime(2026, 3, 17, 11, 22, 33, tzinfo=timezone.utc),
        source_payload={
            "Název": "Byt 2+kk, Praha 8 - Karlín",
            "Celková cena:": "8 490 000 Kč",
            "Poznámka k ceně:": "včetně provize",
            "Plocha:": "Užitná plocha 58 m², Celková plocha 62 m²",
            "Stavba:": "Cihla, Velmi dobrý",
            "Energetická náročnost:": "B",
        },
        source_metadata=RawSourceMetadata(
            region="praha",
            listing_page_number=4,
            scrape_run_id="run-123",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
