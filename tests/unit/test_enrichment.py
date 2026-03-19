"""Tests for enrichment-stage contracts and deterministic derived features."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from datetime import datetime, timezone

import pytest

from scraperweb.enrichment import ENRICHMENT_VERSION, NormalizedListingEnricher
from scraperweb.normalization.models import (
    NormalizedAccessories,
    NormalizedAccessoryAreaFeature,
    NormalizedAreaDetails,
    NormalizedEnergyDetails,
    NormalizationMetadata,
    NormalizedBuilding,
    NormalizedCoreAttributes,
    NormalizedListingLifecycle,
    NormalizedListingRecord,
    NormalizedLocation,
    NormalizedNearbyPlace,
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
        building_material="Cihla",
        physical_condition="Novostavba",
        floor_position=7,
        total_floor_count=7,
        accessories=NormalizedAccessories(
            has_elevator=True,
            is_barrier_free=True,
            furnishing_state="partially_furnished",
            balcony=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=4.0),
            loggia=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=3.5),
            terrace=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=8.0),
            cellar=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=2.0),
        ),
        nearby_places=(
            NormalizedNearbyPlace(
                category="bus_mhd",
                source_key="Bus MHD:",
                source_text="Invalid bus stop",
                name="Florenc",
                distance_m=130,
            ),
            NormalizedNearbyPlace(
                category="metro",
                source_key="Metro:",
                source_text="Křižíkova (450 m)",
                name="Křižíkova",
                distance_m=450,
            ),
            NormalizedNearbyPlace(
                category="tram",
                source_key="Tram:",
                source_text="Karlínské náměstí (210 m)",
                name="Karlínské náměstí",
                distance_m=210,
            ),
            NormalizedNearbyPlace(
                category="vlak",
                source_key="Vlak:",
                source_text="Praha hlavní nádraží (1900 m)",
                name="Praha hlavní nádraží",
                distance_m=1900,
            ),
            NormalizedNearbyPlace(
                category="obchod",
                source_key="Obchod:",
                source_text="Billa (320 m)",
                name="Billa",
                distance_m=320,
            ),
            NormalizedNearbyPlace(
                category="vecerka",
                source_key="Večerka:",
                source_text="Večerka Karlín (180 m)",
                name="Večerka Karlín",
                distance_m=180,
            ),
            NormalizedNearbyPlace(
                category="skola",
                source_key="Škola:",
                source_text="ZŠ Lyčkovo náměstí (650 m)",
                name="ZŠ Lyčkovo náměstí",
                distance_m=650,
            ),
            NormalizedNearbyPlace(
                category="skolka",
                source_key="Školka:",
                source_text="MŠ Pernerova (290 m)",
                name="MŠ Pernerova",
                distance_m=290,
            ),
            NormalizedNearbyPlace(
                category="bankomat",
                source_key="Bankomat:",
                source_text="ČSOB (90 m)",
                name="ČSOB",
                distance_m=90,
            ),
        ),
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
    assert enriched_record.property_features.is_ground_floor is False
    assert enriched_record.property_features.is_upper_floor is True
    assert enriched_record.property_features.relative_floor_position == "top"
    assert enriched_record.property_features.is_top_floor is True
    assert enriched_record.property_features.is_new_build is True
    assert enriched_record.property_features.building_material_bucket == "masonry"
    assert enriched_record.property_features.building_condition_bucket == "new_build"
    assert enriched_record.property_features.energy_efficiency_bucket == "efficient"
    assert enriched_record.property_features.has_energy_efficiency_rating is True
    assert enriched_record.property_features.has_balcony is True
    assert enriched_record.property_features.has_loggia is True
    assert enriched_record.property_features.has_terrace is True
    assert enriched_record.property_features.has_cellar is True
    assert enriched_record.property_features.has_elevator is True
    assert enriched_record.property_features.is_barrier_free is True
    assert enriched_record.property_features.outdoor_accessory_area_sqm == 15.5
    assert enriched_record.property_features.furnishing_bucket == (
        "partially_furnished"
    )
    assert enriched_record.property_features.has_city_district is True
    assert enriched_record.property_features.is_prague_listing is True
    assert enriched_record.location_features.street is None
    assert enriched_record.location_features.street_source is None
    assert enriched_record.location_features.latitude == 50.106109
    assert enriched_record.location_features.longitude == 14.474073
    assert enriched_record.location_features.location_precision == "district"
    assert enriched_record.location_features.geocoding_source == "prague_district_reference"
    assert enriched_record.location_features.geocoding_confidence == "medium"
    assert enriched_record.location_features.geocoding_match_strategy == (
        "district_override"
    )
    assert enriched_record.location_features.geocoding_query_text == "Praha 8, Karlín"
    assert enriched_record.location_features.geocoding_query_text_source == (
        "title_fallback"
    )
    assert enriched_record.location_features.resolved_address_text == "Praha 8, Karlín"
    assert enriched_record.location_features.resolved_street is None
    assert enriched_record.location_features.resolved_house_number is None
    assert enriched_record.location_features.resolved_city_district == "Praha 8"
    assert enriched_record.location_features.resolved_municipality_name == "Praha"
    assert enriched_record.location_features.resolved_municipality_code == "554782"
    assert enriched_record.location_features.resolved_region_code == "CZ010"
    assert enriched_record.location_features.geocoding_fallback_level == "district"
    assert enriched_record.location_features.geocoding_is_fallback is True
    assert enriched_record.location_features.municipality_name == "Praha"
    assert enriched_record.location_features.municipality_code == "554782"
    assert enriched_record.location_features.district_code == "CZ0100"
    assert enriched_record.location_features.region_code == "CZ010"
    assert enriched_record.location_features.municipality_latitude == 50.075638
    assert enriched_record.location_features.municipality_longitude == 14.4379
    assert enriched_record.location_features.distance_to_okresni_mesto_km == 0.0
    assert enriched_record.location_features.distance_to_orp_center_km == 0.0
    assert enriched_record.location_features.metropolitan_area == "Praha"
    assert enriched_record.location_features.metropolitan_district == "Praha 8"
    assert enriched_record.location_features.spatial_cell_id == "praha-cell-5010-1447"
    assert enriched_record.location_features.distance_to_prague_center_km == 4.338
    assert enriched_record.location_features.is_district_city is True
    assert enriched_record.location_features.is_orp_center is True
    assert enriched_record.location_features.orp_code == "1000"
    assert enriched_record.location_features.city_district_normalized == "Praha 8"
    assert enriched_record.location_features.municipality_match_status == "matched"
    assert enriched_record.location_features.municipality_match_method == (
        "city_prague_numbered"
    )
    assert enriched_record.location_features.municipality_match_input == "Praha 8"
    assert enriched_record.location_features.nearest_public_transport_m == 130
    assert enriched_record.location_features.nearest_metro_m == 450
    assert enriched_record.location_features.nearest_tram_m == 210
    assert enriched_record.location_features.nearest_bus_m == 130
    assert enriched_record.location_features.nearest_train_m == 1900
    assert enriched_record.location_features.nearest_shop_m == 180
    assert enriched_record.location_features.nearest_school_m == 650
    assert enriched_record.location_features.nearest_kindergarten_m == 290
    assert enriched_record.location_features.amenities_within_300m_count == 5
    assert enriched_record.location_features.amenities_within_1000m_count == 8
    assert enriched_record.lifecycle_features.listing_age_days == 6
    assert enriched_record.lifecycle_features.updated_recency_days == 1
    assert enriched_record.lifecycle_features.is_fresh_listing_7d is True
    assert enriched_record.lifecycle_features.is_recently_updated_3d is True
    assert enriched_record.enrichment_metadata is not None
    assert enriched_record.enrichment_metadata.enriched_at_utc == (
        normalized_record.normalized_at_utc
    )
    assert enriched_record.enrichment_metadata.source_normalization_version == (
        normalized_record.normalization_version
    )
    assert len(enriched_record.enrichment_metadata.derivation_notes) == 23


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
        building_material="Cihla",
        physical_condition=None,
        floor_position=None,
        total_floor_count=None,
        accessories=NormalizedAccessories(),
        listed_on=None,
        updated_on=None,
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
    assert first_record.property_features.is_ground_floor is None
    assert first_record.property_features.is_upper_floor is None
    assert first_record.property_features.relative_floor_position is None
    assert first_record.property_features.is_top_floor is None
    assert first_record.property_features.is_new_build is None
    assert first_record.property_features.building_material_bucket == "masonry"
    assert first_record.property_features.building_condition_bucket is None
    assert first_record.property_features.energy_efficiency_bucket is None
    assert first_record.property_features.has_energy_efficiency_rating is False
    assert first_record.property_features.has_balcony is None
    assert first_record.property_features.has_loggia is None
    assert first_record.property_features.has_terrace is None
    assert first_record.property_features.has_cellar is None
    assert first_record.property_features.has_elevator is None
    assert first_record.property_features.is_barrier_free is None
    assert first_record.property_features.outdoor_accessory_area_sqm is None
    assert first_record.property_features.furnishing_bucket is None
    assert first_record.property_features.has_city_district is False
    assert first_record.property_features.is_prague_listing is False
    assert first_record.location_features.latitude == 49.19516
    assert first_record.location_features.longitude == 16.606937
    assert first_record.location_features.location_precision == "municipality"
    assert first_record.location_features.geocoding_source == (
        "municipality_centroid_dataset"
    )
    assert first_record.location_features.geocoding_confidence == "medium"
    assert first_record.location_features.geocoding_match_strategy == (
        "municipality_centroid"
    )
    assert first_record.location_features.geocoding_query_text == "Brno"
    assert first_record.location_features.geocoding_query_text_source == "title_fallback"
    assert first_record.location_features.resolved_address_text == "Brno"
    assert first_record.location_features.geocoding_fallback_level == "municipality"
    assert first_record.location_features.geocoding_is_fallback is True
    assert first_record.location_features.municipality_name == "Brno"
    assert first_record.location_features.municipality_code == "582786"
    assert first_record.location_features.district_code == "CZ0642"
    assert first_record.location_features.region_code == "CZ064"
    assert first_record.location_features.municipality_latitude == 49.19516
    assert first_record.location_features.municipality_longitude == 16.606937
    assert first_record.location_features.distance_to_okresni_mesto_km == 0.0
    assert first_record.location_features.distance_to_orp_center_km == 0.0
    assert first_record.location_features.metropolitan_area is None
    assert first_record.location_features.metropolitan_district is None
    assert first_record.location_features.spatial_cell_id is None
    assert first_record.location_features.distance_to_prague_center_km is None
    assert first_record.location_features.is_district_city is True
    assert first_record.location_features.is_orp_center is True
    assert first_record.location_features.city_district_normalized is None
    assert first_record.location_features.municipality_match_status == "matched"
    assert first_record.location_features.municipality_match_method == "city"
    assert first_record.location_features.nearest_public_transport_m is None
    assert first_record.location_features.nearest_metro_m is None
    assert first_record.location_features.nearest_tram_m is None
    assert first_record.location_features.nearest_bus_m is None
    assert first_record.location_features.nearest_train_m is None
    assert first_record.location_features.nearest_shop_m is None
    assert first_record.location_features.nearest_school_m is None
    assert first_record.location_features.nearest_kindergarten_m is None
    assert first_record.location_features.amenities_within_300m_count == 0
    assert first_record.location_features.amenities_within_1000m_count == 0
    assert first_record.lifecycle_features.listing_age_days is None
    assert first_record.lifecycle_features.updated_recency_days is None
    assert first_record.lifecycle_features.is_fresh_listing_7d is None
    assert first_record.lifecycle_features.is_recently_updated_3d is None


def test_enricher_propagates_structured_street_fields_from_normalization() -> None:
    """Expose normalized street facts in enrichment without deriving new address guesses."""

    normalized_record = _build_normalized_record(
        title="Prodej bytu 3+kk 82m²Dlouhá, Praha - Staré Město",
        amount_text="12 500 000 Kč",
        price_note=None,
        energy_efficiency_class="Úsporná",
        city="Praha",
        city_district="Staré Město",
        usable_area_sqm=82.0,
        total_area_sqm=None,
        building_material="Cihlová",
        physical_condition="Ve velmi dobrém stavu",
        floor_position=3,
        total_floor_count=5,
    )
    normalized_record = replace(
        normalized_record,
        location=replace(
            normalized_record.location,
            location_text="Praha - Staré Město",
            location_text_source="title_fallback",
            street="Dlouhá",
            street_source="title_fallback",
            city="Praha",
            city_source="title_fallback",
            city_district="Staré Město",
            city_district_source="title_fallback",
        ),
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.street == "Dlouhá"
    assert enriched_record.location_features.street_source == "title_fallback"


def test_enricher_resolves_exact_address_geocoding_from_structured_inputs() -> None:
    """Prefer address precision when house number and municipality are available."""

    normalized_record = _build_normalized_record(
        title="Prodej bytu 3+1 77m²Cihlářská 12, Blansko",
        amount_text="6 400 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Blansko",
        city_district=None,
        usable_area_sqm=77.0,
        total_area_sqm=None,
        building_material="Cihla",
        physical_condition=None,
        floor_position=2,
        total_floor_count=5,
        street="Cihlářská",
        house_number="12",
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.location_precision == "address"
    assert enriched_record.location_features.geocoding_confidence == "high"
    assert enriched_record.location_features.geocoding_match_strategy == "address_exact"
    assert enriched_record.location_features.geocoding_source == (
        "deterministic_query_projection"
    )
    assert enriched_record.location_features.geocoding_is_fallback is False
    assert enriched_record.location_features.geocoding_fallback_level == "none"
    assert enriched_record.location_features.geocoding_query_text == (
        "Cihlářská 12, Blansko"
    )
    assert enriched_record.location_features.resolved_address_text == (
        "Cihlářská 12, Blansko"
    )
    assert enriched_record.location_features.resolved_street == "Cihlářská"
    assert enriched_record.location_features.resolved_house_number == "12"
    assert enriched_record.location_features.latitude is not None
    assert enriched_record.location_features.longitude is not None


def test_enricher_resolves_street_fallback_when_house_number_is_missing() -> None:
    """Keep street-level precision explicit when only street text is available."""

    normalized_record = _build_normalized_record(
        title="Prodej bytu 3+1 77m²Cihlářská, Blansko",
        amount_text="6 400 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Blansko",
        city_district=None,
        usable_area_sqm=77.0,
        total_area_sqm=None,
        building_material="Cihla",
        physical_condition=None,
        floor_position=2,
        total_floor_count=5,
        street="Cihlářská",
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.location_precision == "street"
    assert enriched_record.location_features.geocoding_confidence == "medium"
    assert enriched_record.location_features.geocoding_match_strategy == "street_centroid"
    assert enriched_record.location_features.geocoding_source == (
        "deterministic_query_projection"
    )
    assert enriched_record.location_features.geocoding_is_fallback is True
    assert enriched_record.location_features.geocoding_fallback_level == "street"
    assert enriched_record.location_features.geocoding_query_text == "Cihlářská, Blansko"
    assert enriched_record.location_features.resolved_house_number is None
    assert enriched_record.location_features.latitude is not None
    assert enriched_record.location_features.longitude is not None


def test_enricher_keeps_unresolved_geocoding_explicit_without_coordinates() -> None:
    """Represent unresolved geocoding as an explicit no-coordinate outcome."""

    normalized_record = _build_normalized_record(
        title="Byt 1+kk",
        amount_text=None,
        price_note=None,
        energy_efficiency_class=None,
        city=None,
        city_district=None,
        usable_area_sqm=None,
        total_area_sqm=None,
        building_material="Cihla",
        physical_condition=None,
        floor_position=None,
        total_floor_count=None,
    )
    normalized_record = replace(
        normalized_record,
        location=replace(
            normalized_record.location,
            geocoding_query_text="Unknown district",
            geocoding_query_text_source="manual_fixture",
        ),
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.latitude is None
    assert enriched_record.location_features.longitude is None
    assert enriched_record.location_features.location_precision == "unresolved"
    assert enriched_record.location_features.geocoding_confidence == "none"
    assert enriched_record.location_features.geocoding_source is None
    assert enriched_record.location_features.geocoding_match_strategy is None
    assert enriched_record.location_features.geocoding_query_text == "Unknown district"
    assert enriched_record.location_features.geocoding_query_text_source == (
        "manual_fixture"
    )
    assert enriched_record.location_features.geocoding_fallback_level == "unresolved"
    assert enriched_record.location_features.geocoding_is_fallback is None


def test_enricher_keeps_inconsistent_lifecycle_dates_optional() -> None:
    """Keep lifecycle features empty when normalized dates are logically inconsistent."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Brno",
        amount_text="6 100 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Brno",
        city_district=None,
        usable_area_sqm=58.0,
        total_area_sqm=60.0,
        building_material="Cihla",
        physical_condition=None,
        floor_position=3,
        total_floor_count=6,
        listed_on=date(2026, 3, 16),
        updated_on=date(2026, 3, 15),
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.lifecycle_features.listing_age_days is None
    assert enriched_record.lifecycle_features.updated_recency_days is None
    assert enriched_record.lifecycle_features.is_fresh_listing_7d is None
    assert enriched_record.lifecycle_features.is_recently_updated_3d is None


