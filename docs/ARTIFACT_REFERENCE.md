# Artifact Reference

This document is the canonical field-level reference for persisted `raw`,
`normalized`, and `enriched` JSON artifacts.

## Ownership Ladder

| Stage | Artifact family | Canonical owner | What the stage may store |
| --- | --- | --- | --- |
| Scraper | Raw | `scraperweb.scraper` | Direct source facts, fetch metadata, and optional replay-safe raw HTML snapshots |
| Normalization | Normalized | `scraperweb.normalization` | Stable typed fields reshaped from raw source facts, plus explicit source provenance and overflow preservation |
| Enrichment | Enriched | `scraperweb.enrichment` | Deterministic derived features computed from normalized records only |

Boundary rules:

- Raw artifacts must preserve source-shaped facts and capture metadata without
  silently normalizing or deriving downstream features.
- Normalized artifacts may restructure source facts into stable typed fields,
  but they must not introduce enrichment-owned joins, fallback-quality labels,
  or derived analytical features.
- Enriched artifacts own all deterministic joins, geocoding outcomes, spatial
  buckets, accessibility signals, and other derived features.

## Storage Layout And Lineage

| Family | Filesystem layout | Primary selector keys | Replay lineage |
| --- | --- | --- | --- |
| Raw | `data/raw/<region>/<listing_id>/<captured_at_utc>.json` | `region`, `listing_id`, `source_metadata.scrape_run_id` | Source of truth for later normalization replay |
| Normalized | `data/normalized/<region>/<listing_id>/<captured_at_utc>.json` | `normalization_metadata.source_region`, `listing_id`, `normalization_metadata.source_scrape_run_id` | Reuses raw `captured_at_utc`; records raw contract and parser lineage in `normalization_metadata` |
| Enriched | `data/enriched/<region>/<listing_id>/<captured_at_utc>.json` | `normalized_record.normalization_metadata.source_region`, `listing_id`, `normalized_record.normalization_metadata.source_scrape_run_id` | Reuses normalized `captured_at_utc`; embeds the full `normalized_record` plus explicit enrichment metadata |

Replay guarantees:

- The same persisted raw snapshot always maps to the same normalized path.
- The same persisted normalized snapshot always maps to the same enriched path.
- `captured_at_utc` is the stable per-listing snapshot timestamp reused across
  all three families.
- Region ownership is inherited forward from the raw capture and remains part
  of the filesystem path at each later stage.
- Raw markup-failure artifacts are separate diagnostics named
  `*.markup-failure.json`; they are not canonical raw listing records and are
  skipped by the normalization workflow.

## Raw Artifacts

### Stage Intent

Raw artifacts store scraper-owned source facts exactly once per captured
listing snapshot. The contract is intentionally permissive inside
`source_payload` so new source keys can be preserved without schema churn.

Current contract versions:

- `raw-listing-record-v1`: legacy raw artifacts without
  `source_payload.source_coordinates`
- `raw-listing-record-v2`: raw artifacts that include the structured
  `source_payload.source_coordinates` object

### Top-Level Fields

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `listing_id` | `string` | Yes | Scraper | Stable Sreality listing identifier used for storage grouping and lineage |
| `source_url` | `string` | Yes | Scraper | Detail-page URL used to capture the raw snapshot |
| `captured_at_utc` | ISO 8601 UTC datetime string | Yes | Scraper | Snapshot timestamp reused by later stages for deterministic artifact paths |
| `source_payload` | `object` | Yes | Scraper | Raw source-shaped detail-page facts preserved as JSON-safe key/value pairs |
| `source_metadata` | `object` | Yes | Scraper | Capture metadata describing where and how the raw snapshot was produced |
| `raw_page_snapshot` | `string` or `null` | Yes | Scraper | Optional captured detail HTML used for auditability and backward-compatible replay |

### `source_metadata`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `region` | `string` | Yes | Scraper | Region slug used for filesystem partitioning and downstream replay selectors |
| `listing_page_number` | `integer` | Yes | Scraper | Listing-page index where the detail URL was discovered |
| `scrape_run_id` | `string` | Yes | Scraper | Operator-visible identifier that groups snapshots produced in one collection run |
| `http_status` | `integer` | Yes | Scraper | Final detail-page HTTP status used for the accepted capture |
| `parser_version` | `string` | Yes | Scraper | Raw parser implementation version that produced `source_payload` |
| `captured_from` | `string` | Yes | Scraper | Capture origin label, currently `detail_page` for accepted raw listing records |

### `source_payload`

