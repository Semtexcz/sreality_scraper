# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and the project uses Semantic Versioning.

## [1.30.1] - 2026-03-19

### Added

- added backlog task `TASK-052` to document raw, normalized, and enriched
  artifacts with field-level references, ownership boundaries, lineage notes,
  and representative examples

### Changed

- refreshed `docs/TASK_SEQUENCE.md` so the active backlog now prioritizes
  artifact-reference documentation ahead of the remaining price-surface design
  task

## [1.30.0] - 2026-03-19

### Added

- added scraper-stage parsing of source-backed detail coordinates into the
  approved raw `source_payload.source_coordinates` object so future raw
  captures preserve GPS without requiring `raw_page_snapshot`
- added regression coverage for structured raw-coordinate parsing, raw
  persistence, collector emission, and normalization precedence across new and
  legacy raw artifacts

### Changed

- changed normalization to prefer structured raw source coordinates before
  legacy `raw_page_snapshot` replay while keeping snapshot parsing as a
  backward-compatible fallback for older stored records
- changed normalization metadata to emit `raw-listing-record-v2` only for raw
  artifacts that carry the structured coordinate object and to keep legacy
  artifacts at `raw-listing-record-v1`
- updated artifact, module, and task-sequence documentation for the active
  source-backed raw-coordinate implementation
- completed `TASK-051` and moved it from `project/backlog/` to `project/done/`

## [1.29.2] - 2026-03-19

### Added

- added the approved `TASK-050` design for a scraper-owned raw-coordinate
  contract, including the optional `source_payload.source_coordinates` object,
  explicit raw provenance, and deterministic migration precedence over legacy
  `raw_page_snapshot` replay

### Changed

- updated architecture, modules, and artifact documentation so raw-coordinate
  ownership is explicit at the scraper boundary and normalization fallback to
  `raw_page_snapshot` is documented as backward-compatible migration behavior
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-050` so the active
  backlog now starts with `TASK-051`
- completed `TASK-050` and moved it from `project/backlog/` to `project/done/`

## [1.29.1] - 2026-03-19

### Added

- added backlog task `TASK-050` to design a scraper-owned raw contract for
  source-backed detail coordinates stored directly in `source_payload`
- added backlog task `TASK-051` to implement raw coordinate parsing so future
  scrapes can preserve GPS without depending on full `raw_page_snapshot`

### Changed

- refreshed `docs/TASK_SEQUENCE.md` so the active backlog now prioritizes the
  raw-coordinate contract and implementation work ahead of `TASK-046`

## [1.29.0] - 2026-03-19

### Added

- added deterministic parsing of source-backed detail coordinates from the
  embedded Sreality `locality` payload stored in `raw_page_snapshot`, including
  normalized `source_coordinate_*` fields and regression coverage for
  coordinate-present and coordinate-missing listings

### Changed

- changed normalization outputs to version `normalized-listing-v9` and
  enrichment outputs to version `enriched-listing-v16` so replayed artifacts now
  preserve source-backed detail coordinates and promote them ahead of fallback
  geocoding when present
- updated architecture, modules, and artifact documentation so the implemented
  coordinate-source precedence is documented as active runtime behavior rather
  than future design guidance
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-049` so the active
  backlog now starts with `TASK-046`
- completed `TASK-049` and moved it from `project/backlog/` to `project/done/`

## [1.28.2] - 2026-03-19

### Added

- added the approved `TASK-048` design for source-backed detail coordinates,
  including normalization-owned `source_coordinate_*` fields and enrichment
  precedence rules for promoting embedded detail-page coordinates ahead of
  deterministic fallback geocoding

### Changed

- updated architecture, module, and artifact documentation so source-backed
  detail coordinates are documented as normalization-owned source facts while
  enrichment remains the canonical owner of the final winning coordinate
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-048` so the backlog
  now starts with `TASK-049`
- completed `TASK-048` and moved it from `project/backlog/` to `project/done/`

## [1.28.1] - 2026-03-19

### Added

- added backlog task `TASK-048` to define the canonical contract for
  source-backed coordinates embedded in Sreality detail HTML
- added backlog task `TASK-049` to implement parsing and propagation of
  source-backed listing coordinates so enrichment can prefer them over fallback
  geocoding

### Changed

- refreshed `docs/TASK_SEQUENCE.md` so the current backlog now prioritizes
  source-backed detail coordinates before the later price-surface design work

## [1.28.0] - 2026-03-19

### Added

- added conservative neighborhood-intensity features under enrichment and
  modeling outputs, including grouped daily-service, community, and leisure
  amenity counts derived from replayable nearby-place categories at fixed radii
- added deterministic environment context fields for nature proximity via
  `nearest_nature_m` and `has_nature_within_1000m` when a normalized
  `prirodni_zajimavost` distance is available
- added regression coverage for grouped amenity counts, nature proximity, and
  workflow replay outputs so micro-location context stays deterministic without
  using price-derived statistics

### Changed

- changed enrichment outputs to version `enriched-listing-v15` and modeling
  inputs to version `modeling-input-v7` so canonical artifacts now include the
  approved neighborhood-intensity and environment feature subset
- updated architecture, module, and artifact documentation so grouped local
  amenity density and nature-proximity ownership remain explicit at the
  enrichment boundary
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-045` so the current
  backlog now starts with `TASK-046`
- completed `TASK-045` and moved it from `project/backlog/` to `project/done/`

## [1.27.0] - 2026-03-19

### Added

- added deterministic multi-center location features under enrichment and
  modeling outputs, including explicit urban-center profile labels plus
  distances to municipality centers, historic centers, primary rail hubs,
  Prague employment anchors, and supported airports
