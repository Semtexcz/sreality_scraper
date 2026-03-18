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
    assert normalized_record.core_attributes.price.note == (
        "Cena včetně provize a kompletního právního servisu"
    )
    assert normalized_record.core_attributes.building.material == "Cihlová"
    assert normalized_record.core_attributes.building.condition == (
        "Ve velmi dobrém stavu, 5. podlaží"
    )
    assert normalized_record.core_attributes.building.energy_efficiency_class == (
        "Mimořádně nehospodárná"
    )
    assert normalized_record.area_details.source_text == "Užitná plocha 77 m²"
    assert normalized_record.area_details.usable_area_sqm == 77.0
    assert normalized_record.area_details.total_area_sqm is None
    assert normalized_record.area_details.built_up_area_sqm is None
    assert normalized_record.area_details.garden_area_sqm is None
    assert normalized_record.area_details.unparsed_fragments == ()
    assert normalized_record.ownership.ownership_type == "Osobní"
    assert normalized_record.listing_lifecycle.listed_on == date(2026, 3, 16)
    assert normalized_record.listing_lifecycle.listed_on_text == "16. 3. 2026"
    assert normalized_record.listing_lifecycle.updated_on == date(2026, 3, 18)
    assert normalized_record.listing_lifecycle.updated_on_text == "18. 3. 2026"
    assert normalized_record.source_identifiers.source_listing_reference == "00183"
    for mapped_key in (
        "ID zakázky:",
        "Plocha:",
        "Upraveno:",
        "Vlastnictví:",
        "Vloženo:",
    ):
        assert mapped_key not in normalized_record.core_attributes.source_specific_attributes
    assert normalized_record.core_attributes.source_specific_attributes == {
        "Bankomat:": "Bankomat ČSOB(856 m)",
        "Bus MHD:": "Blansko, Okružní(43 m)",
        "Cukrárna:": "Kavárna Cafisco(1061 m)",
        "Hospoda:": "Pivnice Sever(785 m)",
        "Hřiště:": "(167 m)",
        "Infrastruktura:": (
            "Vodovod:Vodovod, Plyn:Plynovod, Zdroj vytápění:Plynový kotel, "
            "Vytápěcí těleso:Radiátory, Kanalizace:Veřejná kanalizace, "
            "Telekomunikace:Internet, Kabelová televize, Kabelové rozvody, "
            "Doprava:Vlak, Silnice, MHD, Autobus, Komunikace:Asfaltová"
        ),
        "Kino:": "Kino Blansko(1741 m)",
        "Lokalita:": "Klidná část obce, Bydlení",
        "Lékař:": "MUDr. Eva Hlaváčová(666 m)",
        "Lékárna:": "Dr.Max Lékárna(858 m)",
        "Obchod:": "Kaufland(836 m)",
        "Pošta:": "Pošta Blansko 1 - Česká pošta, s.p.(2017 m)",
        "Příslušenství:": (
            "Bez výtahuNezařízenoBalkonSklep, Bez výtahu, Nezařízeno, Balkon, Sklep"
        ),
        "Restaurace:": "Starobrněnská pivnice VELVET(231 m)",
        "Sportoviště:": (
            "Sdružení rodičů a přátel dětí a školy při ZŠ Dvorská Blansko(928 m)"
        ),
        "Veterinář:": "MVDr. Ivana Stodůlková - veterinární ordinace(1036 m)",
        "Večerka:": "HRUŠKA(231 m)",
        "Vlak:": "Blansko město(1786 m)",
        "Zobrazeno:": "1410×",
        "Škola:": "Střední škola technická a gastronomická Blansko(702 m)",
        "Školka:": "MŠ Blansko, Dvorská 96(811 m)",
    }
    assert normalized_record.location.location_text == "Blansko"
    assert normalized_record.location.city == "Blansko"
    assert normalized_record.location.city_district is None
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

    assert normalized_record.area_details.source_text == (
        "Užitná plocha 56 m², Celková plocha 58 m²"
    )
    assert normalized_record.area_details.usable_area_sqm == 56.0
    assert normalized_record.area_details.total_area_sqm == 58.0
    assert normalized_record.area_details.built_up_area_sqm is None
    assert normalized_record.area_details.garden_area_sqm is None
    assert normalized_record.area_details.unparsed_fragments == ()
    assert normalized_record.ownership.ownership_type == "Osobní"
    assert normalized_record.listing_lifecycle.listed_on == date(2026, 3, 11)
    assert normalized_record.listing_lifecycle.updated_on == date(2026, 3, 18)
    assert normalized_record.source_identifiers.source_listing_reference is None
    assert "ID zakázky:" not in normalized_record.core_attributes.source_specific_attributes
    assert normalized_record.location.location_text == "Brno - Židenice"
    assert normalized_record.location.city == "Brno"
    assert normalized_record.location.city_district == "Židenice"


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