Known contract rules:

- All source-specific keys scraped from the detail page are preserved verbatim.
- Unknown source keys are allowed and must remain JSON-safe.
- Later stages may read source keys, but only normalization may reshape them
  into stable typed fields.

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `Název` | `string` | Usually | Scraper | Source listing title text preserved exactly as scraped |
| `ID zakázky:` | `string` | Optional | Scraper | Source-side listing reference used by normalization as a stable identifier input |
| `Celková cena:` | `string` | Optional | Scraper | Price text copied from the source detail payload |
| `Poznámka k ceně:` | `string` | Optional | Scraper | Source price note text |
| `Stavba:` | `string` | Optional | Scraper | Source building text used for later typed parsing |
| `Plocha:` | `string` | Optional | Scraper | Source area text used for later typed parsing |
| `Energetická náročnost:` | `string` | Optional | Scraper | Source energy text used for later typed parsing |
| `Příslušenství:` | `string` | Optional | Scraper | Source accessory text used for later typed parsing |
| `Vlastnictví:` | `string` | Optional | Scraper | Source ownership text |
| `Vloženo:` | `string` | Optional | Scraper | Source listing-created date text |
| `Upraveno:` | `string` | Optional | Scraper | Source listing-updated date text |
| `Lokalita:` | `string` | Optional | Scraper | Source location descriptor text |
| Nearby-place keys such as `Bus MHD:`, `Škola:`, `Vlak:` | `string` | Optional | Scraper | Source nearby-place facts later normalized into `location.nearby_places` when recognized |
| `source_coordinates` | `object` | Optional | Scraper | Structured source-backed coordinates captured from the embedded detail locality payload |
| Any other source key | JSON-safe primitive, array, or object | Optional | Scraper | Open-ended preservation of source facts not yet promoted into typed normalized fields |

### `source_payload.source_coordinates`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `latitude` | `number` | Yes when object exists | Scraper | Source-backed latitude captured from the detail locality payload |
| `longitude` | `number` | Yes when object exists | Scraper | Source-backed longitude captured from the detail locality payload |
| `source` | `string` | Yes when object exists | Scraper | Explicit provenance label for the coordinate source, currently `detail_locality_payload` |
| `precision` | `string` or `null` | No | Scraper | Optional source precision hint such as `listing` |

Raw coordinate boundary rules:

- Raw coordinates are direct source facts, not derived geocoding outputs.
- The raw coordinate object must not store inferred map-link coordinates,
  municipality centroids, or enrichment-owned confidence/fallback labels.
- When present, this object is the canonical raw coordinate source; legacy
  replay from `raw_page_snapshot` exists only for older raw artifacts that do
  not carry the structured field.

### Representative Example

```json
{
  "captured_at_utc": "2026-03-19T12:50:02.396345+00:00",
  "listing_id": "759501644",
  "raw_page_snapshot": null,
  "source_metadata": {
    "captured_from": "detail_page",
    "http_status": 200,
    "listing_page_number": 1,
    "parser_version": "sreality-detail-v1",
    "region": "all-czechia",
    "scrape_run_id": "0806cb77-7ba0-4cc9-9a76-948e1a017fb8"
  },
  "source_payload": {
    "Název": "Prodej bytu 4+1 87m²Nádražní, Hrochův Týnec",
    "Celková cena:": "5490000Kč",
    "Plocha:": "Užitná plocha 87 m², Celková plocha 97 m²",
    "Příslušenství:": "Bez výtahuČástečně zařízenoLodžieSklepParkovací stání...",
    "source_coordinates": {
      "latitude": 49.9595681020749,
      "longitude": 15.9105578992165,
      "precision": "listing",
      "source": "detail_locality_payload"
    }
  },
  "source_url": "https://www.sreality.cz/detail/prodej/byt/4+1/..."
}
```

## Normalized Artifacts

### Stage Intent

Normalized artifacts convert raw source facts into stable typed fields while
preserving source provenance and leaving unmapped facts explicitly traceable.

Current contract version:

- `normalized-listing-v9`