def test_enricher_keeps_future_lifecycle_dates_optional() -> None:
    """Ignore normalized lifecycle dates that would create negative elapsed durations."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Brno",
        amount_text="6 100 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Brno",
        city_district=None,
        usable_area_sqm=58.0,
        total_area_sqm=60.0,
        building_material="Cihla",
        physical_condition=None,
        floor_position=3,
        total_floor_count=6,
        listed_on=date(2026, 3, 18),
        updated_on=date(2026, 3, 20),
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.lifecycle_features.listing_age_days is None
    assert enriched_record.lifecycle_features.updated_recency_days is None
    assert enriched_record.lifecycle_features.is_fresh_listing_7d is None
    assert enriched_record.lifecycle_features.is_recently_updated_3d is None


def test_enricher_derives_nearby_place_accessibility_for_partial_non_prague_data() -> None:
    """Derive stable nearby-place features while ignoring malformed distance values."""

    normalized_record = _build_normalized_record(
        title="Byt 3+kk, Adamov - Blansko",
        amount_text="6 700 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Adamov",
        city_district="Blansko",
        usable_area_sqm=73.0,
        total_area_sqm=78.0,
        building_material="Cihla",
        physical_condition=None,
        floor_position=2,
        total_floor_count=4,
        nearby_places=(
            NormalizedNearbyPlace(
                category="bus_mhd",
                source_key="Bus MHD:",
                source_text="Náměstí práce",
                name=None,
                distance_m=None,
            ),
            NormalizedNearbyPlace(
                category="metro",
                source_key="Metro:",
                source_text="Vyšehrad",
                name="Vyšehrad",
                distance_m=None,
            ),
            NormalizedNearbyPlace(
                category="tram",
                source_key="Tram:",
                source_text="Blansko centrum",
                name="Blansko centrum",
                distance_m=None,
            ),
            NormalizedNearbyPlace(
                category="vlak",
                source_key="Vlak:",
                source_text="Adamov zastávka (780 m)",
                name="Adamov zastávka",
                distance_m=780,
            ),
            NormalizedNearbyPlace(
                category="vecerka",
                source_key="Večerka:",
                source_text="Potraviny (220 m)",
                name="Potraviny",
                distance_m=220,
            ),
            NormalizedNearbyPlace(
                category="skola",
                source_key="Škola:",
                source_text="ZŠ Ronovská",
                name="ZŠ Ronovská",
                distance_m=None,
            ),
            NormalizedNearbyPlace(
                category="skolka",
                source_key="Školka:",
                source_text="MŠ Jilemnického (410 m)",
                name="MŠ Jilemnického",
                distance_m=410,
            ),
        ),
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.municipality_name == "Adamov"
    assert enriched_record.location_features.nearest_public_transport_m == 780
    assert enriched_record.location_features.nearest_metro_m is None
    assert enriched_record.location_features.nearest_tram_m is None
    assert enriched_record.location_features.nearest_bus_m is None
    assert enriched_record.location_features.nearest_train_m == 780
    assert enriched_record.location_features.nearest_shop_m == 220
    assert enriched_record.location_features.nearest_school_m is None
    assert enriched_record.location_features.nearest_kindergarten_m == 410
    assert enriched_record.location_features.amenities_within_300m_count == 1
    assert enriched_record.location_features.amenities_within_1000m_count == 3


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
        building_material="Panelová",
        physical_condition="Před rekonstrukcí",
        floor_position=3,
        total_floor_count=5,
    )
    enricher = NormalizedListingEnricher()

    enriched_record = enricher.enrich(normalized_record)

    assert enriched_record.price_features.asking_price_czk == 11_340_000
    assert enriched_record.price_features.price_per_square_meter_czk == 140_000.0
    assert enriched_record.property_features.is_ground_floor is False
    assert enriched_record.property_features.is_upper_floor is True
    assert enriched_record.property_features.relative_floor_position == "middle"
    assert enriched_record.property_features.is_top_floor is False
    assert enriched_record.property_features.is_new_build is False
    assert enriched_record.property_features.building_material_bucket == "panel"
    assert enriched_record.property_features.building_condition_bucket == "needs_work"
    assert enriched_record.property_features.energy_efficiency_bucket == "average"
    assert enriched_record.property_features.has_energy_efficiency_rating is True


def test_enricher_derives_accessory_and_outdoor_features_from_normalized_accessories() -> None:
    """Expose explicit accessory booleans and aggregated outdoor area."""

    normalized_record = _build_normalized_record(
        title="Byt 4+kk, Brno - Veveří",
        amount_text="15 000 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Brno",
        city_district="Veveří",
        usable_area_sqm=110.0,
        total_area_sqm=125.0,
        building_material="Cihla",
        physical_condition=None,
        floor_position=5,
        total_floor_count=6,
        accessories=NormalizedAccessories(
            has_elevator=False,
            is_barrier_free=False,
            furnishing_state="furnished",
            balcony=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=6.0),
            loggia=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=4.5),
            terrace=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=12.0),
            cellar=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=3.0),
        ),
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.property_features.has_balcony is True
    assert enriched_record.property_features.has_loggia is True
    assert enriched_record.property_features.has_terrace is True
    assert enriched_record.property_features.has_cellar is True
    assert enriched_record.property_features.has_elevator is False
    assert enriched_record.property_features.is_barrier_free is False
    assert enriched_record.property_features.outdoor_accessory_area_sqm == 22.5
    assert enriched_record.property_features.furnishing_bucket == "furnished"


def test_enricher_keeps_absent_or_unmeasured_accessory_values_explicit() -> None:
    """Preserve optionality when accessory presence or measured areas are missing."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Olomouc",
        amount_text="5 800 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Olomouc",
        city_district=None,
        usable_area_sqm=54.0,
        total_area_sqm=60.0,
        building_material="Cihla",
        physical_condition=None,
        floor_position=2,
        total_floor_count=5,
        accessories=NormalizedAccessories(
            has_elevator=None,
            is_barrier_free=None,
            furnishing_state=None,
            balcony=NormalizedAccessoryAreaFeature(is_present=None, area_sqm=None),
            loggia=NormalizedAccessoryAreaFeature(is_present=False, area_sqm=None),
            terrace=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=None),
            cellar=NormalizedAccessoryAreaFeature(is_present=False, area_sqm=None),
        ),
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.property_features.has_balcony is None
    assert enriched_record.property_features.has_loggia is False
    assert enriched_record.property_features.has_terrace is True
    assert enriched_record.property_features.has_cellar is False
    assert enriched_record.property_features.has_elevator is None
    assert enriched_record.property_features.is_barrier_free is None
    assert enriched_record.property_features.outdoor_accessory_area_sqm is None
    assert enriched_record.property_features.furnishing_bucket is None


