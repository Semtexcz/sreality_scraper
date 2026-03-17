"""Tests for normalization-stage contracts and deterministic raw mapping."""

from __future__ import annotations

from datetime import datetime, timezone

from scraperweb.normalization import NORMALIZATION_VERSION, RawListingNormalizer
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata


def test_normalizer_maps_representative_raw_record_into_stable_contract() -> None:
    """Map representative raw payload fields into the normalized contract."""

    raw_record = RawListingRecord(
        listing_id="2222222222",
        source_url="https://www.sreality.cz/detail/prodej/byt/praha-karlin/2222222222",
        captured_at_utc=datetime(2026, 3, 17, 11, 22, 33, tzinfo=timezone.utc),
        source_payload={
            "Název": "Byt 2+kk 58 m², Praha 8 - Karlín",
            "Celková cena:": "8 490 000 Kč",
            "Poznámka k ceně:": "včetně provize",
            "Stavba:": "Cihla, Velmi dobrý",
            "Energetická náročnost:": "B",
            "Vybavení:": ["Sklep", "Balkon"],
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
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.listing_id == raw_record.listing_id
    assert normalized_record.source_url == raw_record.source_url
    assert normalized_record.captured_at_utc == raw_record.captured_at_utc
    assert normalized_record.normalized_at_utc == raw_record.captured_at_utc
    assert normalized_record.normalization_version == NORMALIZATION_VERSION
    assert normalized_record.core_attributes.title == "Byt 2+kk 58 m², Praha 8 - Karlín"
    assert normalized_record.core_attributes.price.amount_text == "8 490 000 Kč"
    assert normalized_record.core_attributes.price.note == "včetně provize"
    assert normalized_record.core_attributes.building.material == "Cihla"
    assert normalized_record.core_attributes.building.condition == "Velmi dobrý"
    assert normalized_record.core_attributes.building.energy_efficiency_class == "B"
    assert normalized_record.core_attributes.source_specific_attributes == {
        "Vybavení:": ["Sklep", "Balkon"],
    }
    assert normalized_record.location.location_text == "Praha 8 - Karlín"
    assert normalized_record.location.city == "Praha 8"
    assert normalized_record.location.city_district == "Karlín"
    assert normalized_record.normalization_metadata.source_contract_version == (
        "raw-listing-record-v1"
    )
    assert normalized_record.normalization_metadata.source_parser_version == (
        "sreality-detail-v1"
    )
    assert normalized_record.normalization_metadata.source_region == "praha"
    assert normalized_record.normalization_metadata.source_listing_page_number == 4
    assert normalized_record.normalization_metadata.source_scrape_run_id == "run-123"
    assert normalized_record.normalization_metadata.source_captured_from == "detail_page"
    assert normalized_record.normalization_metadata.source_http_status == 200


def test_normalizer_represents_missing_and_partial_values_with_none() -> None:
    """Keep missing typed values explicit while preserving source-specific fields."""

    raw_record = RawListingRecord(
        listing_id="partial-1",
        source_url="https://www.sreality.cz/detail/prodej/byt/praha/partial-1",
        captured_at_utc=datetime(2026, 3, 17, 12, 0, 0, tzinfo=timezone.utc),
        source_payload={
            "Název": "Byt 1+kk",
            "Stavba:": "Panel",
            "Dispozice:": "1+kk",
            "Makléř:": {"jméno": "Example Broker"},
        },
        source_metadata=RawSourceMetadata(
            region="praha",
            listing_page_number=1,
            scrape_run_id="run-456",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.core_attributes.price.amount_text is None
    assert normalized_record.core_attributes.price.note is None
    assert normalized_record.core_attributes.building.material == "Panel"
    assert normalized_record.core_attributes.building.condition is None
    assert normalized_record.core_attributes.building.energy_efficiency_class is None
    assert normalized_record.location.location_text is None
    assert normalized_record.location.city is None
    assert normalized_record.location.city_district is None
    assert list(normalized_record.core_attributes.source_specific_attributes) == [
        "Dispozice:",
        "Makléř:",
    ]


def test_normalizer_is_idempotent_for_identical_raw_input() -> None:
    """Produce identical normalized output for repeated normalization of one record."""

    raw_record = RawListingRecord(
        listing_id="stable-1",
        source_url="https://www.sreality.cz/detail/prodej/byt/praha/stable-1",
        captured_at_utc=datetime(2026, 3, 17, 13, 0, 0, tzinfo=timezone.utc),
        source_payload={
            "Název": "Byt 3+kk 70 m², Praha 4 - Nusle",
            "Celková cena:": "9 250 000 Kč",
        },
        source_metadata=RawSourceMetadata(
            region="praha",
            listing_page_number=2,
            scrape_run_id="run-789",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    normalizer = RawListingNormalizer()

    first_record = normalizer.normalize(raw_record)
    second_record = normalizer.normalize(raw_record)

    assert first_record == second_record