- added backbone public-transport accessibility features derived from
  normalized nearby places, including nearest backbone distance and explicit
  threshold flags for backbone, metro, tram, and rail access
- added regression coverage for Prague polycentric listings, major-city
  municipality fallback, smaller municipalities, and enrichment replay outputs
  so the approved accessibility feature set stays deterministic

### Changed

- changed enrichment outputs to version `enriched-listing-v14` and modeling
  inputs to version `modeling-input-v6` so canonical artifacts now include the
  approved multi-center and accessibility location fields
- updated architecture, module, and artifact documentation so deterministic
  urban-center profiles and backbone accessibility ownership stay documented at
  the enrichment boundary
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-044` so the current
  backlog now starts with `TASK-045`
- completed `TASK-044` and moved it from `project/backlog/` to `project/done/`

## [1.26.0] - 2026-03-19

### Added

- added a canonical `deterministic_square_grid_v1` hierarchy to enriched
  location outputs, including parent, canonical, and fine cell identifiers plus
  explicit grid precision context derived from the best available geocoded
  coordinate
- added modeling-stage support for the approved spatial-grid hierarchy so
  downstream analytical workflows can aggregate listings across multiple spatial
  resolutions without re-deriving cells
- added regression coverage for high-precision address coordinates and
  low-precision municipality coordinates so spatial-grid assignment stays
  deterministic across precision levels

### Changed

- changed enrichment outputs to version `enriched-listing-v13` and modeling
  inputs to version `modeling-input-v5` so canonical artifacts now include
  hierarchical spatial-grid fields
- replaced the Prague-only `spatial_cell_id` derivation with a repository-wide
  deterministic square-grid assignment based on resolved geocoded coordinates
- updated architecture, module, and artifact documentation so spatial grids are
  documented as enrichment-owned location intelligence
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-043` so the current
  backlog now starts with `TASK-044`
- completed `TASK-043` and moved it from `project/backlog/` to `project/done/`

## [1.25.0] - 2026-03-19

### Added

- added replayable geocoding inputs to normalized location artifacts, including
  optional house-number, address-text, and canonical geocoding-query fields
- added explicit multi-level geocoding outputs to enriched location features,
  including resolved latitude and longitude, precision, confidence, fallback
  level, query-text provenance, and resolved address metadata
- added regression coverage for address, street, district, municipality, and
  unresolved geocoding outcomes together with normalization and enrichment
  workflow artifact expectations

### Changed

- changed normalization outputs to version `normalized-listing-v8` and
  enrichment outputs to version `enriched-listing-v12` so canonical artifacts
  now expose deterministic geocoding inputs and outputs
- implemented deterministic offline geocoding using structured normalized
  location inputs, Prague district reference points, municipality centroids,
  and stable query projection for address and street-level estimates
- updated architecture, module, and artifact documentation so the active
  location-intelligence contract now documents implemented geocoding ownership
  and deterministic fallback behavior
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-042` so the current
  backlog now starts with `TASK-043`
- completed `TASK-042` and moved it from `project/backlog/` to `project/done/`

## [1.24.1] - 2026-03-19

### Added

- added the approved `TASK-041` design for multi-level geocoding, including
  canonical address, street, district, municipality, and unresolved precision
  levels together with explicit source, confidence, fallback, and traceability
  fields

### Changed

- updated architecture, module, and artifact documentation so upcoming geocoding
  work keeps source-backed address inputs in normalization, resolved
  coordinates and quality metadata in enrichment, and only stable geocoding
  helpers in modeling
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-041` so the current
  backlog now starts with `TASK-042`
- completed `TASK-041` and moved it from `project/backlog/` to `project/done/`

## [1.24.0] - 2026-03-19

### Added

- added regression coverage for unbounded-by-default scrape runs across CLI
  option building, terminal progress reporting, acquisition orchestration, and
  runtime composition so the scraper no longer silently stops after `50`
  listings

### Changed

- changed `scraperweb scrape` so omitting `--max-estates` now leaves estate
  traversal unbounded by default, while explicit `--max-pages` and
  `--max-estates` caps keep their previous bounded-run behavior
- updated scraper progress output and operator-facing CLI documentation to label
  omitted estate caps as `unbounded`
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-047` so the current
  backlog now starts with `TASK-041`
- completed `TASK-047` and moved it from `project/backlog/` to `project/done/`

## [1.23.1] - 2026-03-19

### Added

- added backlog task `TASK-047` to track removing the default `50`-estate cap
  so routine `scraperweb scrape` runs collect all available listings unless an
  explicit runtime limit is provided

### Changed

- refreshed `docs/TASK_SEQUENCE.md` so the current backlog now starts with
  `TASK-047` before the pending geocoding and spatial work

## [1.23.0] - 2026-03-19

### Added

- added conservative structured street fields to normalized location outputs,
  including explicit `street` and `street_source` provenance captured only when
  title parsing finds a reliable street-to-location split
- added enrichment pass-through fields for normalized street facts so downstream
  consumers can read canonical street data from `location_features` without
  re-parsing raw titles
- added regression coverage for Prague and non-Prague street-prefixed titles,
  municipality-only street suffixes, and ambiguous titles that must keep street
  fields empty

### Changed

- changed normalization outputs to version `normalized-listing-v7` and
  enrichment outputs to version `enriched-listing-v11` so canonical artifacts
  now include structured street location fields
- refreshed the affected normalized fixture artifacts used by enrichment
  workflow coverage so persisted contract expectations match the current street
  parsing behavior
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-040` so the backlog
  now starts with `TASK-041`
- completed `TASK-040` and moved it from `project/backlog/` to `project/done/`

## [1.22.3] - 2026-03-19

