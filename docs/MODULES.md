# Modules

## Target Module Boundaries

The refactor target is a layered module layout with inward dependency flow:

- `scraperweb.cli.*`: argument parsing and runtime option validation
- `scraperweb.application.*`: orchestration services and use cases
- `scraperweb.scraping.*`: HTTP clients and HTML parsers
- `scraperweb.persistence.*`: raw record repository interfaces and adapters
- `scraperweb.domain.*`: raw record and runtime option contracts

This structure is a target architecture and is implemented incrementally in follow-up
tasks.

## Package Modules

### `scraperweb.config`

Centralized runtime settings and path helpers.

### `scraperweb.estate_scraper`

Primary scraping workflow for downloading raw estate listings from `sreality.cz` and
persisting them without transformation.

Status: transitional module pending replacement by layered services.

### `scraperweb.towns`

Loader for regional towns, district towns, and towns with extended competence.

### `scraperweb.districts_loader`

Loader for postcode and district reference data from `data/souradnice.csv`.

### Compatibility wrappers

These modules exist to preserve the old import surface while delegating to the refactored implementation:

- `scraperweb.main`
- `scraperweb.cities_data`
- `scraperweb.districts`

Status: transitional modules, scheduled for removal once the new CLI and service
boundaries are fully adopted.

## Script Entry Points

- `scripts/scrape_estates.py`
- `scripts/load_towns.py`
- `scripts/load_districts.py`

Poetry also exposes:

- `scraperweb`
- `scraperweb-load-towns`
- `scraperweb-load-districts`
