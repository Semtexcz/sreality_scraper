"""Tests for normalization-stage contracts and deterministic raw mapping."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from scraperweb.normalization import NORMALIZATION_VERSION, RawListingNormalizer
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata


def _load_raw_record_from_snapshot(relative_path: str) -> RawListingRecord:
    """Load one persisted raw snapshot into the scraper-stage record contract."""

    snapshot_path = Path(relative_path)
    serialized_record = json.loads(snapshot_path.read_text(encoding="utf-8"))
    source_metadata = RawSourceMetadata(**serialized_record["source_metadata"])
    return RawListingRecord(
        listing_id=serialized_record["listing_id"],
        source_url=serialized_record["source_url"],
        captured_at_utc=datetime.fromisoformat(serialized_record["captured_at_utc"]),
        source_payload=serialized_record["source_payload"],
        source_metadata=source_metadata,
        raw_page_snapshot=serialized_record["raw_page_snapshot"],
    )


def test_normalizer_maps_real_snapshot_into_broader_stable_contract() -> None:
    """Map a representative stored detail snapshot into the expanded contract."""

    raw_record = _load_raw_record_from_snapshot(
        "data/raw/all-czechia/2664846156/2026-03-18T08-56-47.724202+00-00.json",
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.listing_id == raw_record.listing_id
    assert normalized_record.source_url == raw_record.source_url
    assert normalized_record.captured_at_utc == raw_record.captured_at_utc
    assert normalized_record.normalized_at_utc == raw_record.captured_at_utc
    assert normalized_record.normalization_version == NORMALIZATION_VERSION
    assert normalized_record.core_attributes.title == (
        "Prodej bytu 3+1 77m²Cihlářská, Blansko"
    )
    assert normalized_record.core_attributes.price.amount_text == "6400000Kč"
    assert normalized_record.core_attributes.price.amount_czk == 6_400_000
    assert normalized_record.core_attributes.price.currency_code == "CZK"
    assert normalized_record.core_attributes.price.pricing_mode == "fixed_amount"
    assert normalized_record.core_attributes.price.note == (
        "Cena včetně provize a kompletního právního servisu"
    )
    assert normalized_record.core_attributes.building.source_text == (
        "Cihlová, Ve velmi dobrém stavu, 5. podlaží"
    )
    assert normalized_record.core_attributes.building.material == "Cihlová"
    assert normalized_record.core_attributes.building.structural_attributes == ()
    assert normalized_record.core_attributes.building.physical_condition == (
        "Ve velmi dobrém stavu"
    )
    assert normalized_record.core_attributes.building.floor_position == 5
    assert normalized_record.core_attributes.building.total_floor_count is None
    assert normalized_record.core_attributes.building.underground_floor_count is None
    assert normalized_record.core_attributes.building.unparsed_fragments == ()
    assert normalized_record.area_details.source_text == "Užitná plocha 77 m²"
    assert normalized_record.area_details.usable_area_sqm == 77.0
    assert normalized_record.area_details.total_area_sqm is None
    assert normalized_record.area_details.built_up_area_sqm is None
    assert normalized_record.area_details.garden_area_sqm is None
    assert normalized_record.area_details.unparsed_fragments == ()
    assert normalized_record.energy_details.source_text == "Mimořádně nehospodárná"
    assert normalized_record.energy_details.efficiency_class == "Mimořádně nehospodárná"
    assert normalized_record.energy_details.regulation_reference is None
    assert normalized_record.energy_details.consumption_kwh_per_sqm_year is None
    assert normalized_record.energy_details.additional_descriptors == ()
    assert normalized_record.energy_details.unparsed_fragments == ()
    assert normalized_record.ownership.ownership_type == "Osobní"
    assert normalized_record.listing_lifecycle.listed_on == date(2026, 3, 16)
    assert normalized_record.listing_lifecycle.listed_on_text == "16. 3. 2026"
    assert normalized_record.listing_lifecycle.updated_on == date(2026, 3, 18)
    assert normalized_record.listing_lifecycle.updated_on_text == "18. 3. 2026"
    assert normalized_record.source_identifiers.source_listing_reference == "00183"
    for mapped_key in (
        "ID zakázky:",
        "Lokalita:",
        "Plocha:",
        "Upraveno:",
        "Vlastnictví:",
        "Vloženo:",
        "Bankomat:",
        "Bus MHD:",
        "Cukrárna:",
        "Hospoda:",
        "Hřiště:",
        "Kino:",
        "Lékař:",
        "Lékárna:",
        "Obchod:",
        "Pošta:",
        "Restaurace:",
        "Sportoviště:",
        "Veterinář:",
        "Večerka:",
        "Vlak:",
        "Škola:",
        "Školka:",
    ):
        assert mapped_key not in normalized_record.core_attributes.source_specific_attributes
    assert normalized_record.core_attributes.source_specific_attributes == {
        "Infrastruktura:": (
            "Vodovod:Vodovod, Plyn:Plynovod, Zdroj vytápění:Plynový kotel, "
            "Vytápěcí těleso:Radiátory, Kanalizace:Veřejná kanalizace, "
            "Telekomunikace:Internet, Kabelová televize, Kabelové rozvody, "
            "Doprava:Vlak, Silnice, MHD, Autobus, Komunikace:Asfaltová"
        ),
        "Příslušenství:": (
            "Bez výtahuNezařízenoBalkonSklep, Bez výtahu, Nezařízeno, Balkon, Sklep"
        ),
        "Zobrazeno:": "1410×",
    }
    assert normalized_record.location.location_text == "Blansko"
    assert normalized_record.location.location_text_source == "title_fallback"
    assert normalized_record.location.city == "Blansko"
    assert normalized_record.location.city_source == "title_fallback"
    assert normalized_record.location.city_district is None
    assert normalized_record.location.city_district_source is None
    assert normalized_record.location.location_descriptor == "Klidná část obce, Bydlení"
    assert normalized_record.location.location_descriptor_source == (
        "source_payload:Lokalita:"
    )
    nearby_places_by_source_key = {
        place.source_key: place for place in normalized_record.location.nearby_places
    }
    assert len(normalized_record.location.nearby_places) == 17
    assert set(nearby_places_by_source_key) == {
        "Bankomat:",
        "Bus MHD:",
        "Cukrárna:",
        "Hospoda:",
        "Hřiště:",
        "Kino:",
        "Lékař:",
        "Lékárna:",
        "Obchod:",
        "Pošta:",
        "Restaurace:",
        "Sportoviště:",
        "Veterinář:",
        "Večerka:",
        "Vlak:",
        "Škola:",
        "Školka:",
    }
    assert nearby_places_by_source_key["Bankomat:"].category == "bankomat"
    assert nearby_places_by_source_key["Bankomat:"].source_text == (
        "Bankomat ČSOB(856 m)"
    )
    assert nearby_places_by_source_key["Bankomat:"].name == "Bankomat ČSOB"
    assert nearby_places_by_source_key["Bankomat:"].distance_m == 856
    assert nearby_places_by_source_key["Hřiště:"].category == "hriste"
    assert nearby_places_by_source_key["Hřiště:"].source_text == "(167 m)"
    assert nearby_places_by_source_key["Hřiště:"].name is None
    assert nearby_places_by_source_key["Hřiště:"].distance_m == 167
    assert nearby_places_by_source_key["Školka:"].category == "skolka"
    assert nearby_places_by_source_key["Školka:"].source_text == (
        "MŠ Blansko, Dvorská 96(811 m)"
    )
    assert nearby_places_by_source_key["Školka:"].name == "MŠ Blansko, Dvorská 96"
    assert nearby_places_by_source_key["Školka:"].distance_m == 811
    assert normalized_record.normalization_metadata.source_contract_version == (
        "raw-listing-record-v1"
    )
    assert normalized_record.normalization_metadata.source_parser_version == (
        "sreality-detail-v1"
    )
    assert normalized_record.normalization_metadata.source_region == "all-czechia"
    assert normalized_record.normalization_metadata.source_listing_page_number == 3
    assert normalized_record.normalization_metadata.source_scrape_run_id == (
        "dc733c67-1091-4a08-831f-f8243eb1b8f6"
    )
    assert normalized_record.normalization_metadata.source_captured_from == "detail_page"
    assert normalized_record.normalization_metadata.source_http_status == 200


def test_normalizer_keeps_missing_optional_typed_values_explicit_for_real_snapshot() -> None:
    """Keep missing optional fields explicit when a stored snapshot omits them."""

    raw_record = _load_raw_record_from_snapshot(
        "data/raw/all-czechia/1118982988/2026-03-18T08-56-19.555927+00-00.json",
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.core_attributes.price.amount_text == "6750000Kč"
    assert normalized_record.core_attributes.price.amount_czk == 6_750_000
    assert normalized_record.core_attributes.price.currency_code == "CZK"
    assert normalized_record.core_attributes.price.pricing_mode == "fixed_amount"
    assert normalized_record.core_attributes.price.note is None
    assert normalized_record.core_attributes.building.material == "Panelová"
    assert normalized_record.core_attributes.building.structural_attributes == (
        "Jednopodlažní",
    )
    assert normalized_record.core_attributes.building.physical_condition == (
        "Ve velmi dobrém stavu"
    )
    assert normalized_record.core_attributes.building.floor_position == 4
    assert normalized_record.core_attributes.building.total_floor_count == 5
    assert normalized_record.core_attributes.building.underground_floor_count is None
    assert normalized_record.core_attributes.building.unparsed_fragments == ()
    assert normalized_record.area_details.source_text == (
        "Užitná plocha 56 m², Celková plocha 58 m²"
    )
    assert normalized_record.area_details.usable_area_sqm == 56.0
    assert normalized_record.area_details.total_area_sqm == 58.0
    assert normalized_record.area_details.built_up_area_sqm is None
    assert normalized_record.area_details.garden_area_sqm is None
    assert normalized_record.area_details.unparsed_fragments == ()
    assert normalized_record.energy_details.source_text == "Mimořádně nehospodárná"
    assert normalized_record.energy_details.efficiency_class == "Mimořádně nehospodárná"
    assert normalized_record.energy_details.regulation_reference is None
    assert normalized_record.energy_details.consumption_kwh_per_sqm_year is None
    assert normalized_record.energy_details.additional_descriptors == ()
    assert normalized_record.energy_details.unparsed_fragments == ()
    assert normalized_record.ownership.ownership_type == "Osobní"
    assert normalized_record.listing_lifecycle.listed_on == date(2026, 3, 11)
    assert normalized_record.listing_lifecycle.updated_on == date(2026, 3, 18)
    assert normalized_record.source_identifiers.source_listing_reference is None
    assert "ID zakázky:" not in normalized_record.core_attributes.source_specific_attributes
    assert normalized_record.location.location_text == "Brno - Židenice"
    assert normalized_record.location.location_text_source == "title_fallback"
    assert normalized_record.location.city == "Brno"
    assert normalized_record.location.city_source == "title_fallback"
    assert normalized_record.location.city_district == "Židenice"
    assert normalized_record.location.city_district_source == "title_fallback"
    assert normalized_record.location.location_descriptor == (
        "Klidná část obce, Bydlení a kanceláře"
    )
    assert normalized_record.location.location_descriptor_source == (
        "source_payload:Lokalita:"
    )


def test_normalizer_parses_on_request_price_and_richer_building_energy_fields() -> None:
    """Parse deterministic typed fields from richer real-world price and energy strings."""

    raw_record = _load_raw_record_from_snapshot(
        "data/raw/all-czechia/297751372/2026-03-17T18-30-39.745363+00-00.json",
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.core_attributes.price.amount_text == "Cenanavyžádání"
    assert normalized_record.core_attributes.price.amount_czk is None
    assert normalized_record.core_attributes.price.currency_code is None
    assert normalized_record.core_attributes.price.pricing_mode == "on_request"
    assert normalized_record.core_attributes.building.source_text == (
        "Panelová, Ve velmi dobrém stavu, 1. podlaží z 8, Podzemní podlaží"
    )
    assert normalized_record.core_attributes.building.material == "Panelová"
    assert normalized_record.core_attributes.building.structural_attributes == ()
    assert normalized_record.core_attributes.building.physical_condition == (
        "Ve velmi dobrém stavu"
    )
    assert normalized_record.core_attributes.building.floor_position == 1
    assert normalized_record.core_attributes.building.total_floor_count == 8
    assert normalized_record.core_attributes.building.underground_floor_count == 1
    assert normalized_record.core_attributes.building.unparsed_fragments == ()
    assert normalized_record.energy_details.source_text == (
        "Úsporná, č. 264/2020 Sb., 99kWh/m² rok"
    )
    assert normalized_record.energy_details.efficiency_class == "Úsporná"
    assert normalized_record.energy_details.regulation_reference == "č. 264/2020 Sb."
    assert normalized_record.energy_details.consumption_kwh_per_sqm_year == 99.0
    assert normalized_record.energy_details.additional_descriptors == ()
    assert normalized_record.energy_details.unparsed_fragments == ()


def test_normalizer_parses_additional_building_and_energy_descriptors_from_real_snapshot() -> None:
    """Keep structured direct source descriptors that are neither floor counts nor amounts."""

    raw_record = _load_raw_record_from_snapshot(
        "data/raw/all-czechia/3218928460/2026-03-18T08-57-14.026076+00-00.json",
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.core_attributes.price.amount_czk == 65_055_620
    assert normalized_record.core_attributes.building.material == "Skeletová"
    assert normalized_record.core_attributes.building.structural_attributes == ()
    assert normalized_record.core_attributes.building.physical_condition == "Novostavba"
    assert normalized_record.core_attributes.building.floor_position == 7
    assert normalized_record.core_attributes.building.total_floor_count == 7
    assert normalized_record.core_attributes.building.underground_floor_count == 3
    assert normalized_record.energy_details.efficiency_class == "Velmi úsporná"
    assert normalized_record.energy_details.regulation_reference == "č. 264/2020 Sb."
    assert normalized_record.energy_details.consumption_kwh_per_sqm_year == 50.0
    assert normalized_record.energy_details.additional_descriptors == (
        "Nízkoenergetická budova",
    )
    assert normalized_record.energy_details.unparsed_fragments == ()


def test_normalizer_preserves_unparsed_area_fragments_for_traceability() -> None:
    """Keep partially parsed area text traceable when one fragment is unsupported."""

    raw_record = RawListingRecord(
        listing_id="partial-area-1",
        source_url="https://www.sreality.cz/detail/prodej/byt/praha/partial-area-1",
        captured_at_utc=datetime(2026, 3, 18, 12, 0, 0, tzinfo=timezone.utc),
        source_payload={
            "Název": "Prodej bytu 2+kk 70m²Praha 4 - Nusle",
            "Plocha:": "Užitná plocha 70 m², Lodžie dle prohlášení vlastníka",
            "Vlastnictví:": "Osobní",
            "Vloženo:": "18. 3. 2026",
            "Makléř:": {"jméno": "Example Broker"},
        },
        source_metadata=RawSourceMetadata(
            region="all-czechia",
            listing_page_number=1,
            scrape_run_id="run-partial-area",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.area_details.source_text == (
        "Užitná plocha 70 m², Lodžie dle prohlášení vlastníka"
    )
    assert normalized_record.area_details.usable_area_sqm == 70.0
    assert normalized_record.area_details.total_area_sqm is None
    assert normalized_record.area_details.built_up_area_sqm is None
    assert normalized_record.area_details.garden_area_sqm is None
    assert normalized_record.area_details.unparsed_fragments == (
        "Lodžie dle prohlášení vlastníka",
    )
    assert normalized_record.ownership.ownership_type == "Osobní"
    assert normalized_record.listing_lifecycle.listed_on == date(2026, 3, 18)
    assert normalized_record.listing_lifecycle.updated_on is None
    assert normalized_record.source_identifiers.source_listing_reference is None
    assert normalized_record.core_attributes.source_specific_attributes == {
        "Makléř:": {"jméno": "Example Broker"},
    }
    assert normalized_record.location.location_text == "Praha 4 - Nusle"
    assert normalized_record.location.location_text_source == "title_fallback"
    assert normalized_record.location.city == "Praha"
    assert normalized_record.location.city_source == "title_fallback"
    assert normalized_record.location.city_district == "Nusle"
    assert normalized_record.location.city_district_source == "title_fallback"
    assert normalized_record.location.location_descriptor is None
    assert normalized_record.location.location_descriptor_source is None


def test_normalizer_preserves_partially_parseable_building_and_energy_fragments() -> None:
    """Preserve direct source fragments that the building or energy parser cannot map."""

    raw_record = RawListingRecord(
        listing_id="partial-building-energy-1",
        source_url=(
            "https://www.sreality.cz/detail/prodej/byt/praha/partial-building-energy-1"
        ),
        captured_at_utc=datetime(2026, 3, 18, 12, 0, 0, tzinfo=timezone.utc),
        source_payload={
            "Název": "Prodej bytu 2+kk 70m²Praha 4 - Nusle",
            "Celková cena:": "7 500 000 Kč",
            "Stavba:": (
                "Panelová, Loft, Před rekonstrukcí, 2. podlaží z 6, Střešní terasa"
            ),
            "Energetická náročnost:": (
                "Úsporná, č. 264/2020 Sb., 99kWh/m² rok, Mimo standard"
            ),
            "Vloženo:": "18. 3. 2026",
        },
        source_metadata=RawSourceMetadata(
            region="all-czechia",
            listing_page_number=1,
            scrape_run_id="run-partial-building-energy",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.core_attributes.building.material == "Panelová"
    assert normalized_record.core_attributes.building.structural_attributes == ()
    assert normalized_record.core_attributes.building.physical_condition == (
        "Před rekonstrukcí"
    )
    assert normalized_record.core_attributes.building.floor_position == 2
    assert normalized_record.core_attributes.building.total_floor_count == 6
    assert normalized_record.core_attributes.building.underground_floor_count is None
    assert normalized_record.core_attributes.building.unparsed_fragments == (
        "Loft",
        "Střešní terasa",
    )
    assert normalized_record.energy_details.efficiency_class == "Úsporná"
    assert normalized_record.energy_details.regulation_reference == "č. 264/2020 Sb."
    assert normalized_record.energy_details.consumption_kwh_per_sqm_year == 99.0
    assert normalized_record.energy_details.additional_descriptors == (
        "Mimo standard",
    )
    assert normalized_record.energy_details.unparsed_fragments == ()


def test_normalizer_keeps_malformed_supported_nearby_places_traceable() -> None:
    """Emit partial nearby-place entries for supported keys with malformed text."""

    raw_record = RawListingRecord(
        listing_id="partial-nearby-places-1",
        source_url=(
            "https://www.sreality.cz/detail/prodej/byt/praha/partial-nearby-places-1"
        ),
        captured_at_utc=datetime(2026, 3, 18, 12, 0, 0, tzinfo=timezone.utc),
        source_payload={
            "Název": "Prodej bytu 2+kk 70m²Praha 4 - Nusle",
            "Bus MHD:": "Náměstí Bratří Synků",
            "Metro:": "Vyšehrad(1200 m)",
            "Makléř:": {"jméno": "Example Broker"},
        },
        source_metadata=RawSourceMetadata(
            region="all-czechia",
            listing_page_number=1,
            scrape_run_id="run-partial-nearby-places",
            http_status=200,
            parser_version="sreality-detail-v1",
            captured_from="detail_page",
        ),
        raw_page_snapshot=None,
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    nearby_places_by_source_key = {
        place.source_key: place for place in normalized_record.location.nearby_places
    }
    assert nearby_places_by_source_key["Bus MHD:"].category == "bus_mhd"
    assert nearby_places_by_source_key["Bus MHD:"].source_text == (
        "Náměstí Bratří Synků"
    )
    assert nearby_places_by_source_key["Bus MHD:"].name is None
    assert nearby_places_by_source_key["Bus MHD:"].distance_m is None
    assert nearby_places_by_source_key["Metro:"].category == "metro"
    assert nearby_places_by_source_key["Metro:"].source_text == "Vyšehrad(1200 m)"
    assert nearby_places_by_source_key["Metro:"].name == "Vyšehrad"
    assert nearby_places_by_source_key["Metro:"].distance_m == 1200
    assert normalized_record.core_attributes.source_specific_attributes == {
        "Makléř:": {"jméno": "Example Broker"},
    }


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


def test_normalizer_parses_prague_street_title_fallback_from_real_snapshot() -> None:
    """Parse Prague city and district from a representative street-prefixed title."""

    raw_record = _load_raw_record_from_snapshot(
        "data/raw/all-czechia/10208076/2026-03-18T08-57-03.691606+00-00.json",
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.location.location_text == "Praha - Staré Město"
    assert normalized_record.location.location_text_source == "title_fallback"
    assert normalized_record.location.city == "Praha"
    assert normalized_record.location.city_source == "title_fallback"
    assert normalized_record.location.city_district == "Staré Město"
    assert normalized_record.location.city_district_source == "title_fallback"
    assert normalized_record.location.location_descriptor == "Centrum obce"
    assert normalized_record.location.location_descriptor_source == (
        "source_payload:Lokalita:"
    )


def test_normalizer_parses_non_prague_dash_location_without_comma_from_real_snapshot() -> None:
    """Parse municipality and district from a dash-delimited title suffix."""

    raw_record = _load_raw_record_from_snapshot(
        "data/raw/all-czechia/3301245772/2026-03-18T08-57-05.223481+00-00.json",
    )
    normalizer = RawListingNormalizer()

    normalized_record = normalizer.normalize(raw_record)

    assert normalized_record.location.location_text == "Olomouc - Nové Sady"
    assert normalized_record.location.location_text_source == "title_fallback"
    assert normalized_record.location.city == "Olomouc"
    assert normalized_record.location.city_source == "title_fallback"
    assert normalized_record.location.city_district == "Nové Sady"
    assert normalized_record.location.city_district_source == "title_fallback"
    assert normalized_record.location.location_descriptor == "Sídliště"
    assert normalized_record.location.location_descriptor_source == (
        "source_payload:Lokalita:"
    )