### Changed

- reformatted `docs/TASK_SEQUENCE.md` into an explicit ordered backlog plan with
  task-by-task focus, phase, and sequencing rationale for `TASK-040` through
  `TASK-046`

## [1.22.2] - 2026-03-19

### Added

- added backlog tasks `TASK-041` through `TASK-046` to cover multi-level
  geocoding, spatial grids, center-distance and accessibility signals,
  neighborhood context, and a map-ready price-surface workflow

### Changed

- refreshed `docs/TASK_SEQUENCE.md` so the backlog now sequences the location
  intelligence expansion from structured address fields through price-surface
  design

## [1.22.1] - 2026-03-19

### Added

- added backlog task `TASK-040` to track the missing structured street field in
  normalized and enriched location data

### Changed

- refreshed `docs/TASK_SEQUENCE.md` so the current backlog now lists `TASK-040`

## [1.22.0] - 2026-03-18

### Added

- added a supported filesystem-backed enrichment replay workflow that reads
  persisted normalized artifacts and emits canonical enriched JSON snapshots
  under `data/enriched/<region>/<listing_id>/<captured_at_utc>.json`
- added CLI support for `scraperweb enrich` with `--region`, `--listing-id`,
  and `--scrape-run-id` selectors plus integration-style replay coverage for
  representative normalized artifacts

### Changed

- updated operator and developer documentation so enrichment is now described as
  a supported stage entrypoint with deterministic artifact layout and
  normalized-to-enriched traceability guarantees
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-034` so the current
  backlog is empty
- completed `TASK-034` and moved it from `project/backlog/` to `project/done/`

## [1.21.0] - 2026-03-18

### Added

- added the approved stable location-intelligence subset to
  `ModelingFeatureSet`, including administrative identifiers, metropolitan
  buckets, coordinate and macro-distance metrics, district-center flags, and
  nearby-place accessibility aggregates
- added focused modeling regression coverage for the enrichment-to-modeling
  location handoff, including Prague administrative, spatial, and amenity
  features

### Changed

- changed modeling inputs to version `modeling-input-v4` and model metadata to
  `listing-baseline-v2` so the canonical modeling contract now includes
  explicit location-derived features from enrichment
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-039` so the
  remaining backlog now contains only `TASK-034`

## [1.20.0] - 2026-03-18

### Added

- added optional metropolitan location enrichment fields for Prague under
  `location_features`, including `metropolitan_area`,
  `metropolitan_district`, `spatial_cell_id`, and
  `distance_to_prague_center_km`
- added Prague-specific district reference mapping for both numbered municipal
  inputs and supported named districts, plus regression coverage for Prague and
  non-metropolitan listings

### Changed

- changed enrichment outputs to version `enriched-listing-v10` so the canonical
  location contract now includes deterministic metropolitan district bucketing
  and Prague center-distance semantics
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-038` so the
  remaining backlog order now starts with `TASK-039`

## [1.19.0] - 2026-03-18

### Added

- added deterministic lifecycle enrichment fields under
  `lifecycle_features`, including `listing_age_days`,
  `updated_recency_days`, `is_fresh_listing_7d`, and
  `is_recently_updated_3d`, all derived only from
  `normalized_record.listing_lifecycle`
- added focused enrichment regression coverage for stable lifecycle snapshots,
  inconsistent source date ordering, and future-dated lifecycle inputs that
  must remain optional

### Changed

- changed enrichment outputs to version `enriched-listing-v9` so the canonical
  contract now exposes lifecycle freshness semantics using
  `enrichment_metadata.enriched_at_utc` as the deterministic reference point
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-033` so the
  remaining backlog order now starts with `TASK-038`

## [1.18.0] - 2026-03-18

### Added

- added deterministic nearby-place accessibility enrichment fields, including
  grouped nearest-distance metrics for public transport and shops plus explicit
  minima for metro, tram, bus, train, school, and kindergarten access
- added amenity-density counts for normalized nearby places within `300 m` and
  `1000 m`, with regression coverage for Prague and non-Prague listings,
  malformed nearby-place parsing, and missing distance values

### Changed

- changed enrichment outputs to version `enriched-listing-v8` so
  `location_features` now expose canonical nearby-place accessibility signals
  derived only from `normalized_record.location.nearby_places`
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-032` so the
  remaining backlog order now starts with `TASK-033`

## [1.17.0] - 2026-03-18

### Added

- added explicit accessory-derived enrichment fields, including nullable
  booleans for balcony, loggia, terrace, cellar, elevator, and barrier-free
  access, plus `outdoor_accessory_area_sqm` and `furnishing_bucket`
- added focused enrichment regression coverage for measured accessory areas,
  absent accessory values, and ambiguous raw accessory fragments that must stay
  ignored by enrichment

### Changed

- changed enrichment outputs to version `enriched-listing-v7` so the canonical
  contract now includes deterministic accessory and outdoor-space semantics
  sourced only from `normalized_record.core_attributes.accessories`
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-031` so the remaining
  backlog order now starts with `TASK-032`

## [1.16.0] - 2026-03-18

### Added

- added deterministic building semantics in enrichment and modeling outputs,
  including `is_ground_floor`, `is_upper_floor`,
  `relative_floor_position`, `building_material_bucket`, and
  `building_condition_bucket`, derived only from
  `normalized_record.core_attributes.building`
- added focused regression coverage for high-rise top-floor semantics, middle
  floor interpretation, and explicit ground-floor handling in low-rise
  buildings

### Changed

- changed enrichment outputs to version `enriched-listing-v6` so the canonical
  contract now includes conservative floor-position, building-material, and
  building-condition semantics derived from normalized building fields only