### Top-Level Fields

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `listing_id` | `string` | Yes | Normalization | Stable listing identifier copied from raw |
| `source_url` | `string` | Yes | Normalization | Source detail URL copied from raw |
| `captured_at_utc` | ISO 8601 UTC datetime string | Yes | Normalization | Raw snapshot timestamp reused for deterministic storage lineage |
| `normalized_at_utc` | ISO 8601 UTC datetime string | Yes | Normalization | Deterministic normalization timestamp for the produced artifact |
| `normalization_version` | `string` | Yes | Normalization | Canonical normalized contract version |
| `core_attributes` | `object` | Yes | Normalization | Typed core listing facts and overflow source attributes |
| `location` | `object` | Yes | Normalization | Typed location facts, nearby places, and source-backed coordinate inputs |
| `normalization_metadata` | `object` | Yes | Normalization | Raw lineage and parser provenance for replay |
| `area_details` | `object` | Yes | Normalization | Typed area fields parsed from source text |
| `energy_details` | `object` | Yes | Normalization | Typed energy-efficiency fields parsed from source text |
| `ownership` | `object` | Yes | Normalization | Ownership facts copied from source |
| `listing_lifecycle` | `object` | Yes | Normalization | Source listing lifecycle dates |
| `source_identifiers` | `object` | Yes | Normalization | Stable source-side identifier fields |

### `core_attributes`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `title` | `string` or `null` | Yes | Normalization | Stable title field copied from raw source text |
| `price` | `object` | Yes | Normalization | Typed price facts parsed from raw price text |
| `building` | `object` | Yes | Normalization | Typed building facts parsed from raw building text |
| `accessories` | `object` | Yes | Normalization | Typed accessory facts parsed from raw accessory text |
| `source_specific_attributes` | `object` | Yes | Normalization | Unmapped or intentionally untyped raw facts preserved verbatim |

#### `core_attributes.price`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `amount_text` | `string` or `null` | Yes | Normalization | Original price text |
| `amount_czk` | `integer` or `null` | Yes | Normalization | Parsed price amount in CZK when available |
| `currency_code` | `string` or `null` | Yes | Normalization | Parsed currency code |
| `pricing_mode` | `string` or `null` | Yes | Normalization | Stable categorical price representation such as `fixed_amount` |
| `note` | `string` or `null` | Yes | Normalization | Price note text copied from raw |

#### `core_attributes.building`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `source_text` | `string` or `null` | Yes | Normalization | Original building text |
| `material` | `string` or `null` | Yes | Normalization | Parsed building material label |
| `structural_attributes` | `array[string]` | Yes | Normalization | Recognized structural fragments preserved as stable labels |
| `physical_condition` | `string` or `null` | Yes | Normalization | Parsed building condition label |
| `floor_position` | `integer` or `null` | Yes | Normalization | Parsed floor position |
| `total_floor_count` | `integer` or `null` | Yes | Normalization | Parsed total floor count |
| `underground_floor_count` | `integer` or `null` | Yes | Normalization | Parsed underground floor count |
| `unparsed_fragments` | `array[string]` | Yes | Normalization | Building fragments preserved when they are not yet typed |

#### `core_attributes.accessories`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `source_text` | `string` or `null` | Yes | Normalization | Original accessories text |
| `has_elevator` | `boolean` or `null` | Yes | Normalization | Parsed elevator presence |
| `is_barrier_free` | `boolean` or `null` | Yes | Normalization | Parsed barrier-free flag |
| `furnishing_state` | `string` or `null` | Yes | Normalization | Stable furnishing category |
| `balcony` | `object` | Yes | Normalization | Balcony presence and optional area |
| `loggia` | `object` | Yes | Normalization | Loggia presence and optional area |
| `terrace` | `object` | Yes | Normalization | Terrace presence and optional area |
| `cellar` | `object` | Yes | Normalization | Cellar presence and optional area |
| `parking_space_count` | `integer` or `null` | Yes | Normalization | Parsed parking count |
| `unparsed_fragments` | `array[string]` | Yes | Normalization | Unsupported accessory fragments kept explicitly |

#### Accessory area objects: `balcony`, `loggia`, `terrace`, `cellar`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `is_present` | `boolean` or `null` | Yes | Normalization | Presence flag for the named accessory |
| `area_sqm` | `number` or `null` | Yes | Normalization | Parsed area in square meters when supplied in the source text |

