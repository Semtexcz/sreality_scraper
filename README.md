# scraperweb

`scraperweb` is a Python project for collecting raw listing data from `sreality.cz`.

The primary goal is data acquisition, not downstream processing. Scraper runs should
capture the source payloads as faithfully as possible and avoid enrichment,
normalization, geocoding, or other transformations that alter the original data.

The approved target architecture extends the repository into a simple linear
in-process pipeline with explicit stage boundaries:

- `scraper`
- `normalization`
- `enrichment`
- `modeling`

Each stage boundary is defined as a typed Python model and follows a one-way
dependency flow from scraper to normalization to enrichment to modeling. The current
runtime still implements the scraper stage only.

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

The `scrape` command is intentionally scoped to raw-data acquisition and persistence.
It does not expose enrichment, geocoding, normalization, reference-data loaders, or
derived-output options.

Scrape command options:

- `--region <slug>` (repeatable): limit scraping to specific regions; when omitted, the
  CLI scrapes the global `all-czechia` listing target
- `--max-pages <int>`: optional max listing pages per selected region; when omitted,
  traversal continues until scraper stop conditions are met
- `--max-estates <int>`: max estates in one run (default `50`)
- `--storage-backend <filesystem|mongodb>`: target storage backend (default `filesystem`)
- `--output-dir <path>`: filesystem output root (default `data/raw`)
- `--mongodb-uri <uri>`: MongoDB URI for MongoDB backend
- `--mongodb-database <name>`: MongoDB database for MongoDB backend

Region traversal semantics:

- when `--max-pages` is provided, traversal stops at that page limit even if pagination
  markup suggests more pages
- traversal stops early when a listing page is empty
- traversal stops early when a listing page repeats an already observed estate URL set
- traversal stops early when a listing page contains only already-seen estate URLs, which protects runs from duplicate tail pages and pagination drift

Validation rules:

- `--mongodb-uri` and `--mongodb-database` are allowed only with
  `--storage-backend mongodb`
- `--output-dir` custom values are allowed only with
  `--storage-backend filesystem`