- changed modeling inputs to version `modeling-input-v3` so the new stable
  building semantics now cross the enrichment-to-modeling boundary
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-030` so the
  remaining backlog order now starts with `TASK-031`
- updated enrichment module documentation to record that building layout and
  condition features now ship from the enrichment stage with conservative
  nullable bucket mappings

## [1.15.0] - 2026-03-18

### Added

- added explicit area-derived enrichment fields sourced from
  `normalized_record.area_details`, including `canonical_area_sqm`,
  `usable_area_sqm`, `total_area_sqm`, `price_per_usable_sqm_czk`, and
  `price_per_total_sqm_czk`
- added focused enrichment regression coverage for canonical-area fallback from
  usable to total area and for zero-valued normalized areas that must stay
  optional

### Changed

- changed enrichment outputs to version `enriched-listing-v5` so floor-area and
  price-density metrics now depend on normalized typed area fields instead of
  title regex parsing while preserving `floor_area_sqm` as a compatibility alias
  of the canonical area feature
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-029` so the remaining
  backlog order now starts with `TASK-030`
- updated enrichment module documentation to record that canonical area and
  area-based price-density features are now derived strictly from normalized
  area fields

## [1.14.0] - 2026-03-18

### Added

- added municipality centroid coordinates and deterministic macro-distance
  features to `location_features`, including
  `municipality_latitude`, `municipality_longitude`,
  `distance_to_okresni_mesto_km`, and `distance_to_orp_center_km`
- added focused enrichment regression coverage for municipality coordinates,
  district-city zero-distance handling, ordinary municipality distance
  calculations, and unresolved location matches that keep spatial fields empty

### Changed

- changed enrichment outputs to version `enriched-listing-v4` so the canonical
  contract now includes the first coordinate and macro-distance location
  features
- documented that enrichment now computes great-circle distances from
  municipality centroids to district-city centroids and district-local ORP
  centers, while metropolitan overrides and spatial cells remain deferred

## [1.13.0] - 2026-03-18

### Added

- added enrichment-owned `location_features` with conservative municipality
  matching, administrative identifiers, district-city and ORP-center flags, and
  explicit match-status traceability derived from the bundled reference datasets
- added regression coverage for Prague municipality normalization, duplicate
  municipality ambiguity, district-aware disambiguation via location text, and
  explicit unmatched-location handling

### Changed

