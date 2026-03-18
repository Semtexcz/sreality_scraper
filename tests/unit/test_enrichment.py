"""Tests for enrichment-stage contracts and deterministic derived features."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from scraperweb.enrichment import ENRICHMENT_VERSION, NormalizedListingEnricher
from scraperweb.normalization.models import (
    NormalizedAreaDetails,
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
    """Compute the current enrichment feature set from normalized inputs only."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Praha 8 - Karlín",
        amount_text="8 490 000 Kč",
        price_note="včetně provize",
        energy_efficiency_class="Velmi úsporná",
        city="Praha 8",
        city_district="Karlín",
        usable_area_sqm=58.0,
        total_area_sqm=62.0,
        physical_condition="Novostavba",
        floor_position=7,
        total_floor_count=7,
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
    assert enriched_record.price_features.price_per_usable_sqm_czk == 146_379.31
    assert enriched_record.price_features.price_per_total_sqm_czk == 136_935.48
    assert enriched_record.price_features.has_price_note is True
    assert enriched_record.property_features.disposition == "2+kk"
    assert enriched_record.property_features.canonical_area_sqm == 58.0
    assert enriched_record.property_features.usable_area_sqm == 58.0
    assert enriched_record.property_features.total_area_sqm == 62.0
    assert enriched_record.property_features.floor_area_sqm == 58.0
    assert enriched_record.property_features.is_top_floor is True
    assert enriched_record.property_features.is_new_build is True
    assert enriched_record.property_features.energy_efficiency_bucket == "efficient"
    assert enriched_record.property_features.has_energy_efficiency_rating is True
    assert enriched_record.property_features.has_city_district is True
    assert enriched_record.property_features.is_prague_listing is True
    assert enriched_record.location_features.municipality_name == "Praha"
    assert enriched_record.location_features.municipality_code == "554782"
    assert enriched_record.location_features.district_code == "CZ0100"
    assert enriched_record.location_features.region_code == "CZ010"
    assert enriched_record.location_features.municipality_latitude == 50.075638
    assert enriched_record.location_features.municipality_longitude == 14.4379
    assert enriched_record.location_features.distance_to_okresni_mesto_km == 0.0
    assert enriched_record.location_features.distance_to_orp_center_km == 0.0
    assert enriched_record.location_features.is_district_city is True
    assert enriched_record.location_features.is_orp_center is True
    assert enriched_record.location_features.orp_code == "1000"
    assert enriched_record.location_features.city_district_normalized == "Praha 8"
    assert enriched_record.location_features.municipality_match_status == "matched"
    assert enriched_record.location_features.municipality_match_method == (
        "city_prague_numbered"
    )
    assert enriched_record.location_features.municipality_match_input == "Praha 8"
    assert enriched_record.enrichment_metadata is not None
    assert enriched_record.enrichment_metadata.enriched_at_utc == (
        normalized_record.normalized_at_utc
    )
    assert enriched_record.enrichment_metadata.source_normalization_version == (
        normalized_record.normalization_version
    )
    assert len(enriched_record.enrichment_metadata.derivation_notes) == 10


def test_enricher_keeps_missing_derived_values_explicit_and_stays_deterministic() -> None:
    """Represent missing derived features as ``None`` and keep repeated output equal."""

    normalized_record = _build_normalized_record(
        title="Byt 1+kk",
        amount_text=None,
        price_note=None,
        energy_efficiency_class=None,
        city="Brno",
        city_district=None,
        usable_area_sqm=None,
        total_area_sqm=None,
        physical_condition=None,
        floor_position=None,
        total_floor_count=None,
    )
    enricher = NormalizedListingEnricher()

    first_record = enricher.enrich(normalized_record)
    second_record = enricher.enrich(normalized_record)

    assert first_record == second_record
    assert first_record.price_features.asking_price_czk is None
    assert first_record.price_features.price_per_square_meter_czk is None
    assert first_record.price_features.price_per_usable_sqm_czk is None
    assert first_record.price_features.price_per_total_sqm_czk is None
    assert first_record.price_features.has_price_note is False
    assert first_record.property_features.disposition == "1+kk"
    assert first_record.property_features.canonical_area_sqm is None
    assert first_record.property_features.usable_area_sqm is None
    assert first_record.property_features.total_area_sqm is None
    assert first_record.property_features.floor_area_sqm is None
    assert first_record.property_features.is_top_floor is None
    assert first_record.property_features.is_new_build is None
    assert first_record.property_features.energy_efficiency_bucket is None
    assert first_record.property_features.has_energy_efficiency_rating is False
    assert first_record.property_features.has_city_district is False
    assert first_record.property_features.is_prague_listing is False
    assert first_record.location_features.municipality_name == "Brno"
    assert first_record.location_features.municipality_code == "582786"
    assert first_record.location_features.district_code == "CZ0642"
    assert first_record.location_features.region_code == "CZ064"
    assert first_record.location_features.municipality_latitude == 49.19516
    assert first_record.location_features.municipality_longitude == 16.606937
    assert first_record.location_features.distance_to_okresni_mesto_km == 0.0
    assert first_record.location_features.distance_to_orp_center_km == 0.0
    assert first_record.location_features.is_district_city is True
    assert first_record.location_features.is_orp_center is True
    assert first_record.location_features.city_district_normalized is None
    assert first_record.location_features.municipality_match_status == "matched"
    assert first_record.location_features.municipality_match_method == "city"


