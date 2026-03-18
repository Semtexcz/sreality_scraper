"""Tests for enrichment-stage contracts and deterministic derived features."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from scraperweb.enrichment import ENRICHMENT_VERSION, NormalizedListingEnricher
from scraperweb.normalization.models import (
    NormalizedEnergyDetails,
    NormalizationMetadata,
    NormalizedBuilding,
    NormalizedCoreAttributes,
    NormalizedListingRecord,
    NormalizedLocation,
    NormalizedPrice,
)
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata


def test_enricher_derives_explicit_features_from_normalized_record() -> None:
    """Compute the V1 enrichment feature set from normalized inputs only."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk 58 m², Praha 8 - Karlín",
        amount_text="8 490 000 Kč",
        price_note="včetně provize",
        energy_efficiency_class="Velmi úsporná",
        city="Praha 8",
        city_district="Karlín",
    )
    enricher = NormalizedListingEnricher()

    enriched_record = enricher.enrich(normalized_record)

    assert enriched_record.listing_id == normalized_record.listing_id
    assert enriched_record.source_url == normalized_record.source_url
    assert enriched_record.captured_at_utc == normalized_record.captured_at_utc
    assert enriched_record.enrichment_version == ENRICHMENT_VERSION
    assert enriched_record.normalized_record == normalized_record
    assert enriched_record.price_features.asking_price_czk == 8_490_000
    assert enriched_record.price_features.price_per_square_meter_czk == 146_379.31
    assert enriched_record.price_features.has_price_note is True
    assert enriched_record.property_features.disposition == "2+kk"
    assert enriched_record.property_features.floor_area_sqm == 58.0
    assert enriched_record.property_features.has_energy_efficiency_rating is True
    assert enriched_record.property_features.has_city_district is True
    assert enriched_record.property_features.is_prague_listing is True
    assert enriched_record.enrichment_metadata is not None
    assert enriched_record.enrichment_metadata.enriched_at_utc == (
        normalized_record.normalized_at_utc
    )
    assert enriched_record.enrichment_metadata.source_normalization_version == (
        normalized_record.normalization_version
    )
    assert len(enriched_record.enrichment_metadata.derivation_notes) == 3


def test_enricher_keeps_missing_derived_values_explicit_and_stays_deterministic() -> None:
    """Represent missing derived features as ``None`` and keep repeated output equal."""

    normalized_record = _build_normalized_record(
        title="Byt 1+kk",
        amount_text=None,
        price_note=None,
        energy_efficiency_class=None,
        city="Brno",
        city_district=None,
    )
    enricher = NormalizedListingEnricher()

    first_record = enricher.enrich(normalized_record)
    second_record = enricher.enrich(normalized_record)

    assert first_record == second_record
    assert first_record.price_features.asking_price_czk is None
    assert first_record.price_features.price_per_square_meter_czk is None
    assert first_record.price_features.has_price_note is False
    assert first_record.property_features.disposition == "1+kk"
    assert first_record.property_features.floor_area_sqm is None
    assert first_record.property_features.has_energy_efficiency_rating is False
    assert first_record.property_features.has_city_district is False
    assert first_record.property_features.is_prague_listing is False


def test_enricher_rejects_non_normalized_inputs() -> None:
    """Keep enrichment isolated from scraper-stage contracts and raw payloads."""

    raw_record = RawListingRecord(
        listing_id="raw-1",
        source_url="https://example.test/raw-1",
        captured_at_utc=datetime(2026, 3, 17, 10, 0, 0, tzinfo=timezone.utc),
        source_payload={"Název": "Byt 2+kk 58 m², Praha 8 - Karlín"},
        source_metadata=RawSourceMetadata(
            region="praha",
            listing_page_number=1,
            scrape_run_id="run-raw",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    enricher = NormalizedListingEnricher()

    with pytest.raises(
        TypeError,
        match="NormalizedListingEnricher accepts NormalizedListingRecord only.",
    ):
        enricher.enrich(raw_record)  # type: ignore[arg-type]


def _build_normalized_record(
    *,
    title: str | None,
    amount_text: str | None,
    price_note: str | None,
    energy_efficiency_class: str | None,
    city: str | None,
    city_district: str | None,
) -> NormalizedListingRecord:
    """Build a normalized record fixture for enrichment tests."""

    return NormalizedListingRecord(
        listing_id="2222222222",
        source_url="https://www.sreality.cz/detail/prodej/byt/praha-karlin/2222222222",
        captured_at_utc=datetime(2026, 3, 17, 11, 22, 33, tzinfo=timezone.utc),
        normalized_at_utc=datetime(2026, 3, 17, 11, 22, 33, tzinfo=timezone.utc),
        normalization_version="normalized-listing-v1",
        core_attributes=NormalizedCoreAttributes(
            title=title,
            price=NormalizedPrice(
                amount_text=amount_text,
                amount_czk=8_490_000 if amount_text == "8 490 000 Kč" else None,
                currency_code="CZK" if amount_text == "8 490 000 Kč" else None,
                pricing_mode="fixed_amount" if amount_text == "8 490 000 Kč" else None,
                note=price_note,
            ),
            building=NormalizedBuilding(
                material="Cihla",
                physical_condition="Ve velmi dobrém stavu",
            ),
            source_specific_attributes={
                "Vybavení:": ["Sklep", "Balkon"],
            },
        ),
        location=NormalizedLocation(
            location_text=(
                f"{city} - {city_district}"
                if city is not None and city_district is not None
                else city
            ),
            city=city,
            city_district=city_district,
        ),
        normalization_metadata=NormalizationMetadata(
            source_contract_version="raw-listing-record-v1",
            source_parser_version="sreality-detail-v1",
            source_region="praha",
            source_listing_page_number=4,
            source_scrape_run_id="run-123",
            source_captured_from="detail_page",
            source_http_status=200,
        ),
        energy_details=NormalizedEnergyDetails(
            efficiency_class=energy_efficiency_class,
        ),
    )