- changed enrichment outputs to version `enriched-listing-v3` so the canonical
  contract now includes the first reference-backed administrative location
  feature set
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-036` so the remaining
  backlog order now starts with `TASK-037`
- updated module documentation to reflect that the first location-intelligence
  features now ship from the enrichment stage while coordinate and spatial work
  remains deferred to later tasks

## [1.12.8] - 2026-03-18

### Added

- added the approved `TASK-035` design for location intelligence, including
  stage ownership, canonical administrative and spatial fields, explicit
  ambiguity handling, and bundled-reference matching provenance rules

### Changed

- updated architecture, module, artifact, and operator documentation so
  reference-backed municipality mapping, coordinates, district-center flags, and
  spatial buckets are now documented as enrichment-owned derived features rather
  than normalization outputs
- refreshed `docs/TASK_SEQUENCE.md` after completing `TASK-035` so the remaining
  backlog order starts with `TASK-036`

## [1.12.7] - 2026-03-18

### Changed

- updated `AGENTS.md` so agents must refresh `docs/TASK_SEQUENCE.md` whenever
  the number of backlog tasks changes

## [1.12.6] - 2026-03-18

### Changed

- renamed `docs/ENRICHMENT_TASK_SEQUENCE.md` to `docs/TASK_SEQUENCE.md` and
  generalized the document so it serves as a reusable backlog ordering overview
- updated `docs/README.md` to reference the generalized task sequence document

## [1.12.5] - 2026-03-18

### Changed

- simplified `docs/ENRICHMENT_TASK_SEQUENCE.md` into a short overview with a
  single ordering table and compact delivery batches

## [1.12.4] - 2026-03-18

### Added

- added `docs/ENRICHMENT_TASK_SEQUENCE.md` to document the recommended
  implementation order, dependency rationale, and delivery batches for
  `TASK-029` through `TASK-039`

### Changed

- updated `docs/README.md` so the new enrichment task sequence document is listed
  alongside the other technical documentation files

## [1.12.3] - 2026-03-18

### Added

- added location-intelligence backlog tasks `TASK-035` through `TASK-039` for
  reference-backed municipality matching, administrative codes, coordinates,
  macro-distance metrics, metropolitan spatial bucketing, and propagation of
  those features into the modeling boundary
- expanded `TASK-032` and `TASK-034` so the enrichment backlog now captures the
  concrete nearby-place feature set and the requirement to replay future
  location intelligence through an operator-facing enrichment workflow

## [1.12.2] - 2026-03-18

### Added

- added backlog tasks `TASK-029` through `TASK-034` to break the remaining
  enrichment-stage roadmap work into explicit deliverables covering typed
  area-based pricing, building semantics, accessories, nearby-place
  accessibility, lifecycle freshness, and an operator-facing enrichment replay
  workflow

## [1.12.1] - 2026-03-18

### Added

- added representative normalization replay validation for persisted raw
  snapshots that exercise both `location.nearby_places` and
  `core_attributes.accessories` in serialized filesystem artifacts

### Changed

- updated operator-facing documentation to record artifact validation
  expectations, canonical access paths for nearby places and accessories, and
  the current decision to defer downstream consumption of these typed fields in
  enrichment and modeling
- recorded migration guidance for normalized artifacts so reviewers can verify
  that mapped nearby-place keys and `Příslušenství:` values no longer remain in
  `core_attributes.source_specific_attributes` after replay

## [1.12.0] - 2026-03-18

### Added

- added typed `core_attributes.accessories` normalization output with explicit
  elevator, barrier-free access, furnishing state, balcony/loggia/terrace/cellar,
  and parking-space capacity fields sourced from `Příslušenství:`
- added focused accessories regression coverage for duplicated leading fragments,
  measured accessory features, parking counts, and ambiguous fragments such as
  `2 garáže`

### Changed

- changed normalization outputs to version `normalized-listing-v6` so supported
  accessories now map into the canonical core-attributes contract instead of
  remaining only under `source_specific_attributes`

## [1.11.1] - 2026-03-18

### Added

- added the approved design for normalized accessories support, including the
  `core_attributes.accessories` contract shape, shared area-feature sub-model,
  conservative fallback rules, and the planned normalization contract bump to
  `normalized-listing-v6`

## [1.11.0] - 2026-03-18

### Added

- added typed `location.nearby_places` normalization output with explicit
  `category`, `source_key`, `source_text`, `name`, and `distance_m` fields for
  supported nearby-place payload keys
- added focused nearby-place regression coverage for persisted raw snapshots and
  malformed-but-supported source values so normalization keeps traceability

### Changed

- changed normalization outputs to version `normalized-listing-v5` so supported
  nearby-place keys now map into the canonical location contract instead of
  remaining only under `core_attributes.source_specific_attributes`

## [1.10.2] - 2026-03-18

### Added

- added the approved design for normalized nearby-place support, including the
  `location.nearby_places` contract shape, overflow coexistence rules, parser
  fallback strategy, and the planned normalization contract bump to
  `normalized-listing-v5`

## [1.10.1] - 2026-03-18

### Added

- added backlog tasks for designing and implementing normalized nearby-place
  parsing and structured accessories parsing, including a follow-up replay and
  documentation task for the resulting schema evolution

## [1.10.0] - 2026-03-18

### Added

- added derived enrichment features for normalized building and energy fields,
  including optional `is_top_floor`, `is_new_build`, and
  `energy_efficiency_bucket` semantics alongside the existing price metrics
- added focused enrichment regression coverage built from normalized record
  fixtures so derived feature behavior stays deterministic without raw payload
  parsing

### Changed

- changed enrichment outputs to version `enriched-listing-v2` so the canonical
  contract now exposes the new building and energy derived features while
  preserving the full normalized source record for traceability
- changed modeling inputs to version `modeling-input-v2` so downstream
  consumers receive the new derived building and energy features at the
  modeling boundary
- changed asking-price derivation to rely on normalized typed monetary fields
  only instead of reparsing preserved raw price text during enrichment

## [1.9.0] - 2026-03-18

### Added

- added typed normalized price fields for Czech listing prices, including parsed
  integer `amount_czk`, explicit `currency_code`, and deterministic
  `pricing_mode` while preserving the original source text
- added structured normalized building and energy contracts with source text,
  floor position metadata, physical condition, underground floor counts, energy
  regulation references, and consumption values parsed directly from raw detail
  payloads
- added focused normalization regression coverage for representative
  `data/raw/all-czechia` snapshots covering fixed-price listings, on-request
  pricing, richer building layouts, energy descriptors, and partially parsed
  building fragments

### Changed

- changed normalization outputs to version `normalized-listing-v4` so explicit
  typed price, building, and energy fields are now emitted in the canonical
  contract instead of overloading `building.condition` or leaving price and
  energy mostly as raw text
- changed enrichment price resolution to prefer normalized typed price amounts
  and to fall back to legacy text parsing only when typed price data is missing

## [1.8.3] - 2026-03-18

### Changed

- updated `docs/ROADMAP.md` so the pipeline and operations checklist now reflects
  the shipped normalization replay workflow and normalized filesystem artifact
  persistence as completed work, while narrowing the remaining persistence
  decisions to enrichment, modeling, and possible backend expansion

## [1.8.2] - 2026-03-18

### Added

- added a public `scraperweb normalize` CLI workflow that replays persisted raw
  filesystem snapshots into normalized JSON artifacts scoped by region,
  listing id, or scrape run id
- added filesystem-backed normalization workflow services and integration-style
  tests that exercise representative raw fixtures derived from
  `data/raw/all-czechia`

### Changed

- changed generated artifacts documentation to include normalized filesystem
  outputs and their traceability guarantees
- changed roadmap and module documentation so normalization is now documented as
  a supported operator-facing workflow instead of an internal-only stage

## [1.8.1] - 2026-03-18

### Added

- added typed location descriptor and per-field provenance metadata so normalized
  location values now distinguish direct `Lokalita:` payload facts from
  title-derived fallback values
- added regression coverage for representative Prague and non-Prague title
  patterns from `data/raw/all-czechia`, including titles without a comma
  separator before the location suffix

### Changed

- changed location normalization to prefer dedicated raw payload fields where
  available and to isolate remaining title parsing behind documented fallback
  rules instead of the previous naive comma split
- changed Prague numbered-district fallback parsing so municipality identity now
  normalizes to `Praha` while keeping the district name in `city_district`

## [1.8.0] - 2026-03-18

### Added

- added grouped normalized fields for area details, ownership, listing
  lifecycle dates, and source listing references derived directly from the
  Sreality detail payload
- added regression coverage for representative `data/raw/all-czechia`
  snapshots and partial area parsing so mapped fields remain deterministic and
  traceable

### Changed

- changed normalization to parse supported `Plocha:` fragments into explicit
  typed area fields while preserving unsupported fragments in the normalized
  contract instead of leaving the raw text only in source-specific overflow
- changed normalization overflow handling so `Vlastnictví:`, `ID zakázky:`,
  `Vloženo:`, and `Upraveno:` now map into dedicated typed sub-contracts
  instead of remaining under `source_specific_attributes`

## [1.7.7] - 2026-03-18

### Added

- added backlog tasks `TASK-019` through `TASK-021` to break the remaining
  normalization-stage roadmap work into explicit deliverables grounded in the
  current `data/raw/all-czechia` payload coverage

## [1.7.6] - 2026-03-18

### Fixed

- fixed detail-page parsing so empty optional `dd` rows no longer cause the
  whole listing to be rejected; the scraper now skips empty values and keeps
  parsing the remaining attributes

## [1.7.5] - 2026-03-18

### Added

- added persisted detail-page markup failure artifacts so skipped listings now
  store the raw failed HTML snapshot and serialized failure metadata for later
  diagnostics in both filesystem and MongoDB backends

## [1.7.4] - 2026-03-18

### Changed

- changed default scraper recovery so detail-page markup validation failures are
  now logged and skipped per listing instead of terminating the whole region run
- changed terminal progress reporting to show skipped listings caused by detail
  markup failures in addition to skipped HTTP failures

## [1.7.3] - 2026-03-17

### Added

- added terminal progress reporting so default scraper runs now announce start,
  per-page activity, periodic processed-estate counts, skipped detail failures,
  and region completion
- added `--verbose` and `--quiet` CLI options to control scraper progress output

### Changed

- changed CLI runtime option validation to reject conflicting `--verbose` and
  `--quiet` combinations
- changed scraper runtime composition to inject a dedicated progress reporter
  instead of relying only on logger output for operator visibility

## [1.7.2] - 2026-03-17

### Added

- added a `--fail-on-http-error` CLI option for debug runs that should stop on
  the first scraper HTTP failure

### Changed

- changed the default scrape behavior so detail-page HTTP failures are logged and
  skipped instead of terminating the whole run
- changed the acquisition flow so scraper HTTP failures are logged by default
  without crashing the CLI unless fail-fast mode is explicitly enabled

## [1.7.1] - 2026-03-17

### Fixed

- fixed the default scrape behavior so runs without `--max-pages` no longer stop
  after the first listing page and instead continue across the all-Czechia
  listing target until scraper stop conditions are met

### Changed

- changed the `--max-pages` CLI option from a required default page cap to an
  optional traversal limit

## [1.7.0] - 2026-03-17

### Added

- added a global `all-czechia` scrape target that points to the nationwide
  apartment-sale listing URL on `sreality.cz`
- added regression coverage for the new default global target at both CLI and
  runtime-composition levels

### Changed

- changed the default CLI behavior so runs without `--region` now scrape the
  global all-Czechia apartment listing target instead of iterating region URLs
- replaced index-based region URL selection with explicit region-slug to listing
  URL mapping in the scraper runtime

## [1.6.0] - 2026-03-17

### Added

- added deterministic traversal regression coverage for repeated listing pages,
  empty listing pages, and pagination drift pages that contain no unseen estate
  URLs

### Changed

- replaced the collector's pagination-count traversal assumption with
  page-by-page stop conditions driven by observed listing-page outcomes
- documented the operator-visible region traversal stop conditions that now end a
  run on empty, repeated, or fully duplicated listing pages before `max_pages`

## [1.5.0] - 2026-03-17

### Added

- added parser-owned markup validation errors for listing and detail pages so
  missing detail links, missing titles, and malformed attribute sections fail
  explicitly instead of producing low-value raw payloads
- added fixture-based parser and collector tests that cover valid markup,
  missing listing links, missing detail titles, and misaligned detail
  attributes

### Changed

- updated the scraper runtime to translate parser validation failures into
  contextual scraper response errors with region, listing-page, and listing-URL
  metadata
- documented the minimum listing-page and detail-page structural assumptions
  that anchor the scraper-stage raw contract

## [1.4.0] - 2026-03-17

### Added

- added scraper-owned HTTP exception types that distinguish bounded-retry
  transport failures from terminal response validation errors while preserving
  region, listing-page, and listing-URL context for callers
- added deterministic unit coverage for successful fetches, transient retry
  recovery, retry exhaustion, invalid HTTP status handling, empty-response
  handling, and acquisition-time failure logging

### Changed

- hardened the scraper HTTP client to validate response status and content, apply
  bounded retries only to transient timeout and connection failures, and fail
  fast for terminal request and response errors
- updated raw acquisition flow to log operator-visible failure context before
  propagating scraper-stage HTTP errors without introducing downstream
  normalization or enrichment behavior

## [1.3.3] - 2026-03-17

### Added

- added backlog tasks `TASK-016` through `TASK-018` to break the remaining
  scraper-stage roadmap work into explicit deliverables for HTTP hardening,
  response and markup validation, and traversal stop-condition redesign

## [1.3.2] - 2026-03-17

### Changed

- restructured `docs/ROADMAP.md` from time-based sections into stage-based
  checklists so implemented and remaining work are tracked per pipeline boundary
  and operational area

## [1.3.1] - 2026-03-17

### Changed

- rewrote `docs/ROADMAP.md` to reflect the current implemented repository state,
  distinguish public runtime capabilities from internal stage components, and focus
  future roadmap items on the remaining operational and product gaps

## [1.3.0] - 2026-03-17

### Added

- added a deterministic modeling-stage `EnrichedListingModelingInputBuilder`
  component that accepts `EnrichedListingRecord` inputs only and emits stable
  `ModelingInputRecord` contracts with explicit model-ready feature and target sets
- added a synchronous `LinearListingPipelineService` that composes scraper,
  normalization, enrichment, and modeling in one in-process sequence without
  replacing the existing raw-only acquisition workflow
- added regression tests that cover stage handoff contracts across the full linear
  pipeline and keep the modeling boundary isolated from upstream non-enriched inputs

### Changed

- replaced the modeling placeholder contract with a typed schema that includes
  `model_version`, `modeling_input_version`, explicit modeling metadata, and full
  enriched-record traceability for downstream consumers
- updated module documentation to mark the modeling package as an active stage with
  a concrete runtime component

## [1.2.0] - 2026-03-17

### Added

- added a deterministic enrichment-stage `NormalizedListingEnricher` component that
  accepts `NormalizedListingRecord` inputs only and emits stable
  `EnrichedListingRecord` contracts
- added explicit derived price and property feature contracts for parsed asking
  price, disposition, floor area, price per square meter, and stage-level boolean
  flags needed by downstream modeling work

### Changed

- replaced the enrichment placeholder contract with a typed schema that includes an
  `enrichment_version` field, preserves the full normalized input record for
  traceability, and documents the initial V1 feature derivations
- expanded module and unit-test coverage so enrichment remains isolated from
  scraper-stage contracts and normalization behavior

## [1.1.0] - 2026-03-17

### Added

- added a normalization-stage `RawListingNormalizer` component that converts
  scraper-owned `RawListingRecord` snapshots into stable `NormalizedListingRecord`
  contracts with explicit provenance metadata
- added explicit normalized price, building, and location sub-contracts plus
  deterministic regression tests for representative normalization mappings

### Changed

- replaced the placeholder normalization contract with a stable typed schema that
  includes `normalization_version`, preserves unmapped raw fields under
  `source_specific_attributes`, and represents missing typed values as `None`

## [1.0.9] - 2026-03-17

### Added

- added a scraper-owned `RawListingCollector` service that emits `RawListingRecord`
  contracts before persistence, keeping raw contract construction inside the scraper
  stage boundary

### Changed

- tightened the raw scraper payload contract to explicit JSON-compatible value types
  and removed the storage-oriented `backend` field from raw source metadata
- refactored `RawAcquisitionService` to orchestrate scraper-emitted raw records
  instead of constructing persistence-shaped records itself
- expanded unit coverage to prove emitted scraper outputs remain source-faithful,
  JSON-serializable, and free of downstream normalized or derived fields

## [1.0.8] - 2026-03-17

### Changed

- removed the temporary `scraperweb.scraping` compatibility package and updated the
  codebase to import scraper clients and parsers directly from `scraperweb.scraper`
- removed `scraperweb.persistence.models` so raw-contract ownership now exists only
  under `scraperweb.scraper.models`, reducing duplicate module surfaces inside
  `scraperweb`

## [1.0.7] - 2026-03-17

### Added

- added explicit `scraperweb.scraper`, `scraperweb.normalization`,
  `scraperweb.enrichment`, and `scraperweb.modeling` package boundaries with typed
  stage-contract modules for the planned linear pipeline
- added regression tests that enforce one-way stage dependencies across the new
  pipeline packages

### Changed

- moved canonical raw-contract ownership to `scraperweb.scraper.models` and updated
  the active runtime to import scraper-stage clients, parsers, and contracts from the
  new package boundary
- converted `scraperweb.scraping.*` and `scraperweb.persistence.models` into
  documented compatibility wrappers so the CLI and raw persistence path keep working
  during the transition

## [1.0.6] - 2026-03-17

### Changed

- approved and documented the in-repo modular pipeline target architecture with
  explicit `scraper`, `normalization`, `enrichment`, and `modeling` stage boundaries
- defined one-way stage dependencies, typed stage-boundary contracts, and module
  ownership rules in the architecture and module documentation
- synchronized package version metadata so `pyproject.toml` and `scraperweb.__version__`
  expose the same release version

## [1.0.5] - 2026-03-17

### Changed

- refined backlog tasks `TASK-010` through `TASK-015` with additive architectural guardrails for typed stage contracts, module ownership, dependency direction, stage version fields, raw-contract serialization, normalization idempotence, and contract-only pipeline handoffs

## [1.0.4] - 2026-03-17

### Added

- added a new `project/backlog/` task set for migrating the repository toward a simple modular pipeline with `scraper`, `normalization`, `enrichment`, and `modeling` stages

### Changed

- aligned the project planning backlog with the existing task template and explicit stage dependencies for the modular pipeline migration

## [1.0.3] - 2026-03-17

### Changed

- moved the test suite under a single `tests/` tree split into `tests/unit/` and `tests/integration/`, keeping shared fixtures under `tests/`

## [1.0.2] - 2026-03-17

### Added

- added an opt-in `integration_tests/` suite with a live Sreality runtime test that downloads and processes one real listing through the production clients, parsers, acquisition service, and filesystem repository

### Changed

- separated pytest discovery for deterministic unit tests and live integration tests, and documented how to enable the live suite explicitly

## [1.0.1] - 2026-03-17

### Added

- added representative HTML fixtures plus regression tests for scraping clients and parser contracts
- added CLI tests for MongoDB runtime selection and Typer-enforced bounded runtime options

### Changed

- expanded raw storage and acquisition service coverage to verify path sanitization, immutable raw payload persistence, and runtime stop conditions

## [1.0.0] - 2026-03-17

### Changed

- narrowed the supported runtime surface to raw listing acquisition and raw persistence only
- simplified runtime configuration to MongoDB values used for raw storage selection
- updated operator documentation to remove enrichment and auxiliary loader workflows

### Removed

- removed the `load-towns` and `load-districts` CLI commands and their legacy runtime modules
- removed geocoding-specific settings and the `geopy` dependency from the active runtime path

## [0.2.1] - 2026-03-17

### Changed

- removed legacy compatibility wrappers and compatibility-only entrypoints so the package exposes only the current CLI and module surface
- updated parser tests and operator documentation to target the active implementation instead of transitional aliases

### Removed

- removed compatibility modules `scraperweb.main`, `scraperweb.cities_data`, and `scraperweb.districts`
- removed compatibility-only Poetry script entrypoints and legacy wrapper scripts
- removed obsolete `SCRAPER_API_URL` configuration and the unused HTTP JSON-post helper

## [0.2.0] - 2026-03-17

### Added

- added a Typer-based `scraperweb` CLI with explicit `scrape`, `load-towns`, and `load-districts` commands
- added CLI regression tests covering scraper command option handling and auxiliary loader command dispatch

### Changed

- replaced the primary Poetry script entrypoint with the new Typer application while keeping legacy loader entrypoints as compatibility wrappers
- refactored runtime option parsing into reusable validation helpers so CLI handlers stay thin and service-oriented
- documented the raw-data-only CLI contract and updated operator usage examples in `README.md`

## [0.1.9] - 2026-03-17

### Added

- added `scraperweb.persistence` with canonical raw-record models plus filesystem and MongoDB storage adapters
- added historical snapshot persistence keyed by `listing_id` and `captured_at_utc` to preserve longitudinal price data for later analysis
- added repository tests covering filesystem storage, MongoDB index setup, and raw acquisition record construction

### Changed

- refactored `scraperweb.application.acquisition_service.RawAcquisitionService` to build immutable `RawListingRecord` objects and persist them through a storage abstraction
- updated `scraperweb.estate_scraper` to select persistence backends without changing orchestration flow
- documented operational tradeoffs and generated artifact layout for filesystem and MongoDB raw storage backends

## [0.1.8] - 2026-03-17

### Added

- added `scraperweb.scraping.clients` with dedicated HTTP client classes for listing and detail page retrieval
- added `scraperweb.scraping.parsers` with dedicated listing-page and detail-page parser classes
- added `scraperweb.application.acquisition_service.RawAcquisitionService` for explicit orchestration of discovery and detail record collection

### Changed

- refactored `scraperweb.estate_scraper` to compose runtime behavior from injected services instead of a single procedural flow
- moved record delivery side effects behind `EstateRecordProcessor`, keeping parser classes side-effect free
- preserved compatibility helper functions (`get_range_of_estates`, `get_list_of_estates`, `get_final_data_for_estate_to_database`) by delegating them to the new classes

## [0.1.7] - 2026-03-17

### Added

- documented target application layers for CLI, orchestration, scraping/parsing, and persistence in `docs/ARCHITECTURE.md`
- documented the raw record contract (`RawListingRecord`) with explicit exclusions for enrichment, normalization, and derived fields
- documented target core interfaces and planned concrete adapters aligned to SOLID boundaries

### Changed

- updated `docs/MODULES.md` with target layered module boundaries for the refactor
- identified transitional modules and replacement/removal direction for the raw-data architecture migration

## [0.1.6] - 2026-03-17

### Added

- added a dedicated `scraperweb.cli_runtime_options` module that defines runtime CLI options for region selection, page limits, estate limits, and storage backend selection
- added parser validation for backend-specific option constraints to keep the future Typer CLI contract explicit and testable
- added deterministic tests for runtime option defaults, limit parsing, and backend option compatibility checks

### Changed

- updated `scraperweb.estate_scraper` entrypoint to parse and apply region/page/estate runtime limits
- documented required, optional, and mutually constrained runtime options in `README.md`

## [0.1.5] - 2026-03-17

### Added

- added bootstrap `tests/` coverage for configuration defaults and deterministic parsing helpers
- added shared test fixtures for mocked HTTP responses to keep tests independent from live network services

### Changed

- configured pytest discovery via `pyproject.toml` and registered `pytest` as a Poetry development dependency

### Fixed

- fixed `scraperweb.config.Settings` so environment variable overrides are evaluated at runtime instead of module import time

## [0.1.4] - 2026-03-17

### Changed

- rewrote backlog tasks into a structured front-matter format with problem statements and definitions of done
- documented the new task template in `project/README.md`

## [0.1.3] - 2026-03-17

### Added

- added backlog tasks for the raw-data refactor, storage abstraction, Typer CLI, and refactored test coverage

### Changed

- updated the roadmap to reflect the new implementation sequence for the raw-data-only project goal

## [0.1.2] - 2026-03-17

### Changed

- clarified the project scope in the documentation as raw data acquisition from `sreality.cz`
- documented that scraper outputs should remain unprocessed and unnormalized
- recorded the open storage decision between MongoDB and filesystem-based persistence

## [0.1.1] - 2026-03-17

### Added

- added top-level project governance and contributor rules in `AGENTS.md`
- added technical documentation in `docs/` for architecture, modules, artifacts, and roadmap
- added lightweight task tracking in `project/` with backlog and done records
- added Poetry script entrypoints for scraper, town loader, and district loader
- added centralized runtime configuration in `scraperweb.config`
- added dedicated runtime modules for estate scraping, town loading, and district loading
- added root `README.md` and `.gitignore`

### Changed

- reorganized repository layout to separate source code, scripts, datasets, docs, and project tracking
- moved CSV reference datasets from `scraperweb/` to `data/`
- converted legacy script-style modules into compatibility wrappers around refactored implementations
- replaced hard-coded runtime values with environment-based configuration defaults

### Removed

- removed tracked Python bytecode artifacts from the repository
- removed generated API HTML files from the active working tree snapshot pending regeneration
