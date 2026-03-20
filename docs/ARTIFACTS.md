# Artifacts

## Source-Controlled Inputs

- `data/OkresniMesta.csv`
- `data/ObceSRozsirenouPusobnosti.csv`
- `data/souradnice.csv`

These files are treated as input datasets for reference-data loading.

Planned ownership:

- normalization may read them only for offline inspection during development, not
  for emitted contract fields
- enrichment is the approved runtime boundary for deterministic joins against
  these datasets when deriving location intelligence
- modeling consumes only the approved flattened outputs of those enrichment joins

## Generated Outputs

The repository currently does not define a dedicated output directory for scraper runs.

The intended generated outputs are raw data downloaded from `sreality.cz`,
deterministic normalized artifacts derived from persisted raw snapshots, and
deterministic enriched artifacts derived from persisted normalized snapshots.

The persistence backend is configurable. Generated outputs are:

- MongoDB collection `raw_listings` containing immutable raw listing records
- filesystem snapshots under `data/raw/<region>/<listing_id>/<captured_at_utc>.json`
- optional sibling HTML snapshots under `data/raw/<region>/<listing_id>/<captured_at_utc>.html`
- normalized filesystem snapshots under
  `data/normalized/<region>/<listing_id>/<captured_at_utc>.json`
- enriched filesystem snapshots under
  `data/enriched/<region>/<listing_id>/<captured_at_utc>.json`

Field-level artifact ownership, lineage, and representative payload structure
for these three JSON families are documented in `docs/ARTIFACT_REFERENCE.md`.

The supported normalization workflow currently targets filesystem-backed raw
snapshots only. Each normalized artifact preserves stable stage identity via
`normalization_version`, `normalized_at_utc`, and `normalization_metadata`.
Recognized nearby-place and accessories values are promoted into the canonical
typed paths `location.nearby_places` and `core_attributes.accessories` instead
of remaining only inside `core_attributes.source_specific_attributes`.

The supported enrichment workflow targets filesystem-backed normalized snapshots
only. Each enriched artifact preserves deterministic lineage via
`enrichment_version`, `enrichment_metadata.enriched_at_utc`,
`enrichment_metadata.source_normalization_version`, and the embedded
`normalized_record`. Operators can replay by `region`, `listing_id`, or
`source_scrape_run_id` without going back through raw acquisition.

Approved geocoding artifact ownership:

- raw artifacts may now expand `source_payload` with an optional
  `source_coordinates` object that stores replay-safe source-backed latitude,
  longitude, explicit source provenance, and an optional raw precision hint
  recovered from the approved embedded locality payload
- newly scraped raw artifacts that emit `source_payload.source_coordinates`
  now imply the active raw contract version `raw-listing-record-v2`, while
  legacy persisted artifacts that omit the object still replay as
  `raw-listing-record-v1`
- raw artifacts must not store map-link query parameters, inferred address
  coordinates, or enrichment-owned fallback-quality metadata inside that raw
  coordinate object
- when both `source_payload.source_coordinates` and `raw_page_snapshot` are
  present, replay should treat the structured raw coordinate object as the
  canonical source and use snapshot parsing only for older artifacts that omit
  the new field
- normalized artifacts may preserve replayable geocoding inputs such as a
  canonical query string, parsed address fragments, and their source
  provenance, but they must not persist derived coordinates or fallback quality
  decisions
- normalized artifacts may also preserve source-backed detail coordinates when
  those coordinates are direct facts reshaped from persisted detail HTML rather
  than derived geocoding outputs; such fields must keep explicit provenance and
  must not silently replace enrichment-owned final coordinates
- enriched artifacts are the canonical location-geocoding boundary and now
  persist resolved coordinates together with explicit `location_precision`,
  `geocoding_source`, `geocoding_confidence`, fallback metadata, and replayable
  query-text provenance
- enriched artifacts must record whether the winning coordinate came from the
  source-backed detail locality payload or from deterministic fallback
  geocoding so downstream spatial consumers do not need undocumented precedence
  rules
- enriched artifacts also own the canonical square-grid hierarchy via
  `spatial_grid_system`, `spatial_grid_parent_cell_id`, `spatial_cell_id`, and
  `spatial_grid_fine_cell_id`, all derived from the best available geocoded
  coordinate while preserving the source precision context
- enriched artifacts also own deterministic urban-structure fields such as
  `urban_center_profile`, distances to supported city anchors, and backbone
  public-transport accessibility thresholds derived from normalized nearby
  places
- enriched artifacts also own conservative neighborhood-context fields derived
  from normalized nearby places, including grouped amenity counts for stable
  daily-service, community, and leisure subsets plus optional nature proximity
- municipality centroid coordinates must remain distinguishable from
  street-level or address-level coordinates through explicit geocoding fields,
  not through undocumented assumptions about which coordinate columns are
  populated

Representative normalization replay validation should confirm:

- stored artifacts remain path-stable and idempotent for the same raw snapshot
- `normalized_at_utc` and `normalization_metadata` preserve raw-capture lineage
- source-backed detail coordinates keep explicit `source_coordinate_*`
  provenance instead of silently replacing enrichment-owned final coordinates
- successfully mapped nearby-place keys are removed from
  `core_attributes.source_specific_attributes`
- successfully mapped `Příslušenství:` values are removed from
  `core_attributes.source_specific_attributes`
- ambiguous accessory fragments remain traceable in
  `core_attributes.accessories.unparsed_fragments`

Representative enrichment replay validation should confirm:

- stored enriched artifacts mirror the normalized snapshot layout and stay
  idempotent for the same normalized input
- `enrichment_metadata.enriched_at_utc` remains deterministic by reusing the
  persisted `normalized_at_utc` timestamp
- `normalized_record` is preserved inside the enriched artifact so later-stage
  consumers can audit the exact normalized inputs used for derivation
- location-intelligence, accessibility, building, accessory, and lifecycle
  features remain reproducible when replayed from persisted normalized artifacts
- geocoding outputs preserve both the replayable normalized input text and the
  resolved precision/confidence metadata so geocoder swaps can be
  audited without re-scraping

Approved notebook-analysis artifact direction:

- `TASK-053` defines the first canonical analysis-dataset contract as a new
  derived artifact family owned by a deterministic export workflow rather than
  by notebook-local flattening
- that dataset should be built from approved downstream contracts only, with
  stable feature columns coming from modeling inputs and resolved
  latitude/longitude plus geocoding provenance copied from enrichment while
  those fields remain enrichment-owned
- the recommended first canonical export layout for the later `TASK-054`
  implementation is `data/analysis/<analysis_dataset_version>/<export_run_id>/`
  with one primary tabular dataset file plus an explicit metadata sidecar

## Backend Tradeoffs

### Filesystem

- simple to inspect, archive, and export into later analytical pipelines
- convenient for local development and reproducible dataset snapshots
- weaker for concurrent writers and query-heavy workflows

### MongoDB

- better for continuous collection runs, indexing, and filtered retrieval
- supports historical snapshot querying without additional file scanning
- adds operational dependency on a running database service

## Generated Documentation

`docs/api/` contains generated HTML documentation from the earlier module layout. It is documentation output, not primary source code.

## Ignored Local Artifacts

The repo ignores local caches and build artifacts such as:

- `__pycache__/`
- `*.pyc`
- virtual environments and local tool caches