def test_enricher_ignores_ambiguous_source_specific_accessory_fragments() -> None:
    """Keep enrichment bound to normalized accessories instead of raw fallback fragments."""

    normalized_record = _build_normalized_record(
        title="Byt 3+1, Ostrava - Poruba",
        amount_text="6 400 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Ostrava",
        city_district="Poruba",
        usable_area_sqm=78.0,
        total_area_sqm=82.0,
        building_material="Panelová",
        physical_condition=None,
        floor_position=6,
        total_floor_count=8,
        accessories=NormalizedAccessories(
            has_elevator=True,
            furnishing_state="unfurnished",
            balcony=NormalizedAccessoryAreaFeature(is_present=True, area_sqm=5.0),
            unparsed_fragments=("2 garáže",),
        ),
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.property_features.has_balcony is True
    assert enriched_record.property_features.has_loggia is None
    assert enriched_record.property_features.has_terrace is None
    assert enriched_record.property_features.has_cellar is None
    assert enriched_record.property_features.has_elevator is True
    assert enriched_record.property_features.is_barrier_free is None
    assert enriched_record.property_features.outdoor_accessory_area_sqm == 5.0
    assert enriched_record.property_features.furnishing_bucket == "unfurnished"


def test_enricher_derives_ground_floor_and_low_rise_building_buckets() -> None:
    """Derive conservative low-rise semantics when building values are explicit."""

    normalized_record = _build_normalized_record(
        title="Byt 1+kk, Pardubice - Centrum",
        amount_text="3 950 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Pardubice",
        city_district="Centrum",
        usable_area_sqm=39.0,
        total_area_sqm=None,
        building_material="Skeletová",
        physical_condition="Ve výstavbě",
        floor_position=0,
        total_floor_count=3,
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.property_features.is_ground_floor is True
    assert enriched_record.property_features.is_upper_floor is False
    assert enriched_record.property_features.relative_floor_position == "ground"
    assert enriched_record.property_features.is_top_floor is False
    assert enriched_record.property_features.is_new_build is False
    assert enriched_record.property_features.building_material_bucket == "skeleton"
    assert enriched_record.property_features.building_condition_bucket == "new_build"


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
        building_material="Cihla",
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
        building_material="Cihla",
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
        building_material="Cihla",
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


def test_enricher_maps_prague_named_districts_into_metropolitan_features() -> None:
    """Resolve supported Prague named districts into district and spatial features."""

    normalized_record = _build_normalized_record(
        title="Byt 2+kk, Praha - Nusle",
        amount_text="7 250 000 Kč",
        price_note=None,
        energy_efficiency_class=None,
        city="Praha",
        city_district="Nusle",
        usable_area_sqm=54.0,
        total_area_sqm=57.0,
        building_material="Cihla",
        physical_condition=None,
        floor_position=3,
        total_floor_count=6,
    )

    enriched_record = NormalizedListingEnricher().enrich(normalized_record)

    assert enriched_record.location_features.municipality_name == "Praha"
    assert enriched_record.location_features.city_district_normalized == "Nusle"
    assert enriched_record.location_features.metropolitan_area == "Praha"
    assert enriched_record.location_features.metropolitan_district == "Praha 4"
    assert enriched_record.location_features.spatial_cell_id == "praha-cell-5005-1443"
    assert enriched_record.location_features.distance_to_prague_center_km == 3.753


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
        building_material="Cihla",
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
        building_material="Cihla",
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
        building_material="Cihla",
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
    building_material: str | None,
    physical_condition: str | None,
    floor_position: int | None,
    total_floor_count: int | None,
    street: str | None = None,
    house_number: str | None = None,
    accessories: NormalizedAccessories | None = None,
    nearby_places: tuple[NormalizedNearbyPlace, ...] = (),
    listed_on: date | None = date(2026, 3, 11),
    updated_on: date | None = date(2026, 3, 16),
) -> NormalizedListingRecord:
    """Build a normalized record fixture for enrichment tests."""

    location_text = (
        f"{city} - {city_district}"
        if city is not None and city_district is not None
        else city
    )
    address_text = _build_address_text(
        street=street,
        house_number=house_number,
        city=city,
        city_district=city_district,
    )
    geocoding_query_text = address_text or street or location_text

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
                material=building_material,
                physical_condition=physical_condition,
                floor_position=floor_position,
                total_floor_count=total_floor_count,
            ),
            accessories=accessories or NormalizedAccessories(),
            source_specific_attributes={
                "Vybavení:": ["Sklep", "Balkon"],
                "Příslušenství:": ["2 garáže", "Terasa o ploše 99 m²"],
            },
        ),
        location=NormalizedLocation(
            location_text=location_text,
            location_text_source="title_fallback" if location_text is not None else None,
            street=street,
            street_source="title_fallback" if street is not None else None,
            house_number=house_number,
            house_number_source="title_fallback" if house_number is not None else None,
            address_text=address_text,
            address_text_source="title_fallback" if address_text is not None else None,
            city=city,
            city_source="title_fallback" if city is not None else None,
            city_district=city_district,
            city_district_source="title_fallback" if city_district is not None else None,
            geocoding_query_text=geocoding_query_text,
            geocoding_query_text_source=(
                "title_fallback" if geocoding_query_text is not None else None
            ),
            nearby_places=nearby_places,
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
        listing_lifecycle=NormalizedListingLifecycle(
            listed_on=listed_on,
            listed_on_text=listed_on.isoformat() if listed_on is not None else None,
            updated_on=updated_on,
            updated_on_text=updated_on.isoformat() if updated_on is not None else None,
        ),
    )


def _parse_amount_czk(amount_text: str | None) -> int | None:
    """Convert one normalized fixed-price fixture string into an integer amount."""

    if amount_text is None:
        return None
    return int(amount_text.replace(" Kč", "").replace(" ", ""))


def _build_address_text(
    *,
    street: str | None,
    house_number: str | None,
    city: str | None,
    city_district: str | None,
) -> str | None:
    """Build one fixture address string from normalized location parts."""

    parts: list[str] = []
    if street is not None:
        if house_number is not None:
            parts.append(f"{street} {house_number}")
        else:
            parts.append(street)
    if city is not None:
        parts.append(city)
    if city_district is not None:
        parts.append(city_district)
    if not parts:
        return None
    return ", ".join(parts)
