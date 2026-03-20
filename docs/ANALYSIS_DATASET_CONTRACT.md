# Analysis Dataset Contract

## Purpose

This document defines the first supported notebook-facing analysis dataset for
`scraperweb`.

The dataset exists to give the exploratory notebook and later training work one
approved tabular projection instead of rebuilding feature semantics inside
notebook cells. It is intentionally thin. The export should reshape already
approved stage contracts into one row per deduplicated listing snapshot without
recomputing enrichment or modeling logic.

## Design Decision

The first supported analysis dataset is a deterministic export workflow that
materializes a versioned tabular artifact from approved downstream contracts.

Approved repository decision:

1. the export is owned by a later workflow, not by notebook-local code
2. the tabular dataset is a new derived artifact family rather than an
   ephemeral in-memory notebook table
3. the projection starts from `ModelingInputRecord` for stable feature columns
4. the projection may also read selected `EnrichedListingRecord` fields that are
   still enrichment-owned, especially resolved coordinates and geocoding
   provenance
5. the export emits one canonical primary table with one row per deduplicated
   listing
6. the export must attach dataset lineage and contract version metadata so later
   notebook and training workflows consume the same semantics

This keeps business meaning anchored to existing stage ownership while avoiding
another wide contract inside `modeling` before the notebook work is validated.

## Scope

The first contract is designed for:

- notebook-backed descriptive analysis
- price-per-square-meter spatial analysis
- article-facing charts and tables
- future training workflows that need the same approved feature semantics

The first contract is not designed for:

- persisting full enriched JSON records in tabular form
- replacing the modeling-stage contract
- storing notebook-only experimental feature engineering

## Input Boundary

The analysis dataset must be derived only from approved downstream stage
contracts:

- `ModelingInputRecord` is the primary feature and target source
- `EnrichedListingRecord` is the approved source for fields not yet promoted
  into modeling, such as resolved latitude/longitude and geocoding provenance

The export must not read raw or normalized artifacts directly.

Required lineage remains:

`raw -> normalized -> enriched -> modeling -> analysis dataset export`

## Row Identity And Grain

The canonical row grain is:

- one deduplicated listing snapshot per `listing_id`

The first supported dataset should default to a listing-level cross section
instead of a time series.

Approved deduplication policy:

1. group candidate records by `listing_id`
2. retain the latest available snapshot by `captured_at_utc`
3. if multiple records still tie, retain the one with the latest deterministic
   modeling timestamp
4. if a tie still remains, choose the lexicographically smallest `source_url`
   so replay stays deterministic

Rationale:

- the notebook should reason about the latest observed market state
- repeated snapshots of one listing must not silently overweight one apartment
- a later longitudinal dataset can be added separately without weakening the
  first cross-sectional contract

## Data-Quality Inclusion Rules

The first export must apply explicit inclusion and exclusion rules before rows
reach the notebook.

### Mandatory inclusion requirements

- `listing_id` must be present
- `captured_at_utc` must be present
- `asking_price_czk` must be a positive integer
- `floor_area_sqm` must be a positive numeric value
- `price_per_square_meter_czk` must be derivable from the approved price and
  area semantics
- municipality, district, region, and ORP codes may be null individually, but
  the row must preserve their explicit nullability rather than filling inferred
  placeholders

### Mandatory exclusion rules

- drop rows with missing or non-positive `asking_price_czk`
- drop rows with missing or non-positive `floor_area_sqm`
- drop rows with missing or non-positive `price_per_square_meter_czk`
- drop rows where `location_precision` is `unresolved`
- drop exact duplicate snapshots that remain identical after the approved
  deduplication policy

### Notebook-level downstream filtering

Some analytical subsets should remain notebook-controlled rather than being hard
deleted from the canonical export:

- coarse geocode exclusion for map rendering
- feature-specific null handling for individual models
- local support thresholds for rendered spatial cells
- optional outlier trimming for descriptive charts

The export should therefore preserve auditable quality flags instead of
hard-coding every analytical filter into the base dataset.

## Required Columns

The first supported table must expose these columns.

### Identity And Lineage

- `analysis_dataset_version`
- `analysis_exported_at_utc`
- `listing_id`
- `source_url`
- `captured_at_utc`
- `modeled_at_utc`
- `modeling_input_version`
- `model_version`
- `source_enrichment_version`
- `source_normalization_version`

### Canonical Targets

- `asking_price_czk`
- `floor_area_sqm`
- `price_per_square_meter_czk`

### Listing And Building Features

- `disposition`
- `is_ground_floor`
- `is_upper_floor`
- `relative_floor_position`
- `is_top_floor`
- `is_new_build`
- `building_material_bucket`
- `building_condition_bucket`
- `energy_efficiency_bucket`
- `has_price_note`
- `has_energy_efficiency_rating`
- `has_city_district`
- `is_prague_listing`

### Administrative And Spatial Features

- `municipality_code`
- `district_code`
- `region_code`
- `orp_code`
- `metropolitan_area`
- `metropolitan_district`
- `spatial_grid_system`
- `spatial_grid_source_precision`
- `spatial_grid_is_approximate`
- `spatial_grid_parent_cell_id`
- `spatial_cell_id`
- `spatial_grid_fine_cell_id`

