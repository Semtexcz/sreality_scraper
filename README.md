# scraperweb

`scraperweb` is a Python project for collecting raw listing data from `sreality.cz`.

The primary goal is data acquisition, not downstream processing. Scraper runs should
capture the source payloads as faithfully as possible and avoid enrichment,
geocoding, or other transformations that alter the original data in-place.

The approved target architecture extends the repository into a simple linear
in-process pipeline with explicit stage boundaries:

- `scraper`
- `normalization`
- `enrichment`
- `modeling`

Each stage boundary is defined as a typed Python model and follows a one-way
dependency flow from scraper to normalization to enrichment to modeling. The current
runtime exposes raw acquisition and a filesystem-backed normalization workflow.

## Project Scope

- Fetch raw real-estate listing data from `sreality.cz`.
- Persist downloaded records in a raw, replayable form.
- Keep storage concerns explicit and replaceable.

The storage backend is still under evaluation. Current options are:

- storing raw outputs in MongoDB
- storing raw outputs on the filesystem

## Structure

- `scraperweb/`: application code
- `data/`: raw output directory and bundled source datasets
- `docs/`: technical documentation and generated API docs
- `project/`: backlog and completed task history
- `AGENTS.md`: rules for AI agents and automated contributors

The `scraperweb/` package now exposes explicit stage boundaries:

- `scraperweb.scraper`: canonical raw contracts, HTTP clients, and HTML parsers
- `scraperweb.normalization`: normalization-stage contracts
- `scraperweb.enrichment`: enrichment-stage contracts
- `scraperweb.modeling`: modeling-stage contracts

## Quick Start

```bash
poetry install
poetry run scraperweb --help
poetry run scraperweb scrape --help
```

## Testing

Unit tests and live integration tests are separated:

- `tests/unit/`: deterministic unit and fixture-based tests
- `tests/integration/`: opt-in live tests that call the real `sreality.cz` service

Default test execution keeps the suite stable:

```bash
poetry run pytest
```

Run the live integration suite explicitly when network access is available:

```bash
RUN_LIVE_INTEGRATION_TESTS=1 poetry run pytest tests/integration
```

## Configuration

Runtime configuration only exposes values required for raw persistence:

- `MONGODB_URI` (default `mongodb://localhost:27017`)
- `MONGODB_DATABASE` (default `RawListings`)

## Runtime CLI

The project now exposes a Typer-based CLI with explicit subcommands:

- `poetry run scraperweb scrape`: scrape raw listing records from `sreality.cz`
- `poetry run scraperweb normalize`: normalize persisted raw filesystem snapshots

The `scrape` command stays scoped to raw-data acquisition and persistence. It does
not expose enrichment, geocoding, reference-data loaders, or derived-output options.

The internal normalization contract distinguishes direct raw payload facts from
documented title-fallback values. For example, `Lokalita:` now maps into a typed
location descriptor field, while municipality and district values derived from the
presentation title are marked explicitly as fallback provenance.

Scrape command options:

- `--region <slug>` (repeatable): limit scraping to specific regions; when omitted, the
  CLI scrapes the global `all-czechia` listing target
- `--max-pages <int>`: optional max listing pages per selected region; when omitted,
  traversal continues until scraper stop conditions are met
- `--max-estates <int>`: optional max estates in one run; when omitted, scraping
  continues until pagination is exhausted or another explicit stop condition is met
- `--resume-existing`: skip detail-page downloads for listings that already have at
  least one persisted raw snapshot in the selected backend and region
- `--storage-backend <filesystem|mongodb>`: target storage backend (default `filesystem`)
- `--output-dir <path>`: filesystem output root (default `data/raw`)
- `--mongodb-uri <uri>`: MongoDB URI for MongoDB backend
- `--mongodb-database <name>`: MongoDB database for MongoDB backend

Region traversal semantics:

- when `--max-pages` is provided, traversal stops at that page limit even if pagination
  markup suggests more pages
- when `--max-estates` is omitted, the runtime reports the estate bound as
  `unbounded` so operators can distinguish a full crawl from a sampled run
- when `--resume-existing` is enabled, the scraper treats `(region, listing_id)` as
  the canonical identity for an existing raw record and skips detail downloads for
  listings that already exist in the selected backend
- resume-mode existence checks ignore `*.markup-failure.json` artifacts because they
  do not represent a successfully persisted raw listing record
- traversal stops early when a listing page is empty
- traversal stops early when a listing page repeats an already observed estate URL set
- traversal stops early when a listing page contains only already-seen estate URLs, which protects runs from duplicate tail pages and pagination drift
- unbounded `all-czechia` traversal now tolerates short duplicate windows with
  no new estate URLs so temporary pagination drift does not stop the run after
  a single stale page
- unbounded `all-czechia` traversal still stops deterministically on a repeated
  duplicate-tail page or after three consecutive stale pages without any newly
  discovered estate URLs
- every traversal stop now emits a page-level diagnostic with the stop reason,
  observed estate count, new estate count, stale-page streak, and repeated-page
  origin when applicable
- resume-mode progress reports skipped-existing listings without counting them as
  processed estates, and region summaries include both processed and skipped counts

Validation rules:

- `--mongodb-uri` and `--mongodb-database` are allowed only with
  `--storage-backend mongodb`
- `--output-dir` custom values are allowed only with
  `--storage-backend filesystem`

Normalize command options:

- exactly one selector is required:
  `--region <slug>`, `--listing-id <id>`, or `--scrape-run-id <uuid>`
- `--input-dir <path>`: filesystem raw snapshot root (default `data/raw`)
- `--output-dir <path>`: filesystem normalized output root (default
  `data/normalized`)

Normalization workflow semantics:

- input currently supports persisted filesystem raw snapshots only
- region scope reads every `*.json` raw record under `data/raw/<region>/`
- listing scope reads every `*.json` raw record under `data/raw/<region>/<listing_id>/`
- scrape-run scope scans filesystem raw snapshots and selects records whose
  `source_metadata.scrape_run_id` matches the requested run id
- markup-failure artifacts are ignored and are never normalized
- normalized outputs mirror raw snapshot identity at
  `data/normalized/<region>/<listing_id>/<captured_at_utc>.json`
- each normalized JSON artifact preserves `normalization_version`,
  `normalized_at_utc`, and full `normalization_metadata` traceability fields so
  operators can inspect stage handoffs or reuse the outputs downstream without
  rerunning scraping
- supported nearby-place source keys now replay into `location.nearby_places`
  instead of remaining only in `core_attributes.source_specific_attributes`
- supported `Příslušenství:` fragments now replay into
  `core_attributes.accessories`, while unsupported or ambiguous fragments remain
  traceable in `core_attributes.accessories.unparsed_fragments`

Replay and validation notes:

- representative replay coverage should include persisted snapshots with
  populated `location.nearby_places` and `core_attributes.accessories`
- validation should confirm both typed fields and traceability guarantees in the
  serialized JSON artifacts, including the absence of successfully mapped source
  keys from `core_attributes.source_specific_attributes`
- downstream enrichment and modeling stages currently preserve these typed
  normalization outputs for traceability; enrichment derives nearby-place
  accessibility metrics from them and modeling now consumes the approved stable
  flattened location feature subset from enrichment
- upcoming location-intelligence work is intentionally scoped to enrichment
  rather than normalization, so municipality codes, ORP mappings, coordinates,
  and spatial buckets remain derived features with explicit match provenance
