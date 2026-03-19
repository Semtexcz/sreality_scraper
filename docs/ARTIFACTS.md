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

- normalized artifacts may preserve replayable geocoding inputs such as a
  canonical query string, parsed address fragments, and their source
  provenance, but they must not persist derived coordinates or fallback quality
  decisions
- enriched artifacts are the canonical location-geocoding boundary and now
  persist resolved coordinates together with explicit `location_precision`,
  `geocoding_source`, `geocoding_confidence`, fallback metadata, and replayable
  query-text provenance
- enriched artifacts also own the canonical square-grid hierarchy via
  `spatial_grid_system`, `spatial_grid_parent_cell_id`, `spatial_cell_id`, and
  `spatial_grid_fine_cell_id`, all derived from the best available geocoded
  coordinate while preserving the source precision context
- enriched artifacts also own deterministic urban-structure fields such as
  `urban_center_profile`, distances to supported city anchors, and backbone
  public-transport accessibility thresholds derived from normalized nearby
  places
- municipality centroid coordinates must remain distinguishable from
  street-level or address-level coordinates through explicit geocoding fields,
  not through undocumented assumptions about which coordinate columns are
  populated

Representative normalization replay validation should confirm:

- stored artifacts remain path-stable and idempotent for the same raw snapshot
- `normalized_at_utc` and `normalization_metadata` preserve raw-capture lineage
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