### `location`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `location_text` | `string` or `null` | Yes | Normalization | Canonical textual locality label |
| `location_text_source` | `string` or `null` | Yes | Normalization | Provenance for `location_text` |
| `street` | `string` or `null` | Yes | Normalization | Parsed street name |
| `street_source` | `string` or `null` | Yes | Normalization | Provenance for `street` |
| `house_number` | `string` or `null` | Yes | Normalization | Parsed house number fragment |
| `house_number_source` | `string` or `null` | Yes | Normalization | Provenance for `house_number` |
| `address_text` | `string` or `null` | Yes | Normalization | Stable source-backed or title-fallback address text |
| `address_text_source` | `string` or `null` | Yes | Normalization | Provenance for `address_text` |
| `city` | `string` or `null` | Yes | Normalization | Parsed municipality name |
| `city_source` | `string` or `null` | Yes | Normalization | Provenance for `city` |
| `city_district` | `string` or `null` | Yes | Normalization | Parsed city-district text |
| `city_district_source` | `string` or `null` | Yes | Normalization | Provenance for `city_district` |
| `location_descriptor` | `string` or `null` | Yes | Normalization | Additional locality descriptor from source text |
| `location_descriptor_source` | `string` or `null` | Yes | Normalization | Provenance for `location_descriptor` |
| `source_coordinate_latitude` | `number` or `null` | Yes | Normalization | Source-backed latitude reshaped from raw source facts |
| `source_coordinate_longitude` | `number` or `null` | Yes | Normalization | Source-backed longitude reshaped from raw source facts |
| `source_coordinate_source` | `string` or `null` | Yes | Normalization | Provenance label for source-backed coordinates |
| `source_coordinate_precision` | `string` or `null` | Yes | Normalization | Source precision hint copied from raw when available |
| `geocoding_query_text` | `string` or `null` | Yes | Normalization | Replayable geocoding input text for later enrichment |
| `geocoding_query_text_source` | `string` or `null` | Yes | Normalization | Provenance for `geocoding_query_text` |
| `nearby_places` | `array[object]` | Yes | Normalization | Supported nearby-place facts normalized from raw source keys |

`location` boundary rules:

- Source-backed coordinates remain normalization-owned source facts, not final
  winning coordinates.
- Normalization may preserve geocoding input text, but it must not persist
  resolved coordinates, confidence, fallback-level, or match-quality outputs.

#### `location.nearby_places[]`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `category` | `string` | Yes | Normalization | Stable nearby-place category label |
| `source_key` | `string` | Yes | Normalization | Original raw source key such as `Bus MHD:` |
| `source_text` | `string` | Yes | Normalization | Original raw nearby-place value |
| `name` | `string` or `null` | Yes | Normalization | Parsed nearby-place name |
| `distance_m` | `integer` or `null` | Yes | Normalization | Parsed nearby-place distance in meters |

### `normalization_metadata`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `source_contract_version` | `string` | Yes | Normalization | Raw contract version observed during normalization replay |
| `source_parser_version` | `string` | Yes | Normalization | Raw parser version that produced the source artifact |
| `source_region` | `string` | Yes | Normalization | Raw region slug propagated into normalized storage layout |
| `source_listing_page_number` | `integer` | Yes | Normalization | Raw listing-page origin |
| `source_scrape_run_id` | `string` | Yes | Normalization | Raw scrape-run lineage key |
| `source_captured_from` | `string` | Yes | Normalization | Raw capture-origin label |
| `source_http_status` | `integer` | Yes | Normalization | Raw accepted HTTP status |

### `area_details`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `source_text` | `string` or `null` | Yes | Normalization | Original area text |
| `usable_area_sqm` | `number` or `null` | Yes | Normalization | Parsed usable area |
| `total_area_sqm` | `number` or `null` | Yes | Normalization | Parsed total area |
| `built_up_area_sqm` | `number` or `null` | Yes | Normalization | Parsed built-up area |
| `garden_area_sqm` | `number` or `null` | Yes | Normalization | Parsed garden area |
| `unparsed_fragments` | `array[string]` | Yes | Normalization | Area fragments not yet promoted into typed fields |

### `energy_details`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `source_text` | `string` or `null` | Yes | Normalization | Original energy text |
| `efficiency_class` | `string` or `null` | Yes | Normalization | Parsed energy class |
| `regulation_reference` | `string` or `null` | Yes | Normalization | Parsed legal-reference fragment |
| `consumption_kwh_per_sqm_year` | `number` or `null` | Yes | Normalization | Parsed energy consumption when available |
| `additional_descriptors` | `array[string]` | Yes | Normalization | Additional supported energy descriptors |
| `unparsed_fragments` | `array[string]` | Yes | Normalization | Unsupported energy fragments preserved explicitly |

### `ownership`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `ownership_type` | `string` or `null` | Yes | Normalization | Ownership label copied from raw source text |

### `listing_lifecycle`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `listed_on` | ISO 8601 date string or `null` | Yes | Normalization | Parsed listing-created date |
| `listed_on_text` | `string` or `null` | Yes | Normalization | Original listing-created date text |
| `updated_on` | ISO 8601 date string or `null` | Yes | Normalization | Parsed last-updated date |
| `updated_on_text` | `string` or `null` | Yes | Normalization | Original last-updated date text |