def test_enricher_derives_building_and_energy_features_from_normalized_fields() -> None:
    """Derive building and energy semantics from explicit normalized sub-fields."""

    normalized_record = _build_normalized_record(
        title="Byt 3+kk, Brno - Žabovřesky",
        amount_text="11 340 000 Kč",
        price_note=None,
        energy_efficiency_class="Méně úsporná",
        city="Brno",
        city_district="Žabovřesky",
        usable_area_sqm=81.0,
        total_area_sqm=None,
        physical_condition="Před rekonstrukcí",
        floor_position=3,
        total_floor_count=5,
    )
    enricher = NormalizedListingEnricher()

    enriched_record = enricher.enrich(normalized_record)

    assert enriched_record.price_features.asking_price_czk == 11_340_000
    assert enriched_record.price_features.price_per_square_meter_czk == 140_000.0
    assert enriched_record.property_features.is_top_floor is False
    assert enriched_record.property_features.is_new_build is False
    assert enriched_record.property_features.energy_efficiency_bucket == "average"
    assert enriched_record.property_features.has_energy_efficiency_rating is True


def test_enricher_keeps_unknown_energy_bucket_optional() -> None:
    """Keep ambiguous energy bucketing unset when the normalized class is unsupported."""

    normalized_record = _build_normalized_record(
        title="Byt 2+1, Ostrava - Poruba",
        amount_text="4 800 000 Kč",
        price_note=None,
        energy_efficiency_class="Neznámá třída",
        city="Ostrava",
        city_district="Poruba",
        usable_area_sqm=64.0,
        total_area_sqm=None,
        physical_condition="Velmi dobrý",
        floor_position=4,
        total_floor_count=8,
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.property_features.energy_efficiency_bucket is None


def test_enricher_marks_duplicate_municipality_names_as_ambiguous_without_district_hint() -> None:
    """Keep duplicate municipality names unresolved when no safe hint exists."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Adamov",
        amount_text="5 500 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Adamov",
        city_district=None,
        usable_area_sqm=50.0,
        total_area_sqm=None,
        physical_condition=None,
        floor_position=None,
        total_floor_count=None,
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.municipality_name is None
    assert enriched_record.location_features.municipality_code is None
    assert enriched_record.location_features.municipality_match_status == "ambiguous"
    assert enriched_record.location_features.municipality_match_method == "city"
    assert enriched_record.location_features.municipality_match_input == "Adamov"
    assert enriched_record.location_features.municipality_match_candidates == (
        "Adamov (České Budějovice) [535826]",
        "Adamov (Blansko) [581291]",
        "Adamov (Kutná Hora) [531367]",
    )


def test_enricher_uses_location_text_district_hint_to_resolve_duplicate_municipality_names() -> None:
    """Resolve duplicate municipality names only when location text names one district."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Adamov - Blansko",
        amount_text="5 500 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Adamov",
        city_district="Blansko",
        usable_area_sqm=50.0,
        total_area_sqm=None,
        physical_condition=None,
        floor_position=None,
        total_floor_count=None,
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.municipality_name == "Adamov"
    assert enriched_record.location_features.municipality_code == "581291"
    assert enriched_record.location_features.district_name == "Blansko"
    assert enriched_record.location_features.region_name == "Jihomoravský kraj"
    assert enriched_record.location_features.municipality_latitude == 49.295708
    assert enriched_record.location_features.municipality_longitude == 16.663955
    assert enriched_record.location_features.distance_to_okresni_mesto_km == 7.787
    assert enriched_record.location_features.distance_to_orp_center_km == 7.787
    assert enriched_record.location_features.is_district_city is False
    assert enriched_record.location_features.is_orp_center is False
    assert enriched_record.location_features.city_district_normalized == "Blansko"
    assert enriched_record.location_features.municipality_match_status == "matched"
    assert enriched_record.location_features.municipality_match_method == (
        "city_and_location_text_district"
    )


def test_enricher_keeps_non_matching_locations_explicitly_unresolved() -> None:
    """Leave unmatched municipality joins empty instead of guessing a reference row."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Atlantis",
        amount_text="5 500 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Atlantis",
        city_district=None,
        usable_area_sqm=50.0,
        total_area_sqm=None,
        physical_condition=None,
        floor_position=None,
        total_floor_count=None,
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.municipality_name is None
    assert enriched_record.location_features.municipality_code is None
    assert enriched_record.location_features.district_code is None
    assert enriched_record.location_features.region_code is None
    assert enriched_record.location_features.municipality_latitude is None
    assert enriched_record.location_features.municipality_longitude is None
    assert enriched_record.location_features.distance_to_okresni_mesto_km is None
    assert enriched_record.location_features.distance_to_orp_center_km is None
    assert enriched_record.location_features.is_district_city is None
    assert enriched_record.location_features.is_orp_center is None
    assert enriched_record.location_features.municipality_match_status == "unmatched"
    assert enriched_record.location_features.municipality_match_method == "city"
    assert enriched_record.location_features.municipality_match_input == "Atlantis"


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


def test_enricher_falls_back_to_total_area_for_canonical_area_metrics() -> None:
    """Use total area only when usable area is missing from normalized fields."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Brno - Centrum",
        amount_text="6 000 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Brno",
        city_district="Centrum",
        usable_area_sqm=None,
        total_area_sqm=75.0,
        physical_condition=None,
        floor_position=None,
        total_floor_count=None,
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.property_features.canonical_area_sqm == 75.0
    assert enriched_record.property_features.usable_area_sqm is None
    assert enriched_record.property_features.total_area_sqm == 75.0
    assert enriched_record.property_features.floor_area_sqm == 75.0
    assert enriched_record.price_features.price_per_square_meter_czk == 80_000.0
    assert enriched_record.price_features.price_per_usable_sqm_czk is None
    assert enriched_record.price_features.price_per_total_sqm_czk == 80_000.0


def test_enricher_keeps_zero_area_values_optional() -> None:
    """Treat zero-valued normalized area fields as missing derived inputs."""

    normalized_record = _build_normalized_record(
        title="Byt 1+kk, Brno",
        amount_text="3 000 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Brno",
        city_district=None,
        usable_area_sqm=0.0,
        total_area_sqm=0.0,
        physical_condition=None,
        floor_position=None,
        total_floor_count=None,
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.property_features.canonical_area_sqm is None
    assert enriched_record.property_features.usable_area_sqm is None
    assert enriched_record.property_features.total_area_sqm is None
    assert enriched_record.property_features.floor_area_sqm is None
    assert enriched_record.price_features.price_per_square_meter_czk is None
    assert enriched_record.price_features.price_per_usable_sqm_czk is None
    assert enriched_record.price_features.price_per_total_sqm_czk is None


def _build_normalized_record(
    *,
    title: str | None,
    amount_text: str | None,
    price_note: str | None,
    energy_efficiency_class: str | None,
    city: str | None,
    city_district: str | None,
    usable_area_sqm: float | None,
    total_area_sqm: float | None,
    physical_condition: str | None,
    floor_position: int | None,
    total_floor_count: int | None,
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
                amount_czk=_parse_amount_czk(amount_text),
                currency_code="CZK" if amount_text is not None else None,
                pricing_mode="fixed_amount" if amount_text is not None else None,
                note=price_note,
            ),
            building=NormalizedBuilding(
                material="Cihla",
                physical_condition=physical_condition,
                floor_position=floor_position,
                total_floor_count=total_floor_count,
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
        area_details=NormalizedAreaDetails(
            source_text=None,
            usable_area_sqm=usable_area_sqm,
            total_area_sqm=total_area_sqm,
        ),
        energy_details=NormalizedEnergyDetails(
            efficiency_class=energy_efficiency_class,
        ),
    )


def _parse_amount_czk(amount_text: str | None) -> int | None:
    """Convert one normalized fixed-price fixture string into an integer amount."""

    if amount_text is None:
        return None
    return int(amount_text.replace(" Kč", "").replace(" ", ""))
