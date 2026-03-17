# Artifacts

## Source-Controlled Inputs

- `data/OkresniMesta.csv`
- `data/ObceSRozsirenouPusobnosti.csv`
- `data/souradnice.csv`

These files are treated as input datasets for reference-data loading.

## Generated Outputs

The repository currently does not define a dedicated output directory for scraper runs.

The intended generated output is raw data downloaded from `sreality.cz` without
post-processing.

The persistence backend is configurable. Generated outputs are:

- MongoDB collection `raw_listings` containing immutable raw listing records
- filesystem snapshots under `data/raw/<region>/<listing_id>/<captured_at_utc>.json`
- optional sibling HTML snapshots under `data/raw/<region>/<listing_id>/<captured_at_utc>.html`

Derived or normalized payloads are not a target artifact for this project scope.

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