### `source_identifiers`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `source_listing_reference` | `string` or `null` | Yes | Normalization | Stable listing identifier copied from `ID zakázky:` when available |

### Representative Example

```json
{
  "captured_at_utc": "2026-03-19T12:50:12.965183+00:00",
  "listing_id": "1417442124",
  "normalized_at_utc": "2026-03-19T12:50:12.965183+00:00",
  "normalization_version": "normalized-listing-v9",
  "core_attributes": {
    "title": "Prodej bytu 3+kk 119m²Třída Jiřího Pelikána, Olomouc",
    "price": {
      "amount_czk": 13460000,
      "amount_text": "13460000Kč",
      "currency_code": "CZK",
      "note": "Cena včetně provize a právních služeb",
      "pricing_mode": "fixed_amount"
    },
    "source_specific_attributes": {
      "source_coordinates": {
        "latitude": 49.5978419419202,
        "longitude": 17.2347367318141,
        "precision": "listing",
        "source": "detail_locality_payload"
      }
    }
  },
  "location": {
    "address_text": "Třída Jiřího Pelikána, Olomouc",
    "city": "Olomouc",
    "geocoding_query_text": "Třída Jiřího Pelikána, Olomouc",
    "source_coordinate_latitude": 49.5978419419202,
    "source_coordinate_longitude": 17.2347367318141,
    "source_coordinate_source": "detail_locality_payload",
    "nearby_places": [
      {
        "category": "bus_mhd",
        "distance_m": 132,
        "name": "U Zlaté koule",
        "source_key": "Bus MHD:",
        "source_text": "U Zlaté koule(132 m)"
      }
    ]
  },
  "normalization_metadata": {
    "source_contract_version": "raw-listing-record-v2",
    "source_parser_version": "sreality-detail-v1",
    "source_region": "all-czechia",
    "source_scrape_run_id": "..."
  }
}
```

## Enriched Artifacts

### Stage Intent

Enriched artifacts compute deterministic derived features from normalized
records only. They must keep the full embedded `normalized_record` so later
consumers can audit the exact normalized input that produced the features.

Current contract version:

- `enriched-listing-v16`

### Top-Level Fields

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `listing_id` | `string` | Yes | Enrichment | Stable listing identifier copied forward from normalized |
| `source_url` | `string` | Yes | Enrichment | Source detail URL copied forward from normalized |
| `captured_at_utc` | ISO 8601 UTC datetime string | Yes | Enrichment | Original raw snapshot timestamp reused for deterministic storage lineage |
| `enrichment_version` | `string` | Yes | Enrichment | Canonical enriched contract version |
| `normalized_record` | `object` | Yes | Enrichment | Full normalized input artifact preserved for traceability and replay audit |
| `price_features` | `object` | Yes | Enrichment | Derived price features |
| `property_features` | `object` | Yes | Enrichment | Derived property and building features |
| `location_features` | `object` | Yes | Enrichment | Derived geocoding, location-join, grid, accessibility, and context features |
| `lifecycle_features` | `object` | Yes | Enrichment | Derived freshness and recency features |
| `enrichment_metadata` | `object` or `null` | Yes | Enrichment | Metadata that records derivation time and source normalized contract lineage |

### `price_features`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `asking_price_czk` | `integer` or `null` | Yes | Enrichment | Final asking-price amount copied from typed normalized price facts |
| `price_per_square_meter_czk` | `number` or `null` | Yes | Enrichment | Price per canonical area |
| `price_per_usable_sqm_czk` | `number` or `null` | Yes | Enrichment | Price per usable area |
| `price_per_total_sqm_czk` | `number` or `null` | Yes | Enrichment | Price per total area |
| `has_price_note` | `boolean` | Yes | Enrichment | Indicates whether the normalized price retained a note |

