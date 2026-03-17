# scraperweb

`scraperweb` is a Python project for collecting raw listing data from `sreality.cz`.

The primary goal is data acquisition, not downstream processing. Scraper runs should
capture the source payloads as faithfully as possible and avoid enrichment,
normalization, geocoding, or other transformations that alter the original data.

## Project Scope

- Fetch raw real-estate listing data from `sreality.cz`.
- Persist downloaded records in a raw, replayable form.
- Keep storage concerns explicit and replaceable.

The storage backend is still under evaluation. Current options are:

- storing raw outputs in MongoDB
- storing raw outputs on the filesystem

## Structure

- `scraperweb/`: application code
- `data/`: CSV inputs and helper datasets
- `docs/`: technical documentation and generated API docs
- `project/`: backlog and completed task history
- `AGENTS.md`: rules for AI agents and automated contributors

## Quick Start

```bash
poetry install
poetry run scraperweb --help
poetry run scraperweb scrape --help
poetry run scraperweb load-towns --help
poetry run scraperweb load-districts --help
```

## Configuration

Current runtime configuration still exposes environment variables used by the existing
implementation:

- `MONGODB_URI` (default `mongodb://localhost:27017`)
- `MONGODB_DATABASE` (default `RealEstates`)
- `GEOPY_USER_AGENT` (default `scraperweb`)

## Runtime CLI

The project now exposes a Typer-based CLI with explicit subcommands:

- `poetry run scraperweb scrape`: scrape raw listing records from `sreality.cz`
- `poetry run scraperweb load-towns`: load auxiliary town geodata
- `poetry run scraperweb load-districts`: load auxiliary district coordinates

The `scrape` command is intentionally scoped to raw-data acquisition and persistence.
It does not expose enrichment, normalization, or derived-output options.

Scrape command options:

- `--region <slug>` (repeatable): limit scraping to specific regions
- `--max-pages <int>`: max listing pages per selected region (default `1`)
- `--max-estates <int>`: max estates in one run (default `50`)
- `--storage-backend <filesystem|mongodb>`: target storage backend (default `filesystem`)
- `--output-dir <path>`: filesystem output root (default `data/raw`)
- `--mongodb-uri <uri>`: MongoDB URI for MongoDB backend
- `--mongodb-database <name>`: MongoDB database for MongoDB backend

Validation rules:

- `--mongodb-uri` and `--mongodb-database` are allowed only with
  `--storage-backend mongodb`
- `--output-dir` custom values are allowed only with
  `--storage-backend filesystem`