### Resolved Coordinate And Geocoding Fields

- `latitude`
- `longitude`
- `location_precision`
- `geocoding_source`
- `geocoding_confidence`
- `geocoding_fallback_level`
- `geocoding_is_fallback`

### Distance, Accessibility, And Environment Features

- `distance_to_okresni_mesto_km`
- `distance_to_orp_center_km`
- `urban_center_profile`
- `distance_to_municipality_center_km`
- `distance_to_historic_center_km`
- `distance_to_employment_center_km`
- `distance_to_primary_rail_hub_km`
- `distance_to_airport_km`
- `distance_to_prague_center_km`
- `is_district_city`
- `is_orp_center`
- `nearest_public_transport_m`
- `nearest_backbone_public_transport_m`
- `nearest_metro_m`
- `nearest_tram_m`
- `nearest_bus_m`
- `nearest_train_m`
- `has_backbone_public_transport_within_500m`
- `has_backbone_public_transport_within_1000m`
- `has_metro_within_1000m`
- `has_tram_within_500m`
- `has_train_within_1500m`
- `nearest_shop_m`
- `nearest_school_m`
- `nearest_kindergarten_m`
- `amenities_within_300m_count`
- `amenities_within_1000m_count`
- `daily_service_amenities_within_500m_count`
- `community_amenities_within_1000m_count`
- `leisure_amenities_within_1000m_count`
- `nearest_nature_m`
- `has_nature_within_1000m`

## Field Ownership

Field ownership must remain explicit so later tasks do not redefine semantics.

### Modeling-owned columns

These columns come directly from `ModelingInputRecord` and should keep the
existing modeling semantics:

- listing identity, capture time, and modeling metadata
- `asking_price_czk`
- `floor_area_sqm`
- `price_per_square_meter_czk`
- disposition, floor, building, and energy features
- administrative identifiers
- spatial grid identifiers
- distance, accessibility, and neighborhood context features

### Enrichment-owned columns

These columns remain sourced from `EnrichedListingRecord.location_features`
until a later contract task explicitly promotes them into modeling:

- `latitude`
- `longitude`
- `location_precision`
- `geocoding_source`
- `geocoding_confidence`
- `geocoding_fallback_level`
- `geocoding_is_fallback`

The analysis export may copy these fields into the table, but it must not
rename or reinterpret them.

## Target Semantics

### `asking_price_czk`

`asking_price_czk` is the full listing asking price in Czech koruna carried from
the approved enrichment and modeling contracts.

Rules:

- it represents the advertised total asking price for the listing snapshot
- it is the canonical notebook target for full-price modeling and grouped
  factor analysis
- rows with missing or non-positive values are excluded from the base dataset
- the export must not adjust the field for inflation, fees, or inferred
  negotiation margins

### `price_per_square_meter_czk`

`price_per_square_meter_czk` is the canonical asking-price density target in
Czech koruna per square meter.

Rules:

- it is derived from the approved asking price and canonical `floor_area_sqm`
  semantics already owned upstream
- it is the canonical notebook target for spatial comparison and the approved
  grid-based price surface
- rows with missing or non-positive values are excluded from the base dataset
- the export must not recompute the value from alternative area fields

## Precision And Spatial Safety Rules

The base dataset should preserve location quality explicitly rather than hiding
it behind notebook-local heuristics.

Required rules:

- keep `location_precision`, `geocoding_source`, and `geocoding_confidence`
  available on every resolved row
- retain `district` and `municipality` precision rows in the base dataset so
  non-map descriptive analysis can still use them
- do not silently promote coarse coordinates to fine-grid validity
- let the later notebook map workflow exclude coarse rows according to
  `docs/PRICE_SURFACE_WORKFLOW.md`
- expose `spatial_grid_is_approximate` and `spatial_grid_source_precision` so
  downstream consumers can audit grid eligibility decisions

## Artifact And Filesystem Decision

The approved output is a new analysis-dataset artifact family generated by a
deterministic export workflow.

Recommended first layout for `TASK-054`:

- `data/analysis/<analysis_dataset_version>/<export_run_id>/analysis_dataset.parquet`
- sibling metadata file describing input selectors, row counts, lineage
  versions, and export timestamp

Parquet is preferred as the canonical first output because it preserves schema,
types, and notebook-friendly load performance better than CSV. Optional CSV
sidecars may be added later for inspection, but they are not the canonical
contract.

## Lineage And Versioning

The analysis dataset needs repository-level versioning separate from notebook
filenames.

Required expectations:

- define an explicit `analysis_dataset_version`
- include upstream stage versions in every export metadata payload
- persist input selectors such as region scope, source directories, and replay
  timestamps
- preserve enough metadata to reproduce the same row set from persisted
  artifacts
- bump the analysis-dataset version only when table semantics change, not when a
  new export run materializes more recent snapshots

The first contract should therefore distinguish:

- schema semantics version
- export-run timestamp
- upstream artifact lineage version

## Downstream Task Implications

`TASK-054` should implement the deterministic export workflow defined here.

That workflow should:

1. build the canonical table from approved downstream records
2. emit the versioned tabular artifact and metadata sidecar
3. report row counts before and after deduplication and mandatory exclusions
4. remain thin enough that the notebook only filters or visualizes approved
   columns instead of redefining them