### `property_features`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `disposition` | `string` or `null` | Yes | Enrichment | Parsed disposition derived from normalized title text |
| `canonical_area_sqm` | `number` or `null` | Yes | Enrichment | Preferred area value for downstream price-density features |
| `usable_area_sqm` | `number` or `null` | Yes | Enrichment | Forwarded normalized usable area for convenience |
| `total_area_sqm` | `number` or `null` | Yes | Enrichment | Forwarded normalized total area for convenience |
| `floor_area_sqm` | `number` or `null` | Yes | Enrichment | Compatibility alias of canonical area |
| `is_ground_floor` | `boolean` or `null` | Yes | Enrichment | Derived ground-floor flag |
| `is_upper_floor` | `boolean` or `null` | Yes | Enrichment | Derived upper-floor flag |
| `relative_floor_position` | `string` or `null` | Yes | Enrichment | Stable floor-position bucket |
| `is_top_floor` | `boolean` or `null` | Yes | Enrichment | Derived top-floor flag |
| `is_new_build` | `boolean` or `null` | Yes | Enrichment | Derived new-build flag |
| `building_material_bucket` | `string` or `null` | Yes | Enrichment | Stable material bucket |
| `building_condition_bucket` | `string` or `null` | Yes | Enrichment | Stable condition bucket |
| `energy_efficiency_bucket` | `string` or `null` | Yes | Enrichment | Stable energy-efficiency bucket |
| `has_energy_efficiency_rating` | `boolean` | Yes | Enrichment | Indicates whether a normalized energy class was available |
| `has_balcony` | `boolean` or `null` | Yes | Enrichment | Derived balcony flag |
| `has_loggia` | `boolean` or `null` | Yes | Enrichment | Derived loggia flag |
| `has_terrace` | `boolean` or `null` | Yes | Enrichment | Derived terrace flag |
| `has_cellar` | `boolean` or `null` | Yes | Enrichment | Derived cellar flag |
| `has_elevator` | `boolean` or `null` | Yes | Enrichment | Derived elevator flag |
| `is_barrier_free` | `boolean` or `null` | Yes | Enrichment | Derived barrier-free flag |
| `outdoor_accessory_area_sqm` | `number` or `null` | Yes | Enrichment | Summed outdoor accessory area |
| `furnishing_bucket` | `string` or `null` | Yes | Enrichment | Stable furnishing category |
| `has_city_district` | `boolean` | Yes | Enrichment | Indicates whether normalized city-district text was available |
| `is_prague_listing` | `boolean` | Yes | Enrichment | Indicates whether the normalized municipality resolves to Prague |

### `location_features`

#### Geocoding, resolved address, and precision

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `street` | `string` or `null` | Yes | Enrichment | Forwarded street label used by downstream consumers |
| `street_source` | `string` or `null` | Yes | Enrichment | Provenance for `street` copied from normalization |
| `latitude` | `number` or `null` | Yes | Enrichment | Final winning latitude used for derived spatial features |
| `longitude` | `number` or `null` | Yes | Enrichment | Final winning longitude used for derived spatial features |
| `location_precision` | `string` or `null` | Yes | Enrichment | Precision of the winning coordinate, such as `listing`, `address`, `street`, `district`, or `municipality` |
| `geocoding_source` | `string` or `null` | Yes | Enrichment | Provenance of the winning coordinate |
| `geocoding_confidence` | `string` or `null` | Yes | Enrichment | Stable confidence label for the chosen geocoding outcome |
| `geocoding_match_strategy` | `string` or `null` | Yes | Enrichment | Strategy label describing how the winning coordinate was chosen |
| `geocoding_query_text` | `string` or `null` | Yes | Enrichment | Replayable query text that fed deterministic fallback geocoding |
| `geocoding_query_text_source` | `string` or `null` | Yes | Enrichment | Provenance for `geocoding_query_text` |
| `resolved_address_text` | `string` or `null` | Yes | Enrichment | Resolved address text associated with the winning coordinate |
| `resolved_street` | `string` or `null` | Yes | Enrichment | Resolved street name for the winning coordinate |
| `resolved_house_number` | `string` or `null` | Yes | Enrichment | Resolved house number when available |
| `resolved_city_district` | `string` or `null` | Yes | Enrichment | Resolved city-district label when available |
| `resolved_municipality_name` | `string` or `null` | Yes | Enrichment | Resolved municipality name |
| `resolved_municipality_code` | `string` or `null` | Yes | Enrichment | Resolved municipality code |
| `resolved_region_code` | `string` or `null` | Yes | Enrichment | Resolved region code |
| `geocoding_fallback_level` | `string` or `null` | Yes | Enrichment | Fallback level used when the source-backed coordinate was unavailable |
| `geocoding_is_fallback` | `boolean` or `null` | Yes | Enrichment | Indicates whether the winning coordinate came from fallback geocoding |

#### Administrative joins and municipality matching

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `municipality_name` | `string` or `null` | Yes | Enrichment | Canonical matched municipality name |
| `municipality_code` | `string` or `null` | Yes | Enrichment | Canonical matched municipality code |
| `district_name` | `string` or `null` | Yes | Enrichment | Canonical district name |
| `district_code` | `string` or `null` | Yes | Enrichment | Canonical district code |
| `region_name` | `string` or `null` | Yes | Enrichment | Canonical region name |
| `region_code` | `string` or `null` | Yes | Enrichment | Canonical region code |
| `orp_name` | `string` or `null` | Yes | Enrichment | Canonical ORP name |
| `orp_code` | `string` or `null` | Yes | Enrichment | Canonical ORP code |
| `municipality_latitude` | `number` or `null` | Yes | Enrichment | Municipality centroid latitude from reference data |
| `municipality_longitude` | `number` or `null` | Yes | Enrichment | Municipality centroid longitude from reference data |
| `distance_to_okresni_mesto_km` | `number` or `null` | Yes | Enrichment | Distance from municipality centroid to district city |
| `distance_to_orp_center_km` | `number` or `null` | Yes | Enrichment | Distance from municipality centroid to district-local ORP center |
| `urban_center_profile` | `string` or `null` | Yes | Enrichment | Stable multi-center profile label |
| `distance_to_municipality_center_km` | `number` or `null` | Yes | Enrichment | Distance from winning coordinate to municipality center |
| `distance_to_historic_center_km` | `number` or `null` | Yes | Enrichment | Distance to historic center anchor |
| `distance_to_employment_center_km` | `number` or `null` | Yes | Enrichment | Distance to supported employment anchor |
| `distance_to_primary_rail_hub_km` | `number` or `null` | Yes | Enrichment | Distance to supported primary rail hub |
| `distance_to_airport_km` | `number` or `null` | Yes | Enrichment | Distance to supported airport anchor |
| `metropolitan_area` | `string` or `null` | Yes | Enrichment | Metropolitan area label, currently used for Prague |
| `metropolitan_district` | `string` or `null` | Yes | Enrichment | Metropolitan district label when resolved |
| `distance_to_prague_center_km` | `number` or `null` | Yes | Enrichment | Distance to the Prague historical-center anchor |
| `is_district_city` | `boolean` or `null` | Yes | Enrichment | Indicates whether the municipality is the district city |
| `is_orp_center` | `boolean` or `null` | Yes | Enrichment | Indicates whether the municipality is an ORP center |
| `city_district_normalized` | `string` or `null` | Yes | Enrichment | Stable normalized city-district label |
| `municipality_match_status` | `string` | Yes | Enrichment | Matching outcome status, defaulting to `unmatched` |
| `municipality_match_method` | `string` or `null` | Yes | Enrichment | Matching method used for municipality resolution |
| `municipality_match_input` | `string` or `null` | Yes | Enrichment | Input text used to match the municipality |
| `municipality_match_candidates` | `array[string]` | Yes | Enrichment | Candidate municipality labels retained for auditability |

#### Spatial grid

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `spatial_grid_system` | `string` or `null` | Yes | Enrichment | Identifier of the deterministic grid system |
| `spatial_grid_source_precision` | `string` or `null` | Yes | Enrichment | Precision label of the coordinate used to assign grid cells |
| `spatial_grid_is_approximate` | `boolean` or `null` | Yes | Enrichment | Indicates whether the assigned cells come from an approximate coordinate |
| `spatial_grid_parent_cell_id` | `string` or `null` | Yes | Enrichment | Coarse parent cell identifier |
| `spatial_cell_id` | `string` or `null` | Yes | Enrichment | Canonical cell identifier |
| `spatial_grid_fine_cell_id` | `string` or `null` | Yes | Enrichment | Fine-grained cell identifier |

#### Accessibility and neighborhood context

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `nearest_public_transport_m` | `integer` or `null` | Yes | Enrichment | Minimum supported public-transport distance |
| `nearest_backbone_public_transport_m` | `integer` or `null` | Yes | Enrichment | Minimum backbone transit distance |
| `nearest_metro_m` | `integer` or `null` | Yes | Enrichment | Minimum metro distance |
| `nearest_tram_m` | `integer` or `null` | Yes | Enrichment | Minimum tram distance |
| `nearest_bus_m` | `integer` or `null` | Yes | Enrichment | Minimum bus or MHD distance |
| `nearest_train_m` | `integer` or `null` | Yes | Enrichment | Minimum train distance |
| `has_backbone_public_transport_within_500m` | `boolean` or `null` | Yes | Enrichment | Backbone transit threshold flag at 500 meters |
| `has_backbone_public_transport_within_1000m` | `boolean` or `null` | Yes | Enrichment | Backbone transit threshold flag at 1000 meters |
| `has_metro_within_1000m` | `boolean` or `null` | Yes | Enrichment | Metro threshold flag at 1000 meters |
| `has_tram_within_500m` | `boolean` or `null` | Yes | Enrichment | Tram threshold flag at 500 meters |
| `has_train_within_1500m` | `boolean` or `null` | Yes | Enrichment | Train threshold flag at 1500 meters |
| `nearest_shop_m` | `integer` or `null` | Yes | Enrichment | Minimum supported shop distance |
| `nearest_school_m` | `integer` or `null` | Yes | Enrichment | Minimum school distance |
| `nearest_kindergarten_m` | `integer` or `null` | Yes | Enrichment | Minimum kindergarten distance |
| `amenities_within_300m_count` | `integer` | Yes | Enrichment | Count of supported amenities within 300 meters |
| `amenities_within_1000m_count` | `integer` | Yes | Enrichment | Count of supported amenities within 1000 meters |
| `daily_service_amenities_within_500m_count` | `integer` | Yes | Enrichment | Count of daily-service amenities within 500 meters |
| `community_amenities_within_1000m_count` | `integer` | Yes | Enrichment | Count of community amenities within 1000 meters |
| `leisure_amenities_within_1000m_count` | `integer` | Yes | Enrichment | Count of leisure amenities within 1000 meters |
| `nearest_nature_m` | `integer` or `null` | Yes | Enrichment | Minimum supported nature-proxy distance |
| `has_nature_within_1000m` | `boolean` or `null` | Yes | Enrichment | Nature threshold flag at 1000 meters |

`location_features` boundary rules:

- Enrichment owns the final winning coordinate and all quality labels.
- Source-backed detail coordinates may win, but only through explicit
  enrichment fields such as `geocoding_source`, `location_precision`, and
  `geocoding_match_strategy`.
- Downstream consumers must not infer precision or fallback quality from
  missing fields alone; they should read the explicit geocoding metadata.

### `lifecycle_features`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `listing_age_days` | `integer` or `null` | Yes | Enrichment | Days between `listed_on` and `enriched_at_utc` |
| `updated_recency_days` | `integer` or `null` | Yes | Enrichment | Days between `updated_on` and `enriched_at_utc` |
| `is_fresh_listing_7d` | `boolean` or `null` | Yes | Enrichment | Freshness flag for listings at most seven days old |
| `is_recently_updated_3d` | `boolean` or `null` | Yes | Enrichment | Recency flag for listings updated within three days |

### `enrichment_metadata`

| Field | Type | Required | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `enriched_at_utc` | ISO 8601 UTC datetime string | Yes when object exists | Enrichment | Deterministic enrichment timestamp |
| `source_normalization_version` | `string` | Yes when object exists | Enrichment | Normalized contract version used as the enrichment input |
| `derivation_notes` | `array[string]` | Yes when object exists | Enrichment | Human-readable rules that explain the current deterministic derivation behavior |

### Representative Example

```json
{
  "captured_at_utc": "2026-03-19T12:50:45.148060+00:00",
  "enrichment_version": "enriched-listing-v16",
  "listing_id": "147473228",
  "price_features": {
    "asking_price_czk": 7490000,
    "price_per_square_meter_czk": 249666.67
  },
  "property_features": {
    "canonical_area_sqm": 30.0,
    "disposition": "1+kk",
    "is_new_build": true
  },
  "location_features": {
    "geocoding_match_strategy": "source_detail_coordinate",
    "geocoding_source": "detail_locality_payload",
    "latitude": 50.1095022264146,
    "location_precision": "listing",
    "longitude": 14.5185959581486,
    "metropolitan_area": "Praha",
    "metropolitan_district": "Praha 9",
    "municipality_code": "554782",
    "spatial_cell_id": "sqgrid-v1-r00100-y5010-x1451",
    "urban_center_profile": "prague_polycentric_v1"
  },
  "lifecycle_features": {
    "is_fresh_listing_7d": true,
    "listing_age_days": 0
  },
  "enrichment_metadata": {
    "enriched_at_utc": "2026-03-19T12:50:45.148060+00:00",
    "source_normalization_version": "normalized-listing-v9"
  },
  "normalized_record": {
    "normalization_version": "normalized-listing-v9",
    "listing_id": "147473228"
  },
  "source_url": "https://www.sreality.cz/detail/prodej/byt/1+kk/..."
}
```
